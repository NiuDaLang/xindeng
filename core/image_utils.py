# core/image_utils.py
"""
Image optimisation utilities.

Pure Pillow-based processing — no external image libraries required.

Public API:
    is_skippable(field_file)              -> bool
    is_already_optimized(field_file)      -> bool
    optimize_image(field_file, **opts)    -> (ContentFile, new_name) | None
    save_optimized_to_field(instance, field_name, content, new_full_name)
    robust_exists(path)                   -> bool
    sanitize_filename(name)               -> str

The returned tuple from optimize_image is (optimized_file_content, new_full_name).
`new_full_name` is the *full storage path* (including the field's upload_to prefix).

If None is returned, the caller should leave the field untouched.
"""

from __future__ import annotations

import io
import logging
import os
import re
import unicodedata
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Tunables (override per-field via the signal registry)
# ──────────────────────────────────────────────────────────────

DEFAULT_MAX_DIMENSION = 1600
DEFAULT_QUALITY       = 82
DEFAULT_FORMAT        = "WEBP"

# Files smaller than this are processed inline (fast enough);
# larger files are pushed to Celery.
INLINE_SIZE_THRESHOLD_BYTES = 1 * 1024 * 1024  # 1 MB

# If an image is already under this size AND already WebP, skip entirely.
ALREADY_OPTIMIZED_BYTES = 300 * 1024  # 300 KB

# Anything smaller than this is left alone — no point re-compressing.
MIN_PROCESS_BYTES = 80 * 1024  # 80 KB

# Filenames we must never touch (shared defaults, placeholders).
SKIP_FILENAMES = {
    "pattern1.png",
    "default.png",
    "placeholder.png",
    "placeholder.jpg",
}

# Top-level media folders treated as static-like content, never processed.
SKIP_PATH_PREFIXES = (
    "three/",
    "favicon/",
    "ckeditor5_storage/",
)

# Extensions we never process.
SKIP_EXTENSIONS = (
    ".svg", ".ico", ".webmanifest",
    ".mp4", ".webm", ".mov", ".avi", ".mkv",
)


# ──────────────────────────────────────────────────────────────
# Public helpers
# ──────────────────────────────────────────────────────────────

def _normalize_name(name: str) -> str:
    """NFC-normalize and forward-slash-normalize a storage name."""
    if not name:
        return ""
    return unicodedata.normalize("NFC", name).replace("\\", "/").lstrip("/")


def is_skippable(field_file) -> bool:
    """
    Return True if this file must not be processed:
      - empty / None
      - lives inside a static-like media folder
      - has a non-processable extension
      - filename is in the shared-defaults allowlist
    """
    if not field_file or not getattr(field_file, "name", ""):
        return True

    name = _normalize_name(field_file.name)
    name_lower = name.lower()

    # Folder-based fast path
    if any(name_lower.startswith(p) for p in SKIP_PATH_PREFIXES):
        return True

    # Extension-based fast path
    if any(name_lower.endswith(ext) for ext in SKIP_EXTENSIONS):
        return True

    # Shared default filenames
    basename = os.path.basename(name_lower)
    if basename in SKIP_FILENAMES:
        return True

    return False


def is_already_optimized(field_file) -> bool:
    """
    Return True if the file is already WebP and small enough that
    re-processing would not meaningfully help.
    """
    if is_skippable(field_file):
        return False

    name = _normalize_name(field_file.name).lower()
    if not name.endswith(".webp"):
        return False

    try:
        if field_file.size <= ALREADY_OPTIMIZED_BYTES:
            return True
    except (OSError, ValueError):
        return False

    return False


