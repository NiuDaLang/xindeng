# core/tests/test_signals.py
"""
Tests for core.signals — the inline vs async decision rules.

We don't spin up Celery; we monkeypatch core.tasks.optimize_image_task.delay
and core.signals._process_inline to observe which branch was taken.
"""

from __future__ import annotations

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from core.image_utils import INLINE_SIZE_THRESHOLD_BYTES

core_signals = None  # populated by the module-scope fixture below


@pytest.fixture(scope="module", autouse=True)
def _import_core_signals():
    """
    Import core.signals lazily so we don't trip AppRegistryNotReady
    during pytest collection.

    core/signals.py calls register_all() at import time, which needs
    apps.get_model() to work — only possible once CoreConfig.ready()
    has run, i.e. after django.setup(). Fixtures run after that.
    """
    global core_signals
    from core import signals
    core_signals = signals
    yield

# ──────────────────────────────────────────────────────────────
# Fake instance + field_file
# ──────────────────────────────────────────────────────────────

class _FakeMeta:
    app_label = "store"
    model_name = "product"


class _FakeInstance:
    _meta = _FakeMeta()
    pk = 42

    def __init__(self, field_file, field_name: str = "images"):
        setattr(self, field_name, field_file)


def _file_of_size(name: str, size: int) -> SimpleUploadedFile:
    # Real bytes; SimpleUploadedFile.size is len(content).
    return SimpleUploadedFile(name, b"x" * size)


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def patch_inline(monkeypatch):
    calls = []
    def fake_inline(instance, field_name, opts):
        calls.append((instance, field_name, dict(opts)))
    monkeypatch.setattr(core_signals, "_process_inline", fake_inline)
    return calls


@pytest.fixture
def patch_async(monkeypatch):
    calls = []
    def fake_async(instance, field_name, opts):
        calls.append((instance, field_name, dict(opts)))
    monkeypatch.setattr(core_signals, "_schedule_async", fake_async)
    return calls


# ──────────────────────────────────────────────────────────────
# Receiver-level: dispatch decision
# ──────────────────────────────────────────────────────────────

HERO_OPTS = {
    "max_dimension": 1600,
    "quality": 82,
    "inline_above_threshold": True,
}
GALLERY_OPTS = {"max_dimension": 1600, "quality": 82}


class TestReceiverDispatch:

    def _call(self, field_name, opts, instance):
        receiver = core_signals.make_receiver("store", "product", field_name, opts)
        receiver(sender=object, instance=instance, created=True)

    # helper to build an instance wired for a specific field name
    @staticmethod
    def _inst(field_file, field_name="images"):
        return _FakeInstance(field_file, field_name=field_name)

    def test_hero_small_file_is_inline(self, patch_inline, patch_async, monkeypatch):
        # Bypass the is_skippable / is_already_optimized guards by
        # pretending the file is a fresh, large-enough PNG.
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("hero.png", 500 * 1024)   # 500 KB < 1 MB
        self._call("images", HERO_OPTS, _FakeInstance(f))

        assert len(patch_inline) == 1
        assert len(patch_async) == 0

    def test_hero_large_file_still_inline(self, patch_inline, patch_async, monkeypatch):
        # Hero opts have inline_above_threshold=True, so even a 5 MB file
        # should be inline (as long as it's under the 20 MB hard cap).
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("hero.png", 5 * 1024 * 1024)
        self._call("images", HERO_OPTS, _FakeInstance(f))

        assert len(patch_inline) == 1
        assert len(patch_async) == 0

    def test_hero_above_hard_cap_goes_async(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("hero.png", core_signals.INLINE_HARD_CAP_BYTES + 1)
        self._call("images", HERO_OPTS, _FakeInstance(f))

        assert len(patch_async) == 1
        assert len(patch_inline) == 0

    def test_hero_exactly_at_hard_cap_goes_async(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("hero.png", core_signals.INLINE_HARD_CAP_BYTES)
        self._call("images", HERO_OPTS, _FakeInstance(f))

        # >= cap -> async
        assert len(patch_async) == 1

    def test_gallery_small_file_is_inline(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("gallery.png", 500 * 1024)
        self._call("image", GALLERY_OPTS, self._inst(f, field_name="image"))

        assert len(patch_inline) == 1
        assert len(patch_async) == 0

    def test_gallery_large_file_is_async(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("gallery.png", 2 * 1024 * 1024)
        self._call("image", GALLERY_OPTS, self._inst(f, field_name="image"))

        assert len(patch_async) == 1
        assert len(patch_inline) == 0

    def test_gallery_exactly_at_inline_threshold_is_async(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("gallery.png", INLINE_SIZE_THRESHOLD_BYTES)
        self._call("image", GALLERY_OPTS, self._inst(f, field_name="image"))

        assert len(patch_async) == 1

    def test_gallery_one_byte_below_threshold_is_inline(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: False)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("gallery.png", INLINE_SIZE_THRESHOLD_BYTES - 1)
        self._call("image", GALLERY_OPTS, self._inst(f, field_name="image"))

        assert len(patch_inline) == 1

    def test_skip_guard_short_circuits(self, patch_inline, patch_async, monkeypatch):
        monkeypatch.setattr(core_signals, "is_skippable", lambda f: True)
        monkeypatch.setattr(core_signals, "is_already_optimized", lambda f: False)

        f = _file_of_size("hero.png", 5 * 1024 * 1024)
        self._call("images", HERO_OPTS, _FakeInstance(f))

        assert patch_inline == []
        assert patch_async == []

    def test_skip_image_optimization_attribute_bypasses(self, patch_inline, patch_async):
        instance = _FakeInstance(_file_of_size("hero.png", 5 * 1024 * 1024))
        instance._skip_image_optimization = True

        receiver = core_signals.make_receiver("store", "product", "images", HERO_OPTS)
        receiver(sender=object, instance=instance, created=True)

        assert patch_inline == []
        assert patch_async == []


# ──────────────────────────────────────────────────────────────
# Registry integrity
# ──────────────────────────────────────────────────────────────

class TestRegistry:

    def test_hero_fields_are_inline_above_threshold(self):
        for key in [
            ("store", "product", "images"),
            ("store", "productvariation", "images"),
            ("blog", "post", "featured_image"),
        ]:
            assert key in core_signals.IMAGE_FIELD_REGISTRY, f"missing registry entry: {key}"
            assert core_signals.IMAGE_FIELD_REGISTRY[key].get("inline_above_threshold") is True

    def test_gallery_fields_are_not_inline_above_threshold(self):
        for key in [
            ("store", "productgallery", "image"),
            ("store", "productvariationgallery", "image"),
        ]:
            assert key in core_signals.IMAGE_FIELD_REGISTRY
            assert core_signals.IMAGE_FIELD_REGISTRY[key].get("inline_above_threshold", False) is False

    def test_hard_cap_is_20mb(self):
        assert core_signals.INLINE_HARD_CAP_BYTES == 20 * 1024 * 1024

    def test_inline_threshold_is_1mb(self):
        assert INLINE_SIZE_THRESHOLD_BYTES == 1 * 1024 * 1024

