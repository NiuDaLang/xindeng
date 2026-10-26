# store/tests/test_vault_upload_approval.py
"""
Tests for review_vault_upload_approve.

Covers the happy path (file moves, pointer updates, log written),
the two gates (superuser, PENDING-only), the compensating-rename-on-
failure path, and the retire-previous-file behaviour.

The `superuser` fixture uses `make_superuser` (from tests/_fakes.py),
which sets both is_admin and is_superadmin. This file only strictly
needs is_superadmin — every admin-facing action here is guarded by
superuser_required, not by Django's ModelAdmin.has_view_permission.
But the fixture is shared across the three store vault test files
and the settlements aggregate tests for uniformity; if this file
ever gains a test that hits the admin changelist (e.g. testing
OrderAdmin.get_actions filtering), the fixture is already correct.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from django.urls import reverse

from tests._fakes import make_superuser

# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    vault = tmp_path / "private_digital_vault"
    (vault / "_pending").mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def superuser(db):
    return make_superuser(username="superu", email="superu@example.com")


@pytest.fixture
def regular_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="regular",
        email="regular@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def chain_with_pending(db, django_user_model, vault_root):
    """
    Returns a dict with artisan, product, variation, and a pending
    ArtisanVaultUpload whose staged file exists on disk.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import (
        Product, ProductVariation, ArtisanVaultUpload,
    )

    user = django_user_model.objects.create_user(
        username="artisan",
        email="artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user, display_name="Approval Artisan",
        slug="approval-artisan", is_verified=True,
    )
    category = Category.objects.create(
        category_name="Approval Digital",
        slug="approval-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Approval Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Pending",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )

    staged_name = "abc-123.pdf"
    staged_path = vault_root / "_pending" / staged_name
    staged_path.write_bytes(b"%PDF-1.4\n% approval test\n%%EOF\n")

    upload = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        storage_kind="LOCAL",
        status="PENDING",
        staged_filename=staged_name,
        original_filename="ebook.pdf",
        file_size=staged_path.stat().st_size,
        checksum="deadbeef" * 8,
    )
    return {
        "artisan_user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
        "upload": upload,
        "staged_path": staged_path,
        "staged_name": staged_name,
    }


@pytest.fixture
def chain_with_pending_custom(db, django_user_model, vault_root):
    """
    Companion to chain_with_pending for the CUSTOM (order-product-
    scoped) approval path. Builds a CUSTOM product, an Order with a
    single OrderProduct line, and a pending ArtisanVaultUpload whose
    order_product FK is set.

    The variation is still populated on the upload (it always is —
    variation is a non-nullable FK), but the approve view will write
    OrderProduct.digital_file_path, not ProductVariation.digital_file_path,
    because upload.order_product_id is set.
    """
    from datetime import timedelta

    from django.utils import timezone

    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import (
        Product, ProductVariation, ArtisanVaultUpload,
    )
    from orders.models import Order, OrderProduct

    user = django_user_model.objects.create_user(
        username="custom_artisan",
        email="custom_artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user, display_name="Custom Approval Artisan",
        slug="custom-approval-artisan", is_verified=True,
    )
    category = Category.objects.create(
        category_name="Custom Approval Digital",
        slug="custom-approval-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Custom Approval Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
        is_physical=False,
        is_active=True,
        status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )

    customer = django_user_model.objects.create_user(
        username="custom_customer",
        email="custom_customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    order = Order.objects.create(
        user=customer,
        order_number="CUSTOM-APPROVAL-0001",
        email=customer.email,
        is_ordered=True,
        ordered_at=timezone.now(),
        order_status="Processing",
        product_total=Decimal("10.00"),
        total_due=Decimal("10.00"),
    )
    order_product = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=product,
        product_variation=variation,
        product_price=Decimal("10.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )

    staged_name = "custom-abc-123.pdf"
    staged_path = vault_root / "_pending" / staged_name
    staged_path.write_bytes(b"%PDF-1.4\n% custom approval test\n%%EOF\n")

    upload = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        order_product=order_product,
        storage_kind="LOCAL",
        status="PENDING",
        staged_filename=staged_name,
        original_filename="custom-ebook.pdf",
        file_size=staged_path.stat().st_size,
        checksum="cafebabe" * 8,
    )
    return {
        "artisan_user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
        "customer": customer,
        "order": order,
        "order_product": order_product,
        "upload": upload,
        "staged_path": staged_path,
        "staged_name": staged_name,
    }


