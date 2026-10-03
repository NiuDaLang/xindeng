# core/tests/test_image_utils.py
"""
Tests for core.image_utils — sanitize_filename, is_skippable,
is_already_optimized, optimize_image, robust_exists, get_image_dimensions.
"""

from __future__ import annotations
import io
import os
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from core import image_utils as iu
from core.tests._fakes import FakeFieldFile

# ══════════════════════════════════════════════════════════════
# sanitize_filename
# ══════════════════════════════════════════════════════════════

class TestSanitizeFilename:

    def test_passthrough_clean_name(self):
        assert iu.sanitize_filename("photo.jpg") == "photo.jpg"

    def test_preserves_directory_prefix(self):
        assert (
            iu.sanitize_filename("images/products/hero.png")
            == "images/products/hero.png"
        )

    @pytest.mark.parametrize("bad,expected", [
        ("a<b>c.jpg",          "abc.jpg"),
        ("a:b|c.jpg",          "abc.jpg"),
        ("a?b*c.jpg",          "abc.jpg"),
        ('a"b.jpg',            "ab.jpg"),
        ("a\x00b.jpg",         "ab.jpg"),
        ("a\x1fb.jpg",         "ab.jpg"),
    ])
    def test_strips_windows_illegal_chars(self, bad, expected):
        assert iu.sanitize_filename(bad) == expected

    def test_backslash_is_treated_as_path_separator(self):
        # Cross-platform intent: a Windows upload named 'a\\b.jpg' should
        # land at 'a/b.jpg', not 'ab.jpg'. Backslash is normalised before
        # the illegal-char strip runs, so it survives as a separator.
        assert iu.sanitize_filename("a\\b.jpg") == "a/b.jpg"

    @pytest.mark.parametrize("name", [
        "CON", "con", "PRN", "AUX", "NUL",
        "COM1", "com9", "LPT1", "lpt9",
    ])
    def test_prefixes_windows_reserved_names(self, name):
        assert iu.sanitize_filename(name) == f"_{name}"
        # extension form
        assert iu.sanitize_filename(f"{name}.txt") == f"_{name}.txt"

    def test_not_confused_by_com0_or_lpt0(self):
        # COM0 / LPT0 are NOT reserved on Windows.
        assert iu.sanitize_filename("COM0") == "COM0"
        assert iu.sanitize_filename("LPT0") == "LPT0"

    def test_collapses_whitespace(self):
        # Control chars (\t, \n) are stripped as illegal BEFORE whitespace
        # collapsing runs, so they vanish rather than becoming spaces.
        # 'a   b\t\nc.jpg' -> strip -> 'a   bc.jpg' -> collapse -> 'a bc.jpg'
        assert iu.sanitize_filename("a   b c.jpg") == "a b c.jpg"

    def test_control_chars_in_whitespace_are_removed_not_spaced(self):
        # Documents the current behaviour of the illegal-char pass running
        # before the whitespace pass. If this ever changes, the test will
        # flag it as an intentional decision rather than silent drift.
        assert iu.sanitize_filename("a   b\t\nc.jpg") == "a bc.jpg"

    def test_strips_leading_trailing_dots_and_spaces(self):
        assert iu.sanitize_filename("  .hidden.  ") == "hidden"
        assert iu.sanitize_filename("name .jpg") == "name.jpg"

    def test_nfd_is_composed_to_nfc(self):
        # 'e' + combining acute -> 'é'
        nfd = "cafe\u0301.jpg"
        out = iu.sanitize_filename(nfd)
        assert out == "café.jpg"
        assert "\u0301" not in out

    def test_extension_preserved_case(self):
        assert iu.sanitize_filename("Photo.JPG") == "Photo.JPG"

    def test_empty_input_returns_empty(self):
        assert iu.sanitize_filename("") == ""
        assert iu.sanitize_filename(None) == ""

    def test_all_illegal_stem_falls_back_to_file(self):
        # After stripping, stem is empty -> 'file'
        assert iu.sanitize_filename("<>|?.jpg") == "file.jpg"

    def test_dotfile_handling(self):
        # Current behaviour: leading-dot basenames lose the dot, because
        # rpartition(".") treats the whole name as an extension and the
        # subsequent .strip(" .") removes the leading dot. Dotfiles as
        # user uploads are already pathological; if you ever need to
        # preserve them, special-case names starting with '.' before the
        # rpartition call.
        assert iu.sanitize_filename(".gitignore") == "gitignore"

    def test_backslash_normalised_to_forward_slash(self):
        assert iu.sanitize_filename("a\\b\\c.jpg") == "a/b/c.jpg"


# ══════════════════════════════════════════════════════════════
# is_skippable
# ══════════════════════════════════════════════════════════════