def optimize_image(
    field_file,
    *,
    max_dimension: int = DEFAULT_MAX_DIMENSION,
    quality: int = DEFAULT_QUALITY,
    output_format: str = DEFAULT_FORMAT,
    force: bool = False,
):
    """
    Return (ContentFile, new_full_name) or None.

    `new_full_name` is the intended *full* storage path, i.e. it preserves
    the original directory prefix and just swaps the extension.

    Returns None if the input is skippable, unreadable, already fine,
    or would grow when re-encoded.
    """
    if is_skippable(field_file):
        return None

    if not force and is_already_optimized(field_file):
        return None

    try:
        size_bytes = field_file.size
    except (OSError, ValueError):
        size_bytes = None

    if not force and size_bytes is not None and size_bytes < MIN_PROCESS_BYTES:
        return None

    # Open the source
    try:
        field_file.open("rb")
        img = Image.open(field_file)
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        logger.warning("image_utils: unable to open %s: %s", field_file.name, exc)
        return None
    finally:
        try:
            field_file.close()
        except Exception:
            pass

    original_format = (img.format or "").upper()

    # Skip animated GIFs — Pillow's resize would destroy the animation.
    if original_format == "GIF" and getattr(img, "is_animated", False):
        logger.info("image_utils: skipping animated GIF %s", field_file.name)
        return None

    # Respect EXIF orientation before resizing.
    img = ImageOps.exif_transpose(img) or img

    # Resize
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    # Normalise mode for the target format
    target = output_format.upper()

    if target == "WEBP":
        if img.mode in ("P", "CMYK", "LA", "1", "I", "F"):
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        elif img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
    elif target == "JPEG":
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            rgba = img.convert("RGBA")
            background.paste(rgba, mask=rgba.split()[-1])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

    # Encode
    buffer = io.BytesIO()
    save_kwargs = {"optimize": True}

    if target == "WEBP":
        save_kwargs.update({"quality": quality, "method": 6})
    elif target == "JPEG":
        save_kwargs.update({"quality": quality, "progressive": True})
    elif target == "PNG":
        save_kwargs.update({"compress_level": 9})

    try:
        img.save(buffer, format=target, **save_kwargs)
    except OSError as exc:
        logger.warning(
            "image_utils: failed to encode %s as %s: %s",
            field_file.name, target, exc,
        )
        return None

    encoded = buffer.getvalue()

    # If we made it bigger, keep the original.
    if size_bytes is not None and len(encoded) >= size_bytes and not force:
        logger.debug(
            "image_utils: skipping %s — optimised size %d >= original %d",
            field_file.name, len(encoded), size_bytes,
        )
        return None

    new_full_name = _swap_extension(field_file.name, target.lower())
    return ContentFile(encoded), new_full_name


def save_optimized_to_field(instance, field_name, content, new_full_name):
    """
    Persist optimized content back to `instance.<field_name>` correctly.

    Uses temp-then-replace semantics for same-path updates so the file
    is never in a missing state, even if the process is killed mid-write.
    Deletes the original file when the path changes (e.g. .jpg -> .webp).
    """
    import os

    field_file = getattr(instance, field_name)
    storage = field_file.storage
    old_name = field_file.name

    # ── Case 1: same path (in-place replacement) ──
    if old_name == new_full_name:
        try:
            # Write to a temp path first, then atomically replace.
            tmp_name = new_full_name + ".tmp_optimize"
            saved_tmp = storage.save(tmp_name, content)
            tmp_path = storage.path(saved_tmp)
            final_path = storage.path(new_full_name)
            os.replace(tmp_path, final_path)  # atomic on same filesystem
        except Exception as exc:
            logger.exception(
                "image_utils: in-place replace failed for %s: %s",
                new_full_name, exc,
            )
            # Best-effort cleanup of temp
            try:
                storage.delete(tmp_name)
            except Exception:
                pass
            return
        # field_file.name unchanged
    # ── Case 2: path changed (extension swap) ──
    else:
        try:
            saved_name = storage.save(new_full_name, content)
        except Exception as exc:
            logger.exception(
                "image_utils: storage.save failed for %s: %s", new_full_name, exc,
            )
            return

        # Handle potential collision suffix.
        if saved_name != new_full_name:
            try:
                storage.delete(saved_name)
                storage.delete(new_full_name)
                saved_name = storage.save(new_full_name, content)
            except Exception:
                pass

        field_file.name = saved_name

        # Delete the original file.
        if old_name:
            try:
                storage.delete(old_name)
            except Exception as exc:
                logger.warning(
                    "image_utils: could not delete original %s: %s", old_name, exc,
                )

    # ── NEW: prevent the file_cleanup signal from re-deleting ──
    # The file_cleanup module hooks post_save to delete replaced files.
    # We've already handled the old-file deletion above, so clear the
    # tracker to avoid a redundant (but harmless) second attempt.
    instance._cleanup_old_file = None

    # Invalidate the dimension cache for both old and new names.
    from .image_utils import invalidate_image_dimensions_cache
    invalidate_image_dimensions_cache(old_name)
    invalidate_image_dimensions_cache(field_file.name)

    # Persist with re-entry guard.
    setattr(instance, "_skip_image_optimization", True)
    try:
        instance.save(update_fields=[field_name])
    finally:
        try:
            delattr(instance, "_skip_image_optimization")
        except AttributeError:
            pass


def robust_exists(path) -> bool:
    """
    Return True if `path` exists on disk, trying NFC and NFD normalizations.

    Handles macOS <-> Linux normalization mismatches for CJK / accented names.
    """
    try:
        p = Path(path)
    except (TypeError, ValueError):
        return False

    if p.exists():
        return True

    nfc = unicodedata.normalize("NFC", str(p))
    nfd = unicodedata.normalize("NFD", str(p))
    return Path(nfc).exists() or Path(nfd).exists()


# ──────────────────────────────────────────────────────────────
# Filename sanitisation (for the storage subclass)
# ──────────────────────────────────────────────────────────────

# Characters illegal on Windows filesystems — also problematic in URLs.
_WINDOWS_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')