def _url(upload):
    return reverse("review_vault_upload_approve", args=[upload.id])


# ──────────────────────────────────────────────────────────────────
# Gates
# ──────────────────────────────────────────────────────────────────

class TestGates:

    def test_unauthenticated_is_rejected(self, client, chain_with_pending):
        # superuser_required raises PermissionDenied for any non-superuser,
        # including anonymous. This matches the behaviour of the existing
        # product-review views in store/views.py — a 403, not a login
        # redirect. If that changes app-wide, this test and the sibling
        # product-review tests should change together.
        response = client.post(_url(chain_with_pending["upload"]))
        assert response.status_code == 403

    def test_regular_user_is_rejected(self, client, regular_user, chain_with_pending):
        client.force_login(regular_user)
        response = client.post(_url(chain_with_pending["upload"]))
        # superuser_required raises PermissionDenied -> 403
        assert response.status_code == 403

    def test_already_approved_is_noop(
        self, client, superuser, chain_with_pending,
    ):
        from store.models import ArtisanVaultUpload

        upload = chain_with_pending["upload"]
        upload.status = "APPROVED"
        upload.save(update_fields=["status"])

        client.force_login(superuser)
        response = client.post(_url(upload))
        assert response.status_code in (301, 302)

        upload.refresh_from_db()
        assert upload.status == "APPROVED"
        # File never moved.
        assert chain_with_pending["staged_path"].is_file()
        assert not (chain_with_pending["staged_path"].parent.parent
                    / upload.staged_filename).is_file()


# ──────────────────────────────────────────────────────────────────
# Happy path
# ──────────────────────────────────────────────────────────────────

class TestApproveHappyPath:

    def test_approve_moves_file_updates_pointer_and_logs(
        self, client, superuser, chain_with_pending, vault_root,
    ):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog

        chain = chain_with_pending
        upload = chain["upload"]
        variation = chain["variation"]
        staged_path = chain["staged_path"]

        client.force_login(superuser)
        response = client.post(_url(upload))
        assert response.status_code in (301, 302)

        # File moved out of _pending/ into the vault root.
        assert not staged_path.exists()
        new_path = vault_root / chain["staged_name"]
        assert new_path.is_file()
        assert new_path.read_bytes().startswith(b"%PDF-")

        # Pointer updated on the variation.
        variation.refresh_from_db()
        assert variation.digital_file_path == chain["staged_name"]

        # Upload flipped to APPROVED with reviewer metadata.
        upload.refresh_from_db()
        assert upload.status == "APPROVED"
        assert upload.reviewed_at is not None
        assert upload.reviewed_by == superuser

        # Review log written.
        log = VaultUploadReviewLog.objects.get(upload=upload)
        assert log.action == "approved"
        assert log.actor == superuser

    def test_approve_retires_previous_file(
        self, client, superuser, chain_with_pending, vault_root,
    ):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog

        chain = chain_with_pending
        variation = chain["variation"]

        # Simulate an already-live previous file.
        old_name = "old-version.pdf"
        old_path = vault_root / old_name
        old_path.write_bytes(b"%PDF-1.4\n% old\n%%EOF\n")
        variation.digital_file_path = old_name
        variation.save(update_fields=["digital_file_path"])

        client.force_login(superuser)
        client.post(_url(chain["upload"]))

        # Old file moved to _retired/, not deleted.
        assert not old_path.exists()
        retired_path = vault_root / "_retired" / old_name
        assert retired_path.is_file()
        assert retired_path.read_bytes() == b"%PDF-1.4\n% old\n%%EOF\n"

        # New file is the live one.
        assert (vault_root / chain["staged_name"]).is_file()
        variation.refresh_from_db()
        assert variation.digital_file_path == chain["staged_name"]


