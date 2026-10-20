# tests/

Shared test helpers for the project. Individual apps keep their
test suites in `<app>/tests/`.

## Fixtures

`conftest.py` provides image-byte factories (`png_small`,
`png_medium`, `png_oversize`, `jpeg_exif_rotated`, `gif_animated`,
`tiny_corrupt`) used across the image-pipeline and vault test suites.

The media-root redirect lives in `xindeng/conftest.py` so every test
in every app is protected: nothing writes into the real `media/` tree.

`_fakes.py` provides `FakeFieldFile`, a minimal `FieldFile` stand-in
for tests that need a `.name` with a directory prefix (Django's
`validate_file_name` strips paths at construction time).

## Transaction semantics

`transaction.on_commit()` callbacks do **not** fire under pytest-django's
default test transaction. Use the `django_capture_on_commit_callbacks`
fixture whenever a test asserts on dispatch behaviour.