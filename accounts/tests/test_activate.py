# accounts/tests/test_activate.py
"""
Tests for the registration activation view.

Regression guard for the 2026-10-29 guest walk finding: activate
crashed with ValueError when auth_login was called without an
explicit backend under the two-backend AUTHENTICATION_BACKENDS
config. The activation itself succeeded (is_active=True) before
the crash, so the account was usable after a manual retry — the
500 was on the auto-login step only. The test pins the full path
so a future backend addition cannot reintroduce the crash.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

Account = get_user_model()


@pytest.mark.django_db
class TestActivateView:

    def test_activate_marks_user_active_and_logs_in(self, client):
        """The full path: is_active flip, session set, redirect."""
        user = Account.objects.create_user(
            username="activation-test",
            email="activation-test@example.com",
            receive_newsletter=False,
            password="a-test-password-1!",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse("activate", kwargs={"uidb64": uid, "token": token})

        response = client.get(url)

        # 1. Redirect to the post-activate target, not 500.
        assert response.status_code == 302
        assert response.url == reverse("dashboard", kwargs={"subpage": "main"})

        # 2. Account is active.
        user.refresh_from_db()
        assert user.is_active is True

        # 3. Session carries the ModelBackend marker, which is the
        #    specific invariant that the missing-backend crash broke.
        #    Django stores it in the _auth_user_backend session key.
        assert client.session["_auth_user_backend"] == (
            "django.contrib.auth.backends.ModelBackend"
        )

        # 4. The session user id matches.
        assert client.session["_auth_user_id"] == str(user.pk)

    def test_activate_does_not_log_in_on_invalid_token(self, client):
        """Invalid token: no login, no is_active flip, redirect to register."""
        user = Account.objects.create_user(
            username="activation-invalid",
            email="activation-invalid@example.com",
            receive_newsletter=False,
            password="a-test-password-1!",
        )
        user.is_active = False
        user.save(update_fields=["is_active"])

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        url = reverse("activate", kwargs={"uidb64": uid, "token": "bad-token"})

        response = client.get(url)

        # Redirected to register (the else branch in the view).
        assert response.status_code == 302
        assert response.url == reverse("register")

        user.refresh_from_db()
        assert user.is_active is False

        # No session logged in.
        assert "_auth_user_id" not in client.session
        assert "_auth_user_backend" not in client.session