# ──────────────────────────────────────────────────────────────────
# Edge cases
# ──────────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_external_pending_is_rejected(
        self, client, superuser, chain_with_pending, vault_root,
    ):
        chain = chain_with_pending
        upload = chain["upload"]
        upload.storage_kind = "EXTERNAL_PENDING"
        upload.staged_filename = ""
        upload.save(update_fields=["storage_kind", "staged_filename"])

        client.force_login(superuser)
        response = client.post(_url(upload))
        assert response.status_code in (301, 302)

        upload.refresh_from_db()
        assert upload.status == "PENDING"

    def test_missing_staged_file_is_rejected(
        self, client, superuser, chain_with_pending, vault_root,
    ):
        chain = chain_with_pending
        chain["staged_path"].unlink()

        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        assert response.status_code in (301, 302)

        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "PENDING"
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path

    def test_compensating_rename_restores_file_on_db_failure(
        self, client, superuser, chain_with_pending, vault_root, monkeypatch,
    ):
        """
        Force a DB failure after the file has been moved. The view
        should rename the file back to _pending/ so the filesystem is
        unchanged and the transaction is a true no-op.
        """
        from store.models import ArtisanVaultUpload

        chain = chain_with_pending
        staged_path = chain["staged_path"]
        staged_name = chain["staged_name"]

        def boom(*args, **kwargs):
            raise RuntimeError("forced DB failure")

        monkeypatch.setattr(ArtisanVaultUpload, "save", boom)

        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        assert response.status_code in (301, 302)

        # File restored to _pending/, not left in the vault root.
        assert staged_path.is_file()
        assert not (vault_root / staged_name).is_file()

        # DB unchanged.
        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "PENDING"
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path


# ──────────────────────────────────────────────────────────────────
# CUSTOM (order-product-scoped) approval path
# ──────────────────────────────────────────────────────────────────

class TestApproveCustomOrderProduct:
    """
    Pins the order-product-scoped branch of review_vault_upload_approve:
    the file is promoted to OrderProduct.digital_file_path (not the
    variation's), the variation pointer is untouched, and
    issue_download_token is called on the order-product inside the
    atomic block.

    See store/views.py::review_vault_upload_approve and the CUSTOM
    pipeline v2 handoff.
    """

    def test_approve_writes_order_product_pointer_not_variation(
        self, client, superuser, chain_with_pending_custom, vault_root,
    ):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog
        from store.models import DigitalDownloadToken

        chain = chain_with_pending_custom
        upload = chain["upload"]
        order_product = chain["order_product"]
        variation = chain["variation"]
        staged_path = chain["staged_path"]

        # Pre-conditions: nothing is set yet, no token exists, line
        # not dispatched.
        assert order_product.digital_file_path is None or order_product.digital_file_path == ""
        assert variation.digital_file_path is None or variation.digital_file_path == ""
        assert order_product.is_dispatched is False
        assert order_product.dispatched_at is None
        assert DigitalDownloadToken.objects.filter(order_product=order_product).count() == 0

        client.force_login(superuser)
        response = client.post(_url(upload))
        assert response.status_code in (301, 302)

        # File moved out of _pending/ into the vault root.
        assert not staged_path.exists()
        new_path = vault_root / chain["staged_name"]
        assert new_path.is_file()
        assert new_path.read_bytes().startswith(b"%PDF-")

        # The order-product pointer was written.
        order_product.refresh_from_db()
        assert order_product.digital_file_path == chain["staged_name"]

        # The variation pointer was NOT touched — this is the load-
        # bearing assertion. If a future refactor drops the
        # is_order_product_scoped branch and unconditionally writes
        # variation.digital_file_path, this fails.
        variation.refresh_from_db()
        assert variation.digital_file_path is None or variation.digital_file_path == ""

        # The download token was issued for the order-product.
        token = DigitalDownloadToken.objects.get(order_product=order_product)
        # Token's user is the customer, not the artisan.
        assert token.user_id == chain["customer"].id
        assert token.email == chain["customer"].email
        # Token is fresh, not expired or revoked.
        assert token.is_revoked is False
        assert token.is_expired is False

        # The order-product was marked dispatched by the helper.
        assert order_product.is_dispatched is True
        assert order_product.dispatched_at is not None

        # Upload flipped to APPROVED with reviewer metadata.
        upload.refresh_from_db()
        assert upload.status == "APPROVED"
        assert upload.reviewed_at is not None
        assert upload.reviewed_by == superuser

        # Review log written.
        log = VaultUploadReviewLog.objects.get(upload=upload)
        assert log.action == "approved"
        assert log.actor == superuser


