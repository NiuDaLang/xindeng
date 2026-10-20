# tests/

Shared test helpers for the project. Individual apps keep their
test suites in `<app>/tests/`.

## Fixtures

`conftest.py` provides image-byte factories (`png_small`,
`png_medium`, `png_oversize`, `jpeg_exif_rotated`, `gif_animated`,
`tiny_corrupt`) used across the image-pipeline and vault test suites.

The media-root redirect lives in the project-root `conftest.py` so
every test in every app is protected: nothing writes into the real
`media/` tree. The image-byte factories live in the same file, for
the same reason — pytest's conftest discovery walks the ancestor
chain from each test file, so a fixture in a sibling package is
invisible to tests in a different package.

`_fakes.py` provides `FakeFieldFile`, a minimal `FieldFile` stand-in
for tests that need a `.name` with a directory prefix (Django's
`validate_file_name` strips paths at construction time).

## Transaction semantics

`transaction.on_commit()` callbacks do **not** fire under pytest-django's
default test transaction. Use the `django_capture_on_commit_callbacks`
fixture whenever a test asserts on dispatch behaviour.

## Superusers in tests

An `Account` is a "superuser" for admin purposes only when both
`is_admin` and `is_superadmin` are True:

  * `is_admin=True` — required by Django's admin site, which
    consults `Account.has_perm()` for `has_view_permission` and
    `has_change_permission`. A user without it gets a 403 on any
    admin changelist or change view, regardless of `is_staff`.

  * `is_superadmin=True` — required by the project's own checks:
    `accounts.decorators.superuser_required` and any
    `ModelAdmin.get_actions` override that filters by the flag.

`MyAccountManager.create_superuser()` sets both (plus `is_staff`
and `is_active`). Fixtures that construct `Account` directly must
do the same — see `tests/_fakes.py::make_superuser`.