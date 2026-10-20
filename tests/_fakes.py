# tests/_fakes.py
"""
Shared test doubles. Not a test module — no test_* functions here.

Lives at the project root (rather than under an app) so every app's
test suite can import from it without a circular or app-specific path.
"""

from __future__ import annotations
from django.contrib.auth import get_user_model


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


def make_superuser(
    *,
    username: str = "fake_superu",
    email: str = "fake-superu@example.com",
    password: str = "x",
):
    """
    Create an Account that satisfies both of the project's
    superuser checks:

      * is_admin      → Account.has_perm() returns this. Django's
                        admin site consults has_perm() for
                        has_view_permission / has_change_permission,
                        so any admin changelist or change view will
                        403 without it.

      * is_superadmin → the project's own flag. Checked by
                        accounts.decorators.superuser_required and by
                        custom ModelAdmin.get_actions overrides.

    The real MyAccountManager.create_superuser() sets both, plus
    is_staff and is_active. This helper reproduces that state
    without going through create_superuser(), which has a custom
    signature (email-first positional) that is awkward to use from
    fixtures.

    Callers who need a custom username or email for a specific
    test can pass them; the defaults work for any test that does
    not care.
    """
    Account = get_user_model()
    user = Account.objects.create_user(
        username=username,
        email=email,
        receive_newsletter=False,
        password=password,
        is_active=True,
        is_staff=True,
    )
    user.is_admin = True
    user.is_superadmin = True
    user.save(update_fields=["is_admin", "is_superadmin"])
    return user