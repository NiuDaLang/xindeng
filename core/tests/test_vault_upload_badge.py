# core/tests/test_vault_upload_badge.py
"""
Tests for the pending-vault-upload badge on the artisan product-edit page.

Covers:
  * ProductVariation.pending_vault_upload_count counts only PENDING rows
  * The product-edit view renders the badge when a pending upload exists
  * The badge is absent when there is no pending upload

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
def artisan_chain(db, django_user_model):
    """Artisan + digital product + one variation, ready to log in as."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="badge_artisan",
        email="badge@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Badge Artisan",
        slug="badge-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Badge Digital",
        slug="badge-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Badge Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",  # editable by artisan
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
    }


def _edit_url(product):
    return reverse("a_dashboard_product_edit", kwargs={"pk": product.pk})


# ──────────────────────────────────────────────────────────────────
# Model property — the source of truth the template reads
# ──────────────────────────────────────────────────────────────────

class TestPendingVaultUploadCount:

    def test_zero_when_no_uploads_exist(self, artisan_chain):
        assert artisan_chain["variation"].pending_vault_upload_count == 0

    def test_counts_a_single_pending_upload(self, artisan_chain):
        from store.models import ArtisanVaultUpload

        ArtisanVaultUpload.objects.create(
            artisan=artisan_chain["profile"],
            product=artisan_chain["product"],
            variation=artisan_chain["variation"],
            status="PENDING",
            staged_filename="a.pdf",
        )
        assert artisan_chain["variation"].pending_vault_upload_count == 1

    def test_ignores_approved_rejected_and_superseded(self, artisan_chain):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain

        # One of each non-PENDING status. These should never be counted.
        for status_value, name in (
            ("APPROVED", "a.pdf"),
            ("REJECTED", "b.pdf"),
            ("SUPERSEDED", "c.pdf"),
        ):
            ArtisanVaultUpload.objects.create(
                artisan=chain["profile"],
                product=chain["product"],
                variation=chain["variation"],
                status=status_value,
                staged_filename=name,
            )

        assert chain["variation"].pending_vault_upload_count == 0

        # Add one PENDING on top; count should be 1, not 4.
        ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            status="PENDING",
            staged_filename="d.pdf",
        )
        assert chain["variation"].pending_vault_upload_count == 1


# ──────────────────────────────────────────────────────────────────
# View — the badge shows up on the artisan's product-edit page
# ──────────────────────────────────────────────────────────────────

class TestBadgeOnProductEditPage:

    def test_badge_absent_when_no_pending_upload(self, client, artisan_chain):
        client.force_login(artisan_chain["user"])
        response = client.get(_edit_url(artisan_chain["product"]))

        assert response.status_code == 200
        assert "待審核檔案" not in response.content.decode()

    def test_badge_present_when_pending_upload_exists(self, client, artisan_chain):
        from store.models import ArtisanVaultUpload

        ArtisanVaultUpload.objects.create(
            artisan=artisan_chain["profile"],
            product=artisan_chain["product"],
            variation=artisan_chain["variation"],
            status="PENDING",
            staged_filename="pending.pdf",
        )
        client.force_login(artisan_chain["user"])
        response = client.get(_edit_url(artisan_chain["product"]))

        assert response.status_code == 200
        assert "待審核檔案" in response.content.decode()