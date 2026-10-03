# core/tests/_fakes.py
"""
Shared test doubles. Not a test module — no test_* functions here.
"""

from __future__ import annotations


class FakeFieldFile:
    """
    Minimal stand-in for a FieldFile when we only need .name and .size
    and the code under test should early-return before opening.

    We can't use SimpleUploadedFile for these cases because Django's
    validate_file_name() strips directory components from the name,
    which defeats tests that specifically check path-prefix behaviour.
    """

    def __init__(self, name: str, size: int):
        self.name = name
        self._size = size

    @property
    def size(self):
        return self._size

    def open(self, *a, **kw):
        raise AssertionError(
            f"FakeFieldFile.open() called on {self.name!r} — "
            "the code under test should have early-returned"
        )

    def close(self):
        pass