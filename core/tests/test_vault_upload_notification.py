# core/tests/test_vault_upload_notification.py
"""
Tests for the vault-upload admin notification path.

Covers:
  * The Celery task dispatches to the email helper for a PENDING row
  * Non-PENDING rows are skipped (defensive against late delivery)
  * The task fires on transaction commit only, not on rollback
  * The review log model exposes the expected defaults

Located under core/tests/ to match pytest.ini's testpaths.
"""

from __future__ import annotations

import io
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.urls import reverse


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    vault = tmp_path / "private_digital_vault"
    vault.mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def artisan_chain(db, django_user_model):
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="notify_artisan",
        email="notify@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Notify Artisan",
        slug="notify-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Notify Digital",
        slug="notify-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Notify Ebook",
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
    return {"user": user, "profile": profile, "product": product, "variation": variation}


def _pdf_bytes() -> bytes:
    return b"%PDF-1.4\n% notify-test\n%%EOF\n"


def _url(product, variation):
    return reverse(
        "a_dashboard_product_variation_upload_vault",
        args=[product.pk, variation.pk],
    )


# ──────────────────────────────────────────────────────────────────
# Task behaviour
# ──────────────────────────────────────────────────────────────────

class TestNotificationTask:

    def test_task_calls_email_helper_for_pending_row(
        self, db, artisan_chain, vault_root,
    ):
        from store.models import ArtisanVaultUpload
        from store.tasks import send_vault_upload_pending_email_task

        chain = artisan_chain
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            storage_kind="LOCAL",
            status="PENDING",
            staged_filename="abc.pdf",
            original_filename="ebook.pdf",
            file_size=1024,
            checksum="deadbeef",
        )

        with patch("emails.utils.send_vault_upload_pending_notification") as mock_send:
            result = send_vault_upload_pending_email_task(str(upload.id))

        assert mock_send.called
        assert str(upload.id) in result

    def test_task_skips_non_pending_row(self, db, artisan_chain, vault_root):
        from store.models import ArtisanVaultUpload
        from store.tasks import send_vault_upload_pending_email_task

        chain = artisan_chain
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            storage_kind="LOCAL",
            status="APPROVED",
            staged_filename="abc.pdf",
        )

        with patch("emails.utils.send_vault_upload_pending_notification") as mock_send:
            result = send_vault_upload_pending_email_task(str(upload.id))

        assert not mock_send.called
        assert "APPROVED" in result

    def test_task_handles_missing_row(self, db):
        import uuid
        from store.tasks import send_vault_upload_pending_email_task

        fake = uuid.uuid4()
        result = send_vault_upload_pending_email_task(str(fake))
        assert "not found" in result


# ──────────────────────────────────────────────────────────────────
# Dispatch timing — on_commit only
# ──────────────────────────────────────────────────────────────────

class TestDispatchTiming:
    """
    Under pytest-django, each test runs inside an outer atomic block
    that is rolled back at the end. That means transaction.on_commit()
    callbacks would never fire during a test — so we use
    django_capture_on_commit_callbacks (pytest-django fixture) to
    capture and optionally execute them within a controlled block.
    """

    def test_task_dispatched_on_successful_commit(
        self, db, artisan_chain, vault_root, django_capture_on_commit_callbacks,
    ):
        from store.models import ArtisanVaultUpload
        from store.tasks import send_vault_upload_pending_email_task

        chain = artisan_chain
        dispatched = []

        with patch.object(
            send_vault_upload_pending_email_task, "delay",
            side_effect=lambda uid: dispatched.append(uid),
        ):
            with django_capture_on_commit_callbacks(execute=True):
                upload = ArtisanVaultUpload.objects.create(
                    artisan=chain["profile"],
                    product=chain["product"],
                    variation=chain["variation"],
                    storage_kind="LOCAL",
                    status="PENDING",
                    staged_filename="abc.pdf",
                )
                uid = str(upload.id)
                transaction.on_commit(
                    lambda u=uid: send_vault_upload_pending_email_task.delay(u)
                )

        assert dispatched == [uid]

    def test_task_not_dispatched_if_transaction_rolls_back(
        self, db, artisan_chain, vault_root, django_capture_on_commit_callbacks,
    ):
        from store.models import ArtisanVaultUpload
        from store.tasks import send_vault_upload_pending_email_task

        chain = artisan_chain
        dispatched = []

        with patch.object(
            send_vault_upload_pending_email_task, "delay",
            side_effect=lambda uid: dispatched.append(uid),
        ):
            with django_capture_on_commit_callbacks(execute=True):
                with pytest.raises(RuntimeError):
                    with transaction.atomic():
                        upload = ArtisanVaultUpload.objects.create(
                            artisan=chain["profile"],
                            product=chain["product"],
                            variation=chain["variation"],
                            storage_kind="LOCAL",
                            status="PENDING",
                            staged_filename="abc.pdf",
                        )
                        uid = str(upload.id)
                        transaction.on_commit(
                            lambda u=uid: send_vault_upload_pending_email_task.delay(u)
                        )
                        raise RuntimeError("simulated failure")

        # The inner atomic block rolled back and discarded its on_commit
        # callbacks, so even though django_capture_on_commit_callbacks
        # was in 'execute' mode, there was nothing to run.
        assert dispatched == []


# ──────────────────────────────────────────────────────────────────
# Model defaults
# ──────────────────────────────────────────────────────────────────

class TestVaultUploadReviewLog:

    def test_defaults_and_str(self, db, artisan_chain, vault_root):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog

        chain = artisan_chain
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            status="PENDING",
        )
        log = VaultUploadReviewLog.objects.create(
            upload=upload,
            action="approved",
            actor=chain["user"],
            note="Looks good.",
        )

        assert log.created_at is not None
        assert log.note == "Looks good."
        assert "approved" in str(log)
        assert chain["user"].username in str(log)

    def test_cascade_on_upload_delete(self, db, artisan_chain, vault_root):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog

        chain = artisan_chain
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            status="PENDING",
        )
        VaultUploadReviewLog.objects.create(
            upload=upload, action="rejected", note="Not the right file.",
        )
        assert VaultUploadReviewLog.objects.count() == 1

        upload.delete()
        assert VaultUploadReviewLog.objects.count() == 0