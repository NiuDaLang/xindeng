# core/tests/test_vault_upload_rejection.py
"""
Tests for review_vault_upload_reject.

Covers gates (superuser, PENDING-only, note-required), the happy path
(file deleted on commit, status flipped, log written with the note),
external pending handling, and the on_commit dispatch of the artisan
notification email.

Located under core/tests/ to match pytest.ini's testpaths.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


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
def superuser(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="superu",
        email="superu@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    user.is_superadmin = True
    user.is_staff = True
    user.save(update_fields=["is_superadmin", "is_staff"])
    return user


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
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation, ArtisanVaultUpload

    user = django_user_model.objects.create_user(
        username="reject_artisan",
        email="reject-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user, display_name="Reject Artisan",
        slug="reject-artisan", is_verified=True,
    )
    category = Category.objects.create(
        category_name="Reject Digital",
        slug="reject-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Reject Ebook",
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

    staged_name = "reject-abc.pdf"
    staged_path = vault_root / "_pending" / staged_name
    staged_path.write_bytes(b"%PDF-1.4\n% reject test\n%%EOF\n")

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
    return reverse("review_vault_upload_reject", args=[upload.id])


# ──────────────────────────────────────────────────────────────────
# Gates
# ──────────────────────────────────────────────────────────────────

class TestGates:

    def test_unauthenticated_is_rejected(self, client, chain_with_pending):
        response = client.post(_url(chain_with_pending["upload"]), {"note": "x"})
        assert response.status_code == 403

    def test_regular_user_is_rejected(self, client, regular_user, chain_with_pending):
        client.force_login(regular_user)
        response = client.post(_url(chain_with_pending["upload"]), {"note": "x"})
        assert response.status_code == 403

    def test_already_approved_is_noop(
        self, client, superuser, chain_with_pending,
    ):
        upload = chain_with_pending["upload"]
        upload.status = "APPROVED"
        upload.save(update_fields=["status"])

        client.force_login(superuser)
        response = client.post(_url(upload), {"note": "reject-after-approve"})
        assert response.status_code in (301, 302)

        upload.refresh_from_db()
        assert upload.status == "APPROVED"
        # File untouched.
        assert chain_with_pending["staged_path"].is_file()

    def test_missing_note_is_rejected(self, client, superuser, chain_with_pending):
        chain = chain_with_pending
        client.force_login(superuser)
        response = client.post(_url(chain["upload"]), {"note": "   "})
        assert response.status_code in (301, 302)

        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "PENDING"
        # File untouched.
        assert chain["staged_path"].is_file()


# ──────────────────────────────────────────────────────────────────
# Happy path
# ──────────────────────────────────────────────────────────────────

class TestRejectHappyPath:

    def test_reject_deletes_file_updates_status_and_logs(
        self, client, superuser, chain_with_pending, vault_root,
        django_capture_on_commit_callbacks, monkeypatch,
    ):
        from store.models import ArtisanVaultUpload, VaultUploadReviewLog
        from store.tasks import send_vault_upload_rejected_email_task

        # The view registers two on_commit callbacks: the file delete
        # and the email dispatch. We're testing the delete here, so
        # neutralise the email side to keep the test hermetic.
        monkeypatch.setattr(
            send_vault_upload_rejected_email_task, "delay",
            lambda uid: None,
        )

        chain = chain_with_pending
        upload = chain["upload"]
        staged_path = chain["staged_path"]

        client.force_login(superuser)
        # django_capture_on_commit_callbacks(execute=True) runs any
        # on_commit callbacks registered inside the block when the
        # block exits. Without this, pytest-django's outer transaction
        # never commits and the callbacks are silently dropped.
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                _url(upload),
                {"note": "Corrupt PDF — please re-export and try again."},
            )
        assert response.status_code in (301, 302)

        # File gone — the on_commit deletion ran.
        assert not staged_path.exists()

        # Upload flipped to REJECTED with reviewer metadata and note.
        upload.refresh_from_db()
        assert upload.status == "REJECTED"
        assert upload.reviewed_at is not None
        assert upload.reviewed_by == superuser
        assert upload.review_note == "Corrupt PDF — please re-export and try again."

        # Review log written with the same note.
        log = VaultUploadReviewLog.objects.get(upload=upload)
        assert log.action == "rejected"
        assert log.actor == superuser
        assert log.note == "Corrupt PDF — please re-export and try again."

        # No pointer was set on the variation (reject does not promote).
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path

    def test_external_pending_rejection_works_without_a_file(
        self, client, superuser, chain_with_pending, vault_root,
    ):
        from store.models import VaultUploadReviewLog

        chain = chain_with_pending
        upload = chain["upload"]
        upload.storage_kind = "EXTERNAL_PENDING"
        upload.staged_filename = ""
        upload.external_url = "https://example.com/file.pdf"
        upload.save(update_fields=["storage_kind", "staged_filename", "external_url"])

        client.force_login(superuser)
        response = client.post(_url(upload), {"note": "Link broken."})
        assert response.status_code in (301, 302)

        upload.refresh_from_db()
        assert upload.status == "REJECTED"
        assert upload.review_note == "Link broken."
        assert VaultUploadReviewLog.objects.filter(
            upload=upload, action="rejected",
        ).exists()


# ──────────────────────────────────────────────────────────────────
# Email dispatch
# ──────────────────────────────────────────────────────────────────

class TestEmailDispatch:

    def test_email_task_dispatched_on_commit(
        self, client, superuser, chain_with_pending,
        django_capture_on_commit_callbacks, monkeypatch,
    ):
        from store.tasks import send_vault_upload_rejected_email_task

        chain = chain_with_pending
        dispatched = []

        monkeypatch.setattr(
            send_vault_upload_rejected_email_task, "delay",
            lambda uid: dispatched.append(uid),
        )

        client.force_login(superuser)
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                _url(chain["upload"]), {"note": "Wrong edition."},
            )
        assert response.status_code in (301, 302)

        assert dispatched == [str(chain["upload"].id)]

    def test_email_task_skips_non_rejected_row(self, db):
        """
        The task itself short-circuits if the row's status has moved
        on — e.g. the artisan re-uploaded before the worker came back
        online and this stale task finally ran.
        """
        from store.tasks import send_vault_upload_rejected_email_task

        # Create a minimal APPROVED row by hand using the same fixture
        # family. Reusing chain_with_pending would couple this test to
        # the client; we want a pure task test.
        from category.models import Category
        from creators.models import CreatorProfile
        from store.models import Product, ProductVariation, ArtisanVaultUpload
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(
            username="task_only", email="task-only@example.com",
            receive_newsletter=False, password="x", is_active=True,
        )
        profile = CreatorProfile.objects.create(
            user=user, display_name="Task Only", slug="task-only",
            is_verified=True,
        )
        category = Category.objects.create(
            category_name="Task Cat", slug="task-cat",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name="Task Book", category=category, creator=profile,
            is_digital=True, digital_fulfillment_type="INSTANT",
            is_physical=False, is_active=True, status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product, price=Decimal("10.00"),
            stock=1, is_available=True,
        )
        upload = ArtisanVaultUpload.objects.create(
            artisan=profile, product=product, variation=variation,
            status="APPROVED", staged_filename="x.pdf",
        )

        result = send_vault_upload_rejected_email_task(str(upload.id))
        assert "not REJECTED" in result