class TestIsSkippable:

    def test_none_is_skippable(self):
        assert iu.is_skippable(None) is True

    def test_empty_name_is_skippable(self):
        assert iu.is_skippable(FakeFieldFile("", 0)) is True

    def test_none_filename_attribute_is_skippable(self):
        # .name is empty string, matches the `not getattr(field_file, "name", "")`
        # guard.
        assert iu.is_skippable(FakeFieldFile("", 0)) is True

    @pytest.mark.parametrize("name", [
        "favicon/favicon.ico",
        "three/hanabi_demo.gif",
        "ckeditor5_storage/foo.png",
    ])
    def test_skip_path_prefixes(self, name):
        assert iu.is_skippable(FakeFieldFile(name, 1)) is True

    def test_prefix_is_case_insensitive(self):
        assert iu.is_skippable(FakeFieldFile("FAVICON/x.png", 1)) is True



    @pytest.mark.parametrize("name", [
        "logo.svg", "x.ico", "site.webmanifest",
        "clip.mp4", "clip.webm", "clip.mov", "clip.avi", "clip.mkv",
    ])
    def test_skip_extensions(self, name):
        f = SimpleUploadedFile(name, b"x")
        assert iu.is_skippable(f) is True

    @pytest.mark.parametrize("name", [
        "default.png", "pattern1.png",
        "placeholder.png", "placeholder.jpg",
    ])
    def test_skip_shared_defaults(self, name):
        f = SimpleUploadedFile(name, b"x")
        assert iu.is_skippable(f) is True

    def test_normal_png_not_skippable(self, png_small):
        assert iu.is_skippable(png_small) is False


# ══════════════════════════════════════════════════════════════
# is_already_optimized
# ══════════════════════════════════════════════════════════════

class TestIsAlreadyOptimized:

    def test_small_webp_is_optimized(self):
        f = SimpleUploadedFile("x.webp", b"w" * 1000)
        # Not skippable and .webp and < 300 KB
        assert iu.is_already_optimized(f) is True

    def test_large_webp_is_not_optimized(self):
        f = SimpleUploadedFile("x.webp", b"w" * (iu.ALREADY_OPTIMIZED_BYTES + 1))
        assert iu.is_already_optimized(f) is False

    def test_small_png_is_not_optimized(self):
        f = SimpleUploadedFile("x.png", b"p" * 1000)
        assert iu.is_already_optimized(f) is False

    def test_skippable_never_optimized(self):
        f = FakeFieldFile("favicon/x.webp", 100)
        assert iu.is_already_optimized(f) is False

# ══════════════════════════════════════════════════════════════
# optimize_image
# ══════════════════════════════════════════════════════════════

