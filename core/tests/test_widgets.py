"""
Tests for core.widgets — the crop-tool marker classes and data attributes.
"""

from __future__ import annotations

import pytest
from django import forms

from core.widgets import (
    CropTargetClearableFileInput,
    CropTargetFileInput,
    _DEFAULT_DEFAULT,
    _DEFAULT_PRESETS,
)


class _F(forms.Form):
    plain = forms.FileField(widget=CropTargetFileInput)
    clearable = forms.ImageField(widget=CropTargetClearableFileInput)


class TestCropTargetFileInput:

    def test_render_contains_marker_class(self):
        widget = CropTargetFileInput()
        html = widget.render("images", None, attrs={"id": "id_images"})
        assert "crop-tool-target" in html

    def test_render_contains_presets(self):
        widget = CropTargetFileInput()
        html = widget.render("images", None)
        assert f'data-crop-presets="{_DEFAULT_PRESETS}"' in html
        assert f'data-crop-default="{_DEFAULT_DEFAULT}"' in html

    def test_custom_presets_and_default(self):
        widget = CropTargetFileInput(crop_presets="16:9,1:1", crop_default="16:9")
        html = widget.render("images", None)
        assert 'data-crop-presets="16:9,1:1"' in html
        assert 'data-crop-default="16:9"' in html

    def test_accept_defaults_to_image(self):
        widget = CropTargetFileInput()
        html = widget.render("images", None)
        assert 'accept="image/*"' in html

    def test_caller_attrs_win_but_marker_class_kept(self):
        widget = CropTargetFileInput()
        html = widget.render("images", None, attrs={"data-custom": "yes"})
        assert 'data-custom="yes"' in html
        assert "crop-tool-target" in html


class TestCropTargetClearableFileInput:

    def test_render_contains_marker_class(self):
        widget = CropTargetClearableFileInput()
        html = widget.render("featured", None)
        assert "crop-tool-target" in html

    def test_value_from_datadict_prefers_upload(self):
        widget = CropTargetClearableFileInput()
        upload = object()
        files = {"featured": upload}
        data = {"featured-clear": "on"}
        result = widget.value_from_datadict(data, files, "featured")
        assert result is upload

    def test_value_from_datadict_falls_back(self):
        widget = CropTargetClearableFileInput()
        # No upload in files -> defer to super() (ClearableFileInput)
        result = widget.value_from_datadict({}, {}, "featured")
        assert result is None  # no clear flag, no upload


class TestFormLevelIntegration:

    def test_plain_file_field_renders_with_marker(self):
        form = _F()
        html = str(form["plain"])
        assert "crop-tool-target" in html

    def test_clearable_file_field_renders_with_marker(self):
        form = _F()
        html = str(form["clearable"])
        assert "crop-tool-target" in html