# ──────────────────────────────────────────────────────────────────
# Review-state guard — a variation-scoped upload cannot be approved
# against a product that is not Pending
# ──────────────────────────────────────────────────────────────────

class TestApproveRefusedOnNonPendingProduct:
    """
    The review-state guard added to review_vault_upload_approve.

    A variation-scoped upload can only be approved into a product that
    is currently Pending. Draft, Rejected, and Unpublished mean the
    product has not (or no longer) been submitted — the file cannot go
    live because the product cannot go live. Published means the file
    has already passed through review; a new upload against a Published
    product cannot be created through the view (the
    is_editable_by_artisan guard refuses it), but a stale edit page, a
    forged POST, or a legacy row could still present one.

    CUSTOM (order-product-scoped) rows are exempt: the product is
    Published by definition, the order line is already under
    fulfilment, and the review is against the file's suitability for
    that specific delivery. TestApproveCustomOrderProduct (above)
    covers the happy path for that scope; nothing here changes it.
    """

    def _set_product_status(self, chain, status_value):
        from store.models import Product
        Product.objects.filter(pk=chain["product"].pk).update(status=status_value)
        chain["product"].refresh_from_db()

    def _assert_refused(self, client, chain, response):
        from store.models import ArtisanVaultUpload
        from django.contrib.messages import get_messages

        assert response.status_code in (301, 302)
        # The staged file did not move.
        assert chain["staged_path"].is_file()
        # No new file appeared at the vault root.
        vault_file = chain["staged_path"].parent.parent / chain["staged_name"]
        assert not vault_file.is_file()
        # The row's status did not change.
        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "PENDING"
        # The variation pointer was not touched.
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path
        # The guard's message is what the reviewer saw.
        messages_list = [str(m) for m in get_messages(response.wsgi_request)]
        assert any("review state does not permit" in m for m in messages_list), (
            "The guard did not fire, or a different refusal reached the "
            "request first. messages were: " + repr(messages_list)
        )

    def test_refused_when_product_is_draft(
        self, client, superuser, chain_with_pending,
    ):
        chain = chain_with_pending
        self._set_product_status(chain, "Draft")
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        self._assert_refused(client, chain, response)

    def test_refused_when_product_is_rejected(
        self, client, superuser, chain_with_pending,
    ):
        chain = chain_with_pending
        self._set_product_status(chain, "Rejected")
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        self._assert_refused(client, chain, response)

    def test_refused_when_product_is_unpublished(
        self, client, superuser, chain_with_pending,
    ):
        chain = chain_with_pending
        self._set_product_status(chain, "Unpublished")
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        self._assert_refused(client, chain, response)

    def test_refused_when_product_is_published(
        self, client, superuser, chain_with_pending,
    ):
        """
        The state a forged POST or a stale edit page would present. A
        new upload against a Published product cannot be created
        through the view, but a legacy row or a forged POST could
        carry one; the guard closes that at approval time.
        """
        chain = chain_with_pending
        self._set_product_status(chain, "Published")
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        self._assert_refused(client, chain, response)

    def test_pending_product_still_approves(
        self, client, superuser, chain_with_pending,
    ):
        """
        Regression guard: the guard must not refuse the happy path.
        The fixture's product is already Pending; this test is the
        baseline the four refusal tests read against.
        """
        chain = chain_with_pending
        assert chain["product"].status == "Pending"
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        assert response.status_code in (301, 302)

        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "APPROVED"
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path == chain["staged_name"]

    def test_custom_row_is_exempt_from_the_guard(
        self, client, superuser, chain_with_pending_custom,
    ):
        """
        A CUSTOM row's product is Published by definition. The guard
        must not refuse it — otherwise every CUSTOM approval would
        fail, because no CUSTOM product is ever Pending.
        """
        chain = chain_with_pending_custom
        # Assert the premise: a CUSTOM product is Published.
        from store.models import Product
        product = Product.objects.get(pk=chain["product"].pk)
        assert product.status == "Published"

        client.force_login(superuser)
        response = client.post(_url(chain["upload"]))
        assert response.status_code in (301, 302)

        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "APPROVED"
        chain["order_product"].refresh_from_db()
        assert chain["order_product"].digital_file_path == chain["staged_name"]
        # The variation pointer was not touched — CUSTOM is order-scoped.
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path