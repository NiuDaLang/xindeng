# store/tests/test_secure_file_download_gate.py
"""
Security and behaviour tests for store.views.secure_file_download_gate.

Covers:
  * Path containment (directory traversal, absolute paths, symlinks)
  * DigitalDownloadToken property split (is_revoked / is_expired / ...)
  * The gate's HTTP behaviour (200 / 403 / 404 / login redirect)
  * The is_claimed write-on-first-download contract

MEDIA_ROOT is redirected per-test by conftest._redirect_media_root; this
file additionally redirects settings.XINDENG_VAULT_ROOT to a per-test
tmp path so no test writes into the real private_digital_vault/ tree.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.urls import reverse
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────
# Vault-root and vault-file fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    """Per-test vault directory, wired into settings."""
    vault = tmp_path / "private_digital_vault"
    vault.mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def vault_file(vault_root):
    """A legitimate ebook inside the vault. Returns its relative path."""
    ebooks = vault_root / "ebooks"
    ebooks.mkdir(parents=True, exist_ok=True)
    sample = ebooks / "sample.pdf"
    sample.write_bytes(b"%PDF-1.4\n% sample ebook for tests\n%%EOF\n")
    return "ebooks/sample.pdf"


# ──────────────────────────────────────────────────────────────────
# Object-graph factory
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def make_chain(db, django_user_model, vault_root):
    """
    Returns a callable that builds a full (user, product, variation,
    order, order_product, token) graph for a given digital_file_path.

    Used by the traversal tests to inject hostile paths without
    disturbing the DB fixture data between cases.
    """
    from category.models import Category
    from store.models import Product, ProductVariation, DigitalDownloadToken
    from orders.models import Order, OrderProduct

    _counter = {"n": 0}

    def _make(digital_file_path: str, *, order_product_digital_file_path: str | None = None):
        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"vaultuser{n}",
            email=f"vault{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )

        category = Category.objects.create(
            category_name=f"Digital Goods {n}",
            slug=f"digital-goods-{n}",
            product_format="e-product",
        )

        product = Product.objects.create(
            product_name=f"Test Ebook {n}",
            category=category,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_active=True,
            status="Published",
        )

        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
            digital_file_path=digital_file_path,
        )

        order = Order.objects.create(
            user=user,
            order_number=f"TEST-VAULT-{n:04d}",
            email=user.email,
            is_ordered=True,
            order_status="Processing",
        )

        order_product = OrderProduct.objects.create(
            order=order,
            user=user,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
            digital_file_path=order_product_digital_file_path,
        )

        token = DigitalDownloadToken.objects.create(
            user=user,
            order_product=order_product,
            expires_at=timezone.now() + timedelta(days=7),
        )

        return {
            "user": user,
            "product": product,
            "variation": variation,
            "order": order,
            "order_product": order_product,
            "token": token,
        }

    return _make


@pytest.fixture
def make_guest_chain(db, vault_root):
    """
    Companion to make_chain for the guest-purchase shape: Order.user and
    OrderProduct.user are None, and the token carries an email snapshot
    instead of a user FK. Mirrors what issue_download_token produces for
    a guest order after commit 2.
    """
    from category.models import Category
    from store.models import Product, ProductVariation, DigitalDownloadToken
    from orders.models import Order, OrderProduct

    _counter = {"n": 0}

    def _make(digital_file_path, token_email="guest-buyer@example.com"):
        _counter["n"] += 1
        n = _counter["n"]

        category = Category.objects.create(
            category_name=f"Guest Digital {n}",
            slug=f"guest-digital-{n}",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name=f"Guest Ebook {n}",
            category=category,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
            digital_file_path=digital_file_path,
        )
        order = Order.objects.create(
            user=None,
            order_number=f"GUEST-VAULT-{n:04d}",
            email=token_email or "",
            is_ordered=True,
            order_status="Processing",
        )
        order_product = OrderProduct.objects.create(
            order=order,
            user=None,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
        )
        token = DigitalDownloadToken.objects.create(
            user=None,
            email=token_email,
            order_product=order_product,
            expires_at=timezone.now() + timedelta(days=7),
        )
        return {
            "product": product,
            "variation": variation,
            "order": order,
            "order_product": order_product,
            "token": token,
        }

    return _make

# ──────────────────────────────────────────────────────────────────
# Path containment — the security fix
# ──────────────────────────────────────────────────────────────────

class TestPathContainment:
    """Each test builds a chain whose digital_file_path is hostile."""

    def test_valid_nested_path_serves_file(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        client.force_login(chain["user"])

        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)

        assert response.status_code == 200
        body = b"".join(response.streaming_content)
        assert body == b"%PDF-1.4\n% sample ebook for tests\n%%EOF\n"

    @pytest.mark.parametrize("hostile", [
        "../outside.pdf",
        "../../outside.pdf",
        "ebooks/../../outside.pdf",
        "ebooks/../../../etc/passwd",
    ])
    def test_dotdot_escape_is_blocked(self, client, make_chain, hostile):
        chain = make_chain(hostile)
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_absolute_path_is_blocked(self, client, make_chain):
        # pathlib drops the left-hand side when the right is absolute, so
        # this must resolve to /etc/passwd — outside the vault — and 404.
        chain = make_chain("/etc/passwd")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_symlink_escape_is_blocked(self, client, make_chain, vault_root, tmp_path):
        # Create an out-of-vault file and a symlink inside the vault that
        # points at it.
        outside = tmp_path / "outside.pdf"
        outside.write_bytes(b"SECRET OUTSIDE VAULT")
        link = vault_root / "escape.pdf"
        link.symlink_to(outside)

        chain = make_chain("escape.pdf")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_symlink_inside_vault_is_also_rejected(self, client, make_chain, vault_root, vault_file):
        # Even a symlink pointing *inside* the vault is refused — policy
        # decision documented in the view.
        target = vault_root / vault_file
        link = vault_root / "alias.pdf"
        link.symlink_to(target)

        chain = make_chain("alias.pdf")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_missing_file_raises_404(self, client, make_chain):
        chain = make_chain("ebooks/does-not-exist.pdf")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_directory_instead_of_file_raises_404(self, client, make_chain, vault_root):
        (vault_root / "ebooks").mkdir(exist_ok=True)
        chain = make_chain("ebooks")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_empty_digital_file_path_raises_404(self, client, make_chain):
        chain = make_chain("")
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404


# ──────────────────────────────────────────────────────────────────
# Token properties — the semantic split
# ──────────────────────────────────────────────────────────────────

class TestTokenProperties:
    """
    Property-level tests for DigitalDownloadToken. Do not go through the
    HTTP gate — prove the property semantics directly.
    """

    def test_fresh_token_not_revoked_not_expired(self, db, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        assert t.is_revoked is False
        assert t.is_expired is False
        assert t.is_revoked_or_expired is False

    def test_time_expired_token_is_expired_not_revoked(self, db, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        t.expires_at = timezone.now() - timedelta(seconds=1)
        t.save(update_fields=["expires_at"])

        assert t.is_revoked is False
        assert t.is_expired is True
        assert t.is_revoked_or_expired is True

    def test_revoked_token_is_revoked_not_expired(self, db, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        t.is_active = False
        t.save(update_fields=["is_active"])

        assert t.is_revoked is True
        assert t.is_expired is False
        assert t.is_revoked_or_expired is True

    def test_revoked_and_expired_token_is_both(self, db, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        t.is_active = False
        t.expires_at = timezone.now() - timedelta(seconds=1)
        t.save(update_fields=["is_active", "expires_at"])

        assert t.is_revoked is True
        assert t.is_expired is True
        assert t.is_revoked_or_expired is True


# ──────────────────────────────────────────────────────────────────
# Gate behaviour — auth, error responses, claim write
# ──────────────────────────────────────────────────────────────────

class TestGateBehaviour:

    def test_anonymous_user_redirected_to_login(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_other_users_token_returns_404(self, client, make_chain, vault_file, django_user_model):
        chain = make_chain(vault_file)
        intruder = django_user_model.objects.create_user(
            username="intruder",
            email="intruder@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(intruder)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_revoked_token_returns_403_with_cancellation_message(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        t.is_active = False
        t.save(update_fields=["is_active"])

        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[t.id])
        response = client.get(url)

        assert response.status_code == 403
        body = response.content.decode("utf-8")
        assert "Revoked" in body or "已撤銷" in body

    def test_expired_token_returns_403_with_expiry_message(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        t = chain["token"]
        t.expires_at = timezone.now() - timedelta(hours=1)
        t.save(update_fields=["expires_at"])

        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[t.id])
        response = client.get(url)

        assert response.status_code == 403
        body = response.content.decode("utf-8")
        assert "Expired" in body or "已失效" in body

    def test_valid_download_marks_claimed(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        op = chain["order_product"]
        assert op.is_claimed is False
        assert op.claim_timestamp is None

        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 200

        op.refresh_from_db()
        assert op.is_claimed is True
        assert op.claim_timestamp is not None

    def test_second_download_does_not_overwrite_claim_timestamp(self, client, make_chain, vault_file):
        chain = make_chain(vault_file)
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])

        client.get(url)
        chain["order_product"].refresh_from_db()
        first_claim = chain["order_product"].claim_timestamp

        client.get(url)
        chain["order_product"].refresh_from_db()
        second_claim = chain["order_product"].claim_timestamp

        assert first_claim == second_claim


class TestGuestEmailFallback:
    """
    Guest tokens carry user=None and an email snapshot. The gate's
    contract for these tokens is:

      * anonymous request                                  -> 302 to login
      * authenticated, email matches token.email (any case) -> 200
      * authenticated, email differs                        -> 404 (not 403;
        do not leak that the token exists)
      * token.email empty or whitespace-only                -> 404 for
        everyone, including an authenticated user whose own email is
        also empty

    The last case is the important one: an empty token.email must never
    match. Without that guard, an Account with an empty email would pass
    a naive string comparison and the gate would fail open.
    """

    def test_guest_token_serves_bytes_to_authenticated_user_with_matching_email(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="guest-buyer@example.com")
        user = django_user_model.objects.create_user(
            username="guest_match",
            email="guest-buyer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)

        assert response.status_code == 200
        body = b"".join(response.streaming_content)
        assert body == b"%PDF-1.4\n% sample ebook for tests\n%%EOF\n"

    def test_guest_download_marks_claimed(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="guest-buyer@example.com")
        user = django_user_model.objects.create_user(
            username="guest_claim",
            email="guest-buyer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        op = chain["order_product"]
        assert op.is_claimed is False

        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 200

        op.refresh_from_db()
        assert op.is_claimed is True
        assert op.claim_timestamp is not None

    def test_guest_token_rejects_authenticated_user_with_different_email(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="guest-buyer@example.com")
        user = django_user_model.objects.create_user(
            username="wrong_guest",
            email="someone-else@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_guest_token_email_match_is_case_insensitive(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="Guest-Buyer@Example.COM")
        user = django_user_model.objects.create_user(
            username="case_guest",
            email="guest-buyer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 200

    def test_guest_token_with_empty_email_rejects_all_authenticated_users(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="")
        user = django_user_model.objects.create_user(
            username="empty_email_user",
            email="whatever@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_guest_token_with_whitespace_email_rejects_all_authenticated_users(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="   ")
        user = django_user_model.objects.create_user(
            username="ws_email_user",
            email="whatever2@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 404

    def test_guest_token_anonymous_still_redirects_to_login(
        self, client, make_guest_chain, vault_file,
    ):
        chain = make_guest_chain(vault_file, token_email="guest-buyer@example.com")
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]

    def test_guest_token_second_download_does_not_overwrite_claim_timestamp(
        self, client, make_guest_chain, vault_file, django_user_model,
    ):
        chain = make_guest_chain(vault_file, token_email="guest-buyer@example.com")
        user = django_user_model.objects.create_user(
            username="guest_second",
            email="guest-buyer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        url = reverse("secure_file_download_gate", args=[chain["token"].id])

        client.get(url)
        chain["order_product"].refresh_from_db()
        first = chain["order_product"].claim_timestamp

        client.get(url)
        chain["order_product"].refresh_from_db()
        second = chain["order_product"].claim_timestamp

        assert first == second


class TestCustomGateBranch:
    """
    Tests for the CUSTOM-delivery branch of secure_file_download_gate:
    file resolution prefers OrderProduct.digital_file_path when set,
    and the security-critical containment/claim logic is unchanged
    for both pointers.

    See store/views.py::secure_file_download_gate and the CUSTOM
    pipeline v2 handoff for the two-pointer reasoning.
    """

    def test_serves_order_product_file_when_set(
        self, client, make_chain, vault_root,
    ):
        """
        When both pointers are set to different files, the gate
        serves the order-product file. This is the test that catches
        a "simplify back to one pointer" refactor. If the gate ever
        resolves the variation pointer despite the order-product
        pointer being set, a CUSTOM customer would receive the shared
        (possibly wrong-customer) variation file.
        """
        # Two distinct files, distinct bytes.
        ebooks = vault_root / "ebooks"
        ebooks.mkdir(parents=True, exist_ok=True)

        variation_file = ebooks / "instant.pdf"
        variation_file.write_bytes(b"%PDF-1.4\n% INSTANT variation file\n")

        custom_file = ebooks / "custom.pdf"
        custom_file.write_bytes(b"%PDF-1.4\n% CUSTOM order-product file\n")

        chain = make_chain(
            "ebooks/instant.pdf",
            order_product_digital_file_path="ebooks/custom.pdf",
        )
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)

        assert response.status_code == 200
        body = b"".join(response.streaming_content)
        # Serves the custom file, not the instant one.
        assert body == b"%PDF-1.4\n% CUSTOM order-product file\n"
        assert body != b"%PDF-1.4\n% INSTANT variation file\n"

        # And the claim flag still flips on first successful serve.
        chain["order_product"].refresh_from_db()
        assert chain["order_product"].is_claimed is True

    def test_404s_when_neither_pointer_set(self, client, make_chain):
        """
        Both pointers empty: 404. Pins the fail-closed branch. This
        is the same outcome the old single-pointer check produced;
        the test makes the branch explicit for the new precedence
        rule.
        """
        chain = make_chain("", order_product_digital_file_path=None)
        # The factory's default None already leaves
        # OrderProduct.digital_file_path null. The variation pointer
        # is the empty string. Neither pointer resolves.
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)

        assert response.status_code == 404
        chain["order_product"].refresh_from_db()
        # 404 fires before the claim flip. The customer received
        # nothing.
        assert chain["order_product"].is_claimed is False

    def test_404s_when_order_product_pointer_escapes_vault(
        self, client, make_chain, vault_root, tmp_path,
    ):
        """
        A traversal attempt on the order-product pointer is caught by
        the containment check, before the claim flip. This is the
        security-critical assertion: the claim flip happens after the
        containment check, so a customer cannot force a 404 to self-
        lock their own line outside the cancellation rules.
        """
        # Plant a file one level above the vault root.
        (tmp_path / "outside.pdf").write_bytes(b"%PDF-1.4\n% outside\n")

        # The variation pointer is a legitimate file so that if the
        # gate ever falls back to it, the test would see a 200 and
        # fail loudly. The order-product pointer is hostile.
        ebooks = vault_root / "ebooks"
        ebooks.mkdir(parents=True, exist_ok=True)
        (ebooks / "instant.pdf").write_bytes(b"%PDF-1.4\n% INSTANT\n")

        chain = make_chain(
            "ebooks/instant.pdf",
            order_product_digital_file_path="../outside.pdf",
        )
        client.force_login(chain["user"])
        url = reverse("secure_file_download_gate", args=[chain["token"].id])
        response = client.get(url)

        assert response.status_code == 404
        chain["order_product"].refresh_from_db()
        assert chain["order_product"].is_claimed is False

