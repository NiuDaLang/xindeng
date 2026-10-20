# conftest.py
"""
Project-level conftest.

Two responsibilities, both project-wide:

  * `_redirect_media_root` — autouse fixture that redirects
    `settings.MEDIA_ROOT` to a fresh per-test tmp directory. Every test
    in every app is protected: nothing writes into the real `media/`
    tree.

  * Image-byte factories — `png_small`, `png_medium`, `png_oversize`,
    `jpeg_exif_rotated`, `gif_animated`, `tiny_corrupt`. These are
    consumed by core's image pipeline tests and by the vault tests in
    store/. They live here (rather than in tests/) because pytest's
    conftest discovery walks the *ancestor* chain from each test file,
    so a fixture in a sibling package is invisible to tests in a
    different package. The root conftest is the only location every
    test inherits.
"""

from __future__ import annotations

import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


# ──────────────────────────────────────────────────────────────
# Media-root redirection (autouse, project-wide)
# ──────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _redirect_media_root(tmp_path, settings):
    """Point MEDIA_ROOT at a fresh per-test directory."""
    media = tmp_path / "media"
    media.mkdir(parents=True, exist_ok=True)
    settings.MEDIA_ROOT = str(media)


# ──────────────────────────────────────────────────────────────
# Image byte factories
# ──────────────────────────────────────────────────────────────

def _png_bytes(width: int, height: int, color=(255, 0, 0, 255)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", (width, height), color).save(buf, format="PNG")
    return buf.getvalue()


def _jpeg_bytes(width: int, height: int, exif_orientation: int | None = None) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), (10, 200, 10))
    kwargs = {}
    if exif_orientation is not None:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        kwargs["exif"] = exif
    img.save(buf, format="JPEG", quality=95, **kwargs)
    return buf.getvalue()


def _animated_gif_bytes(frames: int = 3, size=(32, 32)) -> bytes:
    buf = io.BytesIO()
    imgs = [
        Image.new("P", size, color=i * 40 % 256)
        for i in range(frames)
    ]
    imgs[0].save(
        buf, format="GIF", save_all=True, append_images=imgs[1:],
        duration=100, loop=0,
    )
    return buf.getvalue()


@pytest.fixture
def png_small() -> SimpleUploadedFile:
    """A 100x100 PNG. Below MIN_PROCESS_BYTES."""
    data = _png_bytes(100, 100)
    return SimpleUploadedFile("small.png", data, content_type="image/png")


@pytest.fixture
def png_medium() -> SimpleUploadedFile:
    """A 800x600 noisy PNG — comfortably above MIN_PROCESS_BYTES."""
    import random
    random.seed(0)
    img = Image.new("RGB", (800, 600))
    px = img.load()
    for y in range(600):
        for x in range(800):
            px[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return SimpleUploadedFile("medium.png", buf.getvalue(), content_type="image/png")


@pytest.fixture
def png_oversize() -> SimpleUploadedFile:
    """
    A 3000x2000 NOISY PNG (noise generated at 1500x1000, upscaled).

    Rationale for noise: a solid-colour 3000x2000 PNG is a few KB on
    disk, and WebP Q82 of the same solid colour is LARGER, so
    optimize_image's 'encoded >= original' guard rejects it and returns
    None. Noisy content inverts that — WebP is smaller than the PNG —
    so the test actually reaches the max_dimension clamp.
    """
    import random
    random.seed(1)
    small = Image.new("RGB", (1500, 1000))
    px = small.load()
    for y in range(1000):
        for x in range(1500):
            v = random.randint(0, 255)
            px[x, y] = (v, (v * 7) % 256, (v * 13) % 256)
    img = small.resize((3000, 2000), Image.NEAREST)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return SimpleUploadedFile("huge.png", buf.getvalue(), content_type="image/png")


@pytest.fixture
def jpeg_exif_rotated() -> SimpleUploadedFile:
    """A 200x100 JPEG with EXIF Orientation=6 (rotate 90° CW).
    After exif_transpose it should be 100x200."""
    data = _jpeg_bytes(200, 100, exif_orientation=6)
    return SimpleUploadedFile("rotated.jpg", data, content_type="image/jpeg")


@pytest.fixture
def gif_animated() -> SimpleUploadedFile:
    data = _animated_gif_bytes()
    return SimpleUploadedFile("anim.gif", data, content_type="image/gif")


@pytest.fixture
def tiny_corrupt() -> SimpleUploadedFile:
    """Not a valid image — for negative paths."""
    return SimpleUploadedFile(
        "broken.png", b"\x89PNG\r\n\x1a\nnot-really", content_type="image/png"
    )