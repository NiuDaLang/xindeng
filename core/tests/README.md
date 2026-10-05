# core.tests

Tests for the image pipeline: `sanitize_filename`, `optimize_image`,
`save_optimized_to_field`, the signal dispatchers, and the crop widgets.

Run: `pytest core/tests/ -v` from the project root.

`MEDIA_ROOT` is redirected per-test via `conftest._redirect_media_root`,
so no file ever lands in the real `media/` tree. Use `FakeFieldFile`
from `_fakes.py` when a test needs a `.name` with a directory prefix
(Django's `validate_file_name` strips paths at construction time).