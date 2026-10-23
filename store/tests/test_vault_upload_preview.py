# store/tests/test_vault_upload_preview.py
"""
Tests for the admin-side staged-file preview view.

Two behaviours are pinned here:
  1. ZIP and EPUB uploads force a download (attachment disposition) —
     no browser can render them natively, so inline would be a blank
     tab.
  2. PDF uploads stream inline — the reviewer reads the file in the
     tab and closes it.

The auth gate is covered by the third test; the existing
@superuser_required behaviour (403 for authenticated non-superusers)
is not re-implemented, only asserted.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@pytest.fixture
def pending_upload(db, django_user_model):
    """A PENDING upload with a real file on disk under the test vault root."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import ArtisanVaultUpload, Product, ProductVariation
    from django.conf import settings

    pending = Path(settings.XINDENG_VAULT_ROOT) / "_pending"
    pending.mkdir(parents=True, exist_ok=True)

    artisan_user = django_user_model.objects.create_user(
        username="prev_artisan",
        email="prev-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Preview Artisan",
        slug="preview-artisan",
        is_verified=True,
    )
    cat = Category.objects.create(
        category_name="Preview Cat",
        slug="preview-cat",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Preview Product",
        category=cat,
        creator=profile,
        is_physical=False,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
        is_active=True,
        status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product, price=10, stock=1, is_available=True,
    )
    (pending / "abc.zip").write_bytes(b"PK\x03\x04fakezip")
    upload = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        status="PENDING",
        storage_kind="LOCAL",
        staged_filename="abc.zip",
        original_filename="art.zip",
        file_size=11,
        checksum="a" * 64,
    )
    return upload


@pytest.fixture
def superuser_client(client, django_user_model):
    su = django_user_model.objects.create_superuser(
        email="su-prev@example.com", username="su-prev", password="x",
    )
    client.force_login(su)
    return client


def test_zip_preview_forces_attachment(
    superuser_client, pending_upload,
):
    url = reverse("review_vault_upload_preview", args=[pending_upload.id])
    response = superuser_client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/zip")
    assert response["Content-Disposition"].startswith("attachment;")
    assert 'filename="art.zip"' in response["Content-Disposition"]


def test_pdf_preview_streams_inline(
    superuser_client, pending_upload,
):
    from django.conf import settings
    pending = Path(settings.XINDENG_VAULT_ROOT) / "_pending"
    (pending / "abc.pdf").write_bytes(b"%PDF-1.4 x")
    pending_upload.staged_filename = "abc.pdf"
    pending_upload.original_filename = "art.pdf"
    pending_upload.save(update_fields=["staged_filename", "original_filename"])

    url = reverse("review_vault_upload_preview", args=[pending_upload.id])
    response = superuser_client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"].startswith("inline;")


def test_preview_403_for_non_superuser(
    client, pending_upload, django_user_model,
):
    non_su = django_user_model.objects.create_user(
        username="non-su-prev",
        email="non-su-prev@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    client.force_login(non_su)
    url = reverse("review_vault_upload_preview", args=[pending_upload.id])
    response = client.get(url)
    # superuser_required returns 403 for authenticated non-superusers.
    assert response.status_code == 403