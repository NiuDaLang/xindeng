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
from django.contrib.auth import get_user_model


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


# ──────────────────────────────────────────────────────────────────
# Product-level aggregate — the source of truth for both new badges
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def two_variation_chain(db, django_user_model):
    """
    Same shape as artisan_chain, but with two variations on one
    product. This is the fixture that distinguishes the aggregate
    (per product) from the per-variation property: a test that
    accidentally reads the wrong one still passes with a single
    variation, but fails here.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="badge_artisan_two",
        email="badge-two@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Badge Artisan Two",
        slug="badge-artisan-two",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Badge Digital Two",
        slug="badge-digital-two",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Badge Ebook Two",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",
    )
    variation_a = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    variation_b = ProductVariation.objects.create(
        product=product,
        price=Decimal("12.00"),
        stock=1,
        is_available=True,
    )
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation_a": variation_a,
        "variation_b": variation_b,
    }


def _make_pending(chain, variation, name):
    from store.models import ArtisanVaultUpload
    return ArtisanVaultUpload.objects.create(
        artisan=chain["profile"],
        product=chain["product"],
        variation=variation,
        status="PENDING",
        staged_filename=name,
    )


class TestProductPendingVaultUploadCount:
    """
    Product.pending_vault_upload_count aggregates across variations.

    The per-variation property is covered above. This class exists to
    pin the aggregate's behaviour at the product level, and specifically
    to catch a future "simplification" that swaps the aggregate for a
    .first() / .exists() / single-variation read — every test here uses
    two variations where possible, so a wrong implementation cannot
    accidentally pass.
    """

    def test_zero_when_product_has_no_variations(self, db, django_user_model):
        from category.models import Category
        from creators.models import CreatorProfile
        from store.models import Product

        user = django_user_model.objects.create_user(
            username="badge_empty",
            email="badge-empty@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        profile = CreatorProfile.objects.create(
            user=user,
            display_name="Badge Empty",
            slug="badge-empty",
            is_verified=True,
        )
        category = Category.objects.create(
            category_name="Badge Empty Cat",
            slug="badge-empty-cat",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name="Badge Empty Ebook",
            category=category,
            creator=profile,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_active=True,
            status="Draft",
        )

        assert product.pending_vault_upload_count == 0

    def test_zero_when_only_terminal_states_exist(self, two_variation_chain):
        from store.models import ArtisanVaultUpload

        chain = two_variation_chain
        for status_value, name, variation in (
            ("APPROVED", "a.pdf", chain["variation_a"]),
            ("REJECTED", "b.pdf", chain["variation_b"]),
        ):
            ArtisanVaultUpload.objects.create(
                artisan=chain["profile"],
                product=chain["product"],
                variation=variation,
                status=status_value,
                staged_filename=name,
            )

        assert chain["product"].pending_vault_upload_count == 0

    def test_counts_across_two_variations(self, two_variation_chain):
        chain = two_variation_chain
        _make_pending(chain, chain["variation_a"], "a.pdf")
        _make_pending(chain, chain["variation_b"], "b.pdf")

        # The per-variation property returns 1 on either side; the
        # aggregate must return 2. This is the assertion that fails if
        # the aggregate is accidentally wired to the per-variation
        # property.
        assert chain["variation_a"].pending_vault_upload_count == 1
        assert chain["variation_b"].pending_vault_upload_count == 1
        assert chain["product"].pending_vault_upload_count == 2

    def test_one_pending_one_none_returns_one(self, two_variation_chain):
        chain = two_variation_chain
        _make_pending(chain, chain["variation_a"], "a.pdf")
        # variation_b deliberately has no upload.

        assert chain["product"].pending_vault_upload_count == 1

    def test_supersession_does_not_inflate_count(self, two_variation_chain):
        """
        Artisan re-uploads while the admin hasn't reviewed yet. The old
        row is flipped to SUPERSEDED and a fresh PENDING row is created.
        The aggregate must remain 1 — a naive filter that forgot to
        exclude SUPERSEDED would return 2.
        """
        from store.models import ArtisanVaultUpload

        chain = two_variation_chain
        first = _make_pending(chain, chain["variation_a"], "first.pdf")
        first.status = "SUPERSEDED"
        first.save(update_fields=["status"])
        _make_pending(chain, chain["variation_a"], "second.pdf")

        assert chain["product"].pending_vault_upload_count == 1

    def test_approval_decrements_count(self, two_variation_chain):
        chain = two_variation_chain
        pending = _make_pending(chain, chain["variation_a"], "a.pdf")
        assert chain["product"].pending_vault_upload_count == 1

        pending.status = "APPROVED"
        pending.save(update_fields=["status"])

        assert chain["product"].pending_vault_upload_count == 0


# ──────────────────────────────────────────────────────────────────
# Aggregate badge — products list page
# ──────────────────────────────────────────────────────────────────

class TestAggregateBadgeOnProductsListPage:

    def test_absent_when_no_pending_upload(self, client, two_variation_chain):
        client.force_login(two_variation_chain["user"])
        response = client.get(reverse("a_dashboard_products"))

        assert response.status_code == 200
        body = response.content.decode()
        # The per-variation badge text must not appear on the list page
        # at all — this page only knows about products, not variations.
        assert "待審核檔案" not in body
        # The aggregate badge text is what we're guarding. It should
        # not be present when the count is zero.
        assert "待審檔案" not in body

    def test_present_when_pending_upload_exists(self, client, two_variation_chain):
        chain = two_variation_chain
        _make_pending(chain, chain["variation_a"], "a.pdf")

        client.force_login(chain["user"])
        response = client.get(reverse("a_dashboard_products"))

        assert response.status_code == 200
        assert "待審檔案 1" in response.content.decode()

    def test_renders_the_aggregate_count_not_one(self, client, two_variation_chain):
        """
        Two variations, one PENDING each. The list page must render 2,
        not 1. This is the template-level counterpart to
        test_counts_across_two_variations.
        """
        chain = two_variation_chain
        _make_pending(chain, chain["variation_a"], "a.pdf")
        _make_pending(chain, chain["variation_b"], "b.pdf")

        client.force_login(chain["user"])
        response = client.get(reverse("a_dashboard_products"))

        assert response.status_code == 200
        body = response.content.decode()
        # Loose assertion: the label and the digit both appear. Exact
        # HTML formatting is deliberately not pinned so a markup
        # tweak doesn't churn the test.
        # assert "待審檔案" in body
        # assert "2" in body
        assert "待審檔案 2" in body


# ──────────────────────────────────────────────────────────────────
# Aggregate badge — product edit page header
# ──────────────────────────────────────────────────────────────────

class TestAggregateBadgeOnEditPageHeader:
    """
    The edit page renders BOTH the per-variation badges (on the cards)
    and the product-level aggregate (in the page header). These tests
    guard the header specifically, so a future change that removes the
    header badge while leaving the card badges does not pass silently.
    """

    def test_header_absent_when_no_pending_upload(self, client, artisan_chain):
        client.force_login(artisan_chain["user"])
        response = client.get(_edit_url(artisan_chain["product"]))

        assert response.status_code == 200
        assert "待審檔案" not in response.content.decode()

    def test_header_present_when_pending_upload_exists(self, client, artisan_chain):
        chain = artisan_chain
        from store.models import ArtisanVaultUpload
        ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["product"],
            variation=chain["variation"],
            status="PENDING",
            staged_filename="a.pdf",
        )

        client.force_login(chain["user"])
        response = client.get(_edit_url(chain["product"]))

        assert response.status_code == 200
        assert "待審檔案 1" in response.content.decode()