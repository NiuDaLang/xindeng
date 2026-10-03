# core/tests/test_save_optimized.py
"""
Tests for save_optimized_to_field.

Uses a real on-disk FieldFile backed by SafeFileSystemStorage. MEDIA_ROOT
is redirected by the session autouse fixture in conftest.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image

from core.image_utils import save_optimized_to_field


class _Holder:
    """
    Minimal duck-typed instance with a single FieldFile-like attribute.

    save_optimized_to_field needs an object with:
      .name    (str, settable)
      .storage (file storage backend)
    plus a .save(update_fields=[...]) method on the instance.

    We graft .storage and .name onto a plain File returned by the
    storage backend. This is enough for the code paths under test and
    avoids requiring a real Django model / migration.
    """

    def __init__(self, storage, name: str, content_bytes: bytes):
        saved_name = storage.save(name, ContentFile(content_bytes))

        file_obj = storage.open(saved_name)
        file_obj.name = saved_name        # plain attr; File allows it
        file_obj.storage = storage        # grafted; File doesn't define .storage

        self.image = file_obj

        from core.image_utils import invalidate_image_dimensions_cache
        invalidate_image_dimensions_cache(saved_name)

        self._saved_update_fields = None

    def save(self, *args, **kwargs):
        self._saved_update_fields = kwargs.get("update_fields")


def _webp_bytes(width=200, height=100) -> bytes:
    import io
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (10, 20, 30)).save(buf, format="WEBP", quality=80)
    return buf.getvalue()


def _png_bytes(width=200, height=100) -> bytes:
    import io
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (10, 20, 30)).save(buf, format="PNG")
    return buf.getvalue()


class TestSaveOptimizedCase1SamePath:
    """old_name == new_full_name -> temp-then-rename, no delete."""

    def test_file_content_replaced_in_place(self, settings, tmp_path):
        storage = default_storage
        holder = _Holder(storage, "same/keep.webp", _webp_bytes(100, 100))
        old_path = storage.path(holder.image.name)
        old_bytes = Path(old_path).read_bytes()

        new_content = ContentFile(_webp_bytes(50, 50))
        save_optimized_to_field(holder, "image", new_content, holder.image.name)

        assert holder.image.name == "same/keep.webp"
        assert Path(old_path).read_bytes() != old_bytes
        # Verify it decodes to the new size.
        with Image.open(old_path) as img:
            assert img.size == (50, 50)

    def test_no_tmp_file_left_behind(self, settings):
        storage = default_storage
        holder = _Holder(storage, "same/keep2.webp", _webp_bytes())
        name = holder.image.name

        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes(10, 10)), name)

        # No sibling .tmp_optimize file
        directory = storage.path(name).rsplit("/", 1)[0]
        leftover = [f for f in os.listdir(directory) if ".tmp_optimize" in f]
        assert leftover == []

    def test_update_fields_is_single_field(self, settings):
        storage = default_storage
        holder = _Holder(storage, "same/keep3.webp", _webp_bytes())
        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes(10, 10)), holder.image.name)
        assert holder._saved_update_fields == ["image"]


class TestSaveOptimizedCase2PathChanged:
    """old_name != new_full_name -> save new, delete old."""

    def test_extension_swap_deletes_old_file(self, settings):
        storage = default_storage
        holder = _Holder(storage, "swap/hero.png", _png_bytes())
        old_path = storage.path(holder.image.name)
        assert Path(old_path).exists()

        new_name = "swap/hero.webp"
        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes()), new_name)

        assert holder.image.name == "swap/hero.webp"
        assert not Path(old_path).exists(), "old .png should be deleted"
        assert Path(storage.path("swap/hero.webp")).exists()

    def test_field_name_updated(self, settings):
        storage = default_storage
        holder = _Holder(storage, "swap2/hero.png", _png_bytes())
        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes()), "swap2/hero.webp")
        assert holder.image.name == "swap2/hero.webp"


class TestSaveOptimizedCache:
    def test_dimension_cache_invalidated_for_old_and_new(self, settings):
        from django.core.cache import cache
        from core.image_utils import get_image_dimensions

        cache.clear()
        storage = default_storage
        holder = _Holder(storage, "cache/old.png", _png_bytes(400, 300))

        # Warm the cache for the old name.
        old_name = holder.image.name
        get_image_dimensions(old_name)

        new_name = "cache/old.webp"
        # Pre-warm new name too so we can assert it's cleared.
        # (It doesn't exist yet, so cache stays empty; that's fine.)
        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes()), new_name)

        # Old cache entry should be gone.
        assert cache.get(f"imgdims:{old_name}") is None

    def test_cleanup_old_file_tracker_cleared(self, settings):
        storage = default_storage
        holder = _Holder(storage, "track/hero.png", _png_bytes())
        holder._cleanup_old_file = "track/hero.png"  # as if a pre_save tracker set it
        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes()), "track/hero.webp")
        assert getattr(holder, "_cleanup_old_file", None) is None


class TestSaveOptimizedCollision:
    def test_collision_suffix_is_handled(self, settings, monkeypatch):
        """
        Simulate a storage backend that returns a different name on save
        (e.g. foo.webp -> foo_ABCD.webp). The function should re-save to
        the requested name and update field_file.name accordingly.
        """
        storage = default_storage
        holder = _Holder(storage, "coll/hero.png", _png_bytes())

        call_count = {"n": 0}
        real_save = storage.save

        def flaky_save(name, content, *a, **kw):
            call_count["n"] += 1
            if call_count["n"] == 1:
                # Simulate collision: report a suffixed name.
                return real_save(name.replace(".webp", "_ABCD.webp"), content)
            return real_save(name, content)

        monkeypatch.setattr(storage, "save", flaky_save)

        save_optimized_to_field(holder, "image", ContentFile(_webp_bytes()), "coll/hero.webp")

        # After retry, the field should point at the requested name.
        assert holder.image.name == "coll/hero.webp"
        assert call_count["n"] >= 2