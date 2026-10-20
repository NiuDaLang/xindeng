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
        status="Published",
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