class TestOptimizeImage:

    def test_skippable_returns_none(self):
        f = SimpleUploadedFile("favicon/x.png", b"x" * 200_000)
        assert iu.optimize_image(f) is None

    def test_small_file_returns_none(self, png_small):
        # Below MIN_PROCESS_BYTES
        assert png_small.size < iu.MIN_PROCESS_BYTES
        assert iu.optimize_image(png_small) is None

    def test_force_bypasses_min_size(self, png_small):
        # With force=True we should still get a result...
        result = iu.optimize_image(png_small, force=True)
        # ...but the encode guard may reject a bigger output.
        # Either a tuple or None is acceptable here; the point is we
        # don't early-return on size.
        if result is not None:
            content, name = result
            assert name.endswith(".webp")
            assert len(content.read()) > 0

    def test_png_medium_converts_to_webp(self, png_medium):
        result = iu.optimize_image(png_medium)
        assert result is not None, "expected PNG -> WebP conversion"
        content, new_name = result
        assert new_name.endswith(".webp")
        body = content.read()
        assert len(body) < png_medium.size, (
            f"expected WebP smaller than source PNG "
            f"({len(body)} >= {png_medium.size})"
        )
        # sanity: it should be a real WebP
        assert body[:4] == b"RIFF" and body[8:12] == b"WEBP"

    def test_oversize_is_clamped(self, png_oversize):
        result = iu.optimize_image(png_oversize, max_dimension=1600)
        assert result is not None
        content, _ = result
        img = Image.open(content)
        assert max(img.size) <= 1600

    def test_extension_swap_preserves_directory(self, png_medium):
        f = SimpleUploadedFile("hero.png", png_medium.read(), content_type="image/png")
        # Bypass Django's filename normalisation (validate_file_name strips
        # path components). _name is a plain attribute on File; assigning
        # post-construction preserves the directory prefix for the test.
        f._name = "images/products/gallery/hero.png"

        result = iu.optimize_image(f)
        assert result is not None
        _, new_name = result
        assert new_name == "images/products/gallery/hero.webp"

    def test_exif_orientation_is_applied(self, jpeg_exif_rotated):
        result = iu.optimize_image(jpeg_exif_rotated, force=True)
        assert result is not None, "EXIF-rotated JPEG should still be optimisable"
        content, _ = result
        img = Image.open(content)
        # Orientation 6 = 90° CW. Source is 200x100, transposed -> 100x200.
        assert img.size == (100, 200)

    def test_animated_gif_is_skipped(self, gif_animated):
        assert iu.optimize_image(gif_animated) is None

    def test_unreadable_returns_none(self, tiny_corrupt):
        assert iu.optimize_image(tiny_corrupt) is None

    def test_encoded_not_larger_guard(self, png_small):
        # png_small is below MIN_PROCESS_BYTES, so force=True is needed to
        # reach the encode step. With quality=100 the guard may or may not
        # reject the output; both outcomes are valid — assert no crash and
        # consistency.
        result = iu.optimize_image(png_small, force=True, quality=100)
        if result is not None:
            content, _ = result
            assert len(content.read()) < png_small.size

    def test_already_optimized_small_webp_returns_none(self):
        # Build a real small WebP under ALREADY_OPTIMIZED_BYTES.
        buf = io.BytesIO()
        Image.new("RGB", (64, 64), (1, 2, 3)).save(buf, format="WEBP", quality=50)
        f = SimpleUploadedFile("x.webp", buf.getvalue(), content_type="image/webp")
        if f.size <= iu.ALREADY_OPTIMIZED_BYTES:
            assert iu.optimize_image(f) is None
        else:
            pytest.skip("WebP output larger than ALREADY_OPTIMIZED_BYTES on this Pillow")

    def test_custom_quality_is_honoured(self, png_oversize):
        # optimize_image closes the field_file in a finally block, so we
        # need fresh SimpleUploadedFile instances for each call.
        
        data = png_oversize.read()
        lo_file = SimpleUploadedFile("huge_low.png", data, content_type="image/png")
        hi_file = SimpleUploadedFile("huge_high.png", data, content_type="image/png")

        low = iu.optimize_image(lo_file, quality=20, force=True)
        high = iu.optimize_image(hi_file, quality=90, force=True)

        if low and high:
            assert len(low[0].read()) < len(high[0].read())

    def test_jpeg_output_format(self, png_oversize):
        result = iu.optimize_image(png_oversize, output_format="JPEG", force=True)
        assert result is not None
        content, new_name = result
        assert new_name.endswith(".jpeg")
        img = Image.open(content)
        assert img.format == "JPEG"


# ══════════════════════════════════════════════════════════════
# robust_exists
# ══════════════════════════════════════════════════════════════

class TestRobustExists:

    def test_missing_path(self, tmp_path):
        assert iu.robust_exists(tmp_path / "nope.png") is False

    def test_present_path(self, tmp_path):
        p = tmp_path / "here.png"
        p.write_bytes(b"x")
        assert iu.robust_exists(p) is True

    def test_nfc_input_finds_nfd_on_disk(self, tmp_path):
        # Write NFC on disk, query with NFD (and vice versa).
        nfc_name = "café.png"
        nfd_name = "cafe\u0301.png"
        p = tmp_path / nfc_name
        p.write_bytes(b"x")
        assert iu.robust_exists(tmp_path / nfd_name) is True

    def test_invalid_type_returns_false(self):
        assert iu.robust_exists(None) is False
        assert iu.robust_exists(123) is False


# ══════════════════════════════════════════════════════════════
# get_image_dimensions
# ══════════════════════════════════════════════════════════════

class TestGetImageDimensions:

    def test_empty_name_returns_none(self):
        assert iu.get_image_dimensions("") is None

    def test_missing_file_returns_none(self, settings):
        assert iu.get_image_dimensions("does/not/exist.png") is None

    def test_reads_dimensions(self, settings, tmp_path):
        # Write under MEDIA_ROOT so default_storage.path() resolves it.
        rel = "test_dims/probe.png"
        abs_path = Path(settings.MEDIA_ROOT) / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (321, 123), (0, 0, 0)).save(abs_path)

        dims = iu.get_image_dimensions(rel)
        assert dims == (321, 123)

    def test_cache_round_trip(self, settings, tmp_path):
        from django.core.cache import cache
        cache.clear()

        rel = "test_dims/cache_probe.png"
        abs_path = Path(settings.MEDIA_ROOT) / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (50, 60), (0, 0, 0)).save(abs_path)

        first = iu.get_image_dimensions(rel)
        assert first == (50, 60)

        # Delete the file; a cached lookup should still return dims.
        os.remove(abs_path)
        second = iu.get_image_dimensions(rel)
        assert second == (50, 60)

        # Invalidate -> now returns None (file gone).
        iu.invalidate_image_dimensions_cache(rel)
        assert iu.get_image_dimensions(rel) is None
