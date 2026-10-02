# core/widgets.py
"""
Form widgets that mark a file input as a crop-tool target.

The crop tool (static/js/crop_tool.js) scans for `.crop-tool-target`
inputs and reads their data attributes to configure the modal.

Two variants are provided because the codebase uses two different
base widgets depending on whether the field should show a "Clear"
checkbox alongside the file input:

    CropTargetFileInput             → for forms.FileInput slots
    CropTargetClearableFileInput    → for ClearableFileInput slots
                                      (subclass of creators' Custom variant)

Both are intentionally thin. They only:
  * add the marker class `crop-tool-target`
  * inject `data-crop-presets` and `data-crop-default`
  * keep `accept="image/*"` unless overridden
"""

from django import forms


_DEFAULT_PRESETS = "1:1,4:3,free"
_DEFAULT_DEFAULT = "4:3"


def _build_attrs(attrs, crop_presets, crop_default, base_class):
    merged = {
        "class": base_class,
        "accept": "image/*",
        "data-crop-presets": crop_presets,
        "data-crop-default": crop_default,
    }
    if attrs:
        # Caller-supplied attrs win, but ensure the marker class is kept.
        merged.update(attrs)
        merged["class"] = merged["class"] + " crop-tool-target"
    return merged


class CropTargetFileInput(forms.FileInput):
    """
    FileInput that marks itself for the crop tool.

    Used for fields where the form uses plain FileInput (no Clear checkbox),
    e.g. ArtisanProductForm.images and ProductVariationForm.images.
    """

    def __init__(self, attrs=None, crop_presets=_DEFAULT_PRESETS,
                 crop_default=_DEFAULT_DEFAULT):
        base = "file-input file-input-bordered file-input-sm w-full crop-tool-target"
        super().__init__(_build_attrs(attrs, crop_presets, crop_default, base))


class CropTargetClearableFileInput(forms.ClearableFileInput):
    """
    ClearableFileInput that marks itself for the crop tool.

    Mirrors creators.forms.CustomClearableFileInput's value_from_datadict
    behavior (a submitted file wins over the clear checkbox), but lives in
    core/ so it can be used from any app without importing from creators.

    If you later want to unify with creators.CustomClearableFileInput,
    subclass that one instead and add the same __init__ body.
    """

    template_name = "widgets/clearable_file_input.html"

    def __init__(self, attrs=None, crop_presets=_DEFAULT_PRESETS,
                 crop_default=_DEFAULT_DEFAULT):
        base = "file-input file-input-bordered w-full crop-tool-target"
        super().__init__(_build_attrs(attrs, crop_presets, crop_default, base))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        attrs_dict = context["widget"].get("attrs", {})
        attrs_dict.pop("disabled", None)
        attrs_dict.pop("checked", None)
        return context

    def value_from_datadict(self, data, files, name):
        upload = files.get(name)
        if upload:
            # A new file was uploaded — prefer it, ignore the clear checkbox.
            # Mirrors creators.forms.CustomClearableFileInput.
            return upload
        return super().value_from_datadict(data, files, name)