# Windows reserved device names (case-insensitive, without extension).
_WINDOWS_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
})

# Collapse runs of whitespace.
_WHITESPACE_RUN = re.compile(r"\s+")


def sanitize_filename(name: str) -> str:
    """
    Normalize a filename to be safe across macOS, Linux, and Windows.

    - NFC normalize (compose combining marks)
    - Strip Windows-illegal characters and ASCII control codes
    - Collapse whitespace runs to single spaces
    - Strip leading/trailing dots and spaces
    - Prefix reserved device names with '_'
    - Preserve the file extension

    Returns a sanitized name; may return an empty string if the input
    is entirely illegal (caller should then fall back to a default).

    the three B1/B2/B3 behaviours we decided to keep:
    - \ is treated as a path separator before illegal-char stripping
    - \t/\n vanish (control-char strip runs before whitespace collapse)
    - .gitignore → gitignore (leading dot lost)

    """
    if not name:
        return ""

    # Split off the extension first so sanitisation doesn't strip the dot.
    name = _normalize_name(name)
    dirname, sep, basename = name.rpartition("/")

    # Peel the extension: only treat the *last* dot as the extension separator.
    stem, dot, ext = basename.rpartition(".")
    if not dot or not stem:
        stem, ext = basename, ""
    else:
        # Guard against ".gitignore"-style names where there's no stem.
        if not stem:
            stem, ext = basename, ""

    # Sanitize the stem.
    stem = _WINDOWS_ILLEGAL_CHARS.sub("", stem)
    stem = _WHITESPACE_RUN.sub(" ", stem)
    stem = stem.strip(" .")

    # Sanitize the extension.
    ext = _WINDOWS_ILLEGAL_CHARS.sub("", ext).strip(" .")

    if not stem:
        stem = "file"

    # Reserved device name check.
    if stem.upper() in _WINDOWS_RESERVED_NAMES:
        stem = f"_{stem}"

    sanitized = f"{stem}.{ext}" if ext else stem

    if dirname:
        return f"{dirname}{sep}{sanitized}"
    return sanitized


# ──────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────

def _swap_extension(original_name: str, new_ext: str) -> str:
    """
    'images/products/gallery/foo.JPG' -> 'images/products/gallery/foo.webp'
    Preserves the full directory path. NFC-normalizes the result.
    """
    p = Path(_normalize_name(original_name))
    return unicodedata.normalize(
        "NFC", str(p.with_suffix(f".{new_ext.lstrip('.')}"))
    )


# ──────────────────────────────────────────────────────────────
# Image dimension lookups (for portrait/landscape detection)
# ──────────────────────────────────────────────────────────────

def get_image_dimensions(storage_name: str) -> tuple[int, int] | None:
    """
    Return (width, height) for a storage name, or None if unavailable.

    Reads the image with Pillow but does NOT keep it in memory long —
    the file is closed as soon as dimensions are extracted.

    Uses Django's cache framework if configured. Falls back to a disk
    read on cache miss. Cache key: 'imgdims:<storage_name>'.
    Cache TTL: 24 hours (invalidated explicitly on file changes).
    """
    if not storage_name:
        return None

    # ── Try cache first ──
    cache_key = f"imgdims:{storage_name}"
    try:
        from django.core.cache import cache
        cached = cache.get(cache_key)
        if cached is not None:
            # Tuples serialize fine; ensure it's a tuple of ints.
            return (int(cached[0]), int(cached[1]))
    except Exception:
        # Cache backend unavailable — proceed to disk read.
        pass

    # ── Read from disk ──
    try:
        from django.core.files.storage import default_storage
        path = default_storage.path(storage_name)
    except (NotImplementedError, ValueError, OSError):
        return None

    # Handle NFC/NFD variations (macOS ↔ Linux interop) — mirrors robust_exists.
    import unicodedata
    candidates = [
        path,
        unicodedata.normalize("NFC", path),
        unicodedata.normalize("NFD", path),
    ]

    dims = None
    for candidate in candidates:
        try:
            with Image.open(candidate) as img:
                dims = img.size  # (width, height)
            break
        except (FileNotFoundError, UnidentifiedImageError, OSError):
            continue
        except Exception as exc:
            logger.debug(
                "image_utils: dimension lookup failed for %s: %s",
                candidate, exc,
            )
            continue

    if dims is None:
        return None

    # ── Populate cache ──
    try:
        from django.core.cache import cache
        cache.set(cache_key, dims, timeout=60 * 60 * 24)  # 24 hours
    except Exception:
        pass

    return dims


def invalidate_image_dimensions_cache(storage_name: str) -> None:
    """
    Remove the cached dimensions for a storage name. Called by the
    file_cleanup module after a file swap or delete.
    """
    if not storage_name:
        return
    try:
        from django.core.cache import cache
        cache.delete(f"imgdims:{storage_name}")
    except Exception:
        pass