# store/tests/test_vault_upload_draft_status.py
"""
Tests for the DRAFT status on ArtisanVaultUpload.

This file opens with the two draft_staged_count properties only. The
status itself is added to STATUS_CHOICES in the same commit, but no
code path creates a DRAFT row yet — the promotion lives in the
submit/withdraw views, which are a later commit. Testing the counters
first pins the read side before the write side exists, so a later
change to the promotion cannot silently break the badge.

Mirrors test_vault_upload_badge.py's shape, including the
two-variation fixture, so the aggregate (Product) and the
per-variation (ProductVariation) counters are distinguished from the
first test rather than retrofitted.
"""

from __future__ import annotations

from decimal import Decimal

import pytest


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def artisan_chain(db, django_user_model):
    """Artisan + digital product + one variation, Draft status."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="draft_artisan",
        email="draft@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Draft Artisan",
        slug="draft-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Draft Digital",
        slug="draft-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Draft Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",
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


@pytest.fixture
def two_variation_chain(db, django_user_model):
    """
    Same shape as artisan_chain, but with two variations on one product.

    This is the fixture that distinguishes the aggregate from the
    per-variation property: a test that accidentally reads the wrong
    one still passes with a single variation, but fails here.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="draft_artisan_two",
        email="draft-two@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Draft Artisan Two",
        slug="draft-artisan-two",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Draft Digital Two",
        slug="draft-digital-two",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Draft Ebook Two",
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


def _make_upload(chain, variation, *, status_value, name):
    from store.models import ArtisanVaultUpload
    return ArtisanVaultUpload.objects.create(
        artisan=chain["profile"],
        product=chain["product"],
        variation=variation,
        status=status_value,
        staged_filename=name,
    )


# ──────────────────────────────────────────────────────────────────
# DRAFT is accepted by the model
# ──────────────────────────────────────────────────────────────────

class TestDraftStatusAccepted:

    def test_draft_is_a_valid_status(self, artisan_chain):
        """
        The choices tuple is the model-level contract. A row can be
        created with status=DRAFT and reads back as DRAFT. Full_clean
        is not called; Model.save() does not validate choices, so this
        test proves the choice exists (the constant), not that the
        field rejects other values.
        """
        from store.models import ArtisanVaultUpload

        assert "DRAFT" in dict(ArtisanVaultUpload.STATUS_CHOICES)

        upload = _make_upload(
            artisan_chain, artisan_chain["variation"],
            status_value="DRAFT", name="draft.pdf",
        )
        upload.refresh_from_db()
        assert upload.status == "DRAFT"

    def test_existing_statuses_unchanged(self):
        """
        Regression guard: adding DRAFT must not have reordered or
        renamed the other four choices. The admin and the review
        queue depend on PENDING's label.
        """
        from store.models import ArtisanVaultUpload

        choices = dict(ArtisanVaultUpload.STATUS_CHOICES)
        assert choices["PENDING"] == "Pending review"
        assert choices["APPROVED"] == "Approved"
        assert choices["REJECTED"] == "Rejected by admin"
        assert choices["SUPERSEDED"] == "Superseded by newer upload"


# ──────────────────────────────────────────────────────────────────
# Per-variation counter
# ──────────────────────────────────────────────────────────────────

class TestVariationDraftStagedCount:

    def test_zero_when_no_uploads_exist(self, artisan_chain):
        assert artisan_chain["variation"].draft_staged_count == 0

    def test_counts_a_single_draft_upload(self, artisan_chain):
        _make_upload(
            artisan_chain, artisan_chain["variation"],
            status_value="DRAFT", name="d.pdf",
        )
        assert artisan_chain["variation"].draft_staged_count == 1

    def test_ignores_the_other_statuses(self, artisan_chain):
        chain = artisan_chain
        v = chain["variation"]

        # One of each non-DRAFT status. PENDING is created then flipped
        # to APPROVED / REJECTED / SUPERSEDED so the partial unique
        # constraint is not violated mid-test.
        pending = _make_upload(chain, v, status_value="PENDING", name="p.pdf")
        approved = _make_upload(chain, v, status_value="APPROVED", name="a.pdf")
        rejected = _make_upload(chain, v, status_value="REJECTED", name="r.pdf")
        superseded = _make_upload(chain, v, status_value="SUPERSEDED", name="s.pdf")

        # No DRAFT rows yet.
        assert v.draft_staged_count == 0

        _make_upload(chain, v, status_value="DRAFT", name="d.pdf")

        # Still exactly 1, not 5.
        assert v.draft_staged_count == 1


# ──────────────────────────────────────────────────────────────────
# Product aggregate counter
# ──────────────────────────────────────────────────────────────────

class TestProductDraftStagedCount:

    def test_zero_when_no_uploads_exist(self, two_variation_chain):
        assert two_variation_chain["product"].draft_staged_count == 0

    def test_counts_across_two_variations(self, two_variation_chain):
        """
        The aggregate must sum across variations. A wrong
        implementation that reads a single variation's counter
        returns 1 here and fails.
        """
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        _make_upload(chain, chain["variation_b"], status_value="DRAFT", name="b.pdf")

        assert chain["variation_a"].draft_staged_count == 1
        assert chain["variation_b"].draft_staged_count == 1
        assert chain["product"].draft_staged_count == 2

    def test_one_draft_one_none_returns_one(self, two_variation_chain):
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        # variation_b deliberately has no upload.

        assert chain["product"].draft_staged_count == 1

    def test_pending_rows_do_not_leak_into_draft_count(self, two_variation_chain):
        """
        Comparison-shaped: the two counters are disjoint. A product
        with one DRAFT and one PENDING row has draft_staged_count == 1
        and pending_vault_upload_count == 1, not 2 and 2.
        """
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        _make_upload(chain, chain["variation_b"], status_value="PENDING", name="b.pdf")

        assert chain["product"].draft_staged_count == 1
        assert chain["product"].pending_vault_upload_count == 1

    def test_promotion_decrements_draft_count(self, two_variation_chain):
        """
        A DRAFT row flipped to PENDING leaves the DRAFT count and
        enters the PENDING count. No promotion code exists yet, so
        this flips the status by hand — the point is to pin that the
        two counters read the same row in exactly one of them at a
        time, which is the invariant the promotion will rely on.
        """
        chain = two_variation_chain
        pending = _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        assert chain["product"].draft_staged_count == 1
        assert chain["product"].pending_vault_upload_count == 0

        pending.status = "PENDING"
        pending.save(update_fields=["status"])

        assert chain["product"].draft_staged_count == 0
        assert chain["product"].pending_vault_upload_count == 1