# store/tests/test_product_manager_status_filter.py
"""
Tests for the status="Published" filter on ProductManager.

Commit B closes the state-leak: Draft / Pending / Rejected /
Unpublished products were reaching the storefront because the
manager's availability methods only constrained is_active and
is_deleted. Nine manager methods and one view are covered here; each
test asserts two things:

  * A Published product with an available variation IS returned.
  * Products in Draft, Pending, Rejected, and Unpublished are NOT.

The second assertion is parametrised over the four non-Published
statuses so a future edit that narrows to only one of them fails
loudly rather than passing silently.

filter_products is included because it builds its own queryset and
does not route through any of the manager methods; the leak existed
there too and would not have been closed by the manager-only change.

Test conventions match test_vault_upload_badge.py and test_hs_code.py:
fixtures are inline; Account.create_user requires receive_newsletter
as a positional arg (see tests/README.md and handoff rule 21).
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


# ──────────────────────────────────────────────────────────────────
# Factory fixture — fresh Category + Product + Variation per call
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def make_product(db, django_user_model):
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    _counter = {"n": 0}

    def _make(
        *,
        status="Published",
        category=None,
        category_slug=None,
        category_format="e-product",
        color="DEFAULT",
        variation_stock=1,
        variation_price=Decimal("10.00"),
        tags=None,
    ):
        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"pmf_artisan_{n}",
            email=f"pmf-artisan-{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        profile = CreatorProfile.objects.create(
            user=user,
            display_name=f"PMF Artisan {n}",
            slug=f"pmf-artisan-{n}",
            is_verified=True,
        )
        if category is None:
            category = Category.objects.create(
                category_name=f"PMF Cat {n}",
                slug=category_slug or f"pmf-cat-{n}",
                product_format=category_format,
            )
        product = Product.objects.create(
            product_name=f"PMF Product {n}",
            category=category,
            creator=profile,
            is_digital=(category.product_format == "e-product"),
            is_physical=(category.product_format == "physical"),
            digital_fulfillment_type="INSTANT",
            is_active=True,
            status=status,
            color=color,
        )
        if tags:
            product.tags.add(*tags)

        variation = ProductVariation.objects.create(
            product=product,
            price=variation_price,
            stock=variation_stock,
            is_available=True,
        )
        return {
            "user": user,
            "profile": profile,
            "category": category,
            "product": product,
            "variation": variation,
        }

    return _make

NON_PUBLISHED_STATUSES = ["Draft", "Pending", "Rejected", "Unpublished"]


# ──────────────────────────────────────────────────────────────────
# Helper — the include/exclude assertion pair
# ──────────────────────────────────────────────────────────────────

def _assert_published_included_and_others_excluded(make_product, call):
    """
    `call` is a zero-arg function returning the queryset under test.
    Each of the five products (Published + four non-Published) is
    built with identical conditions except status, so any difference
    in the queryset is attributable to status alone.
    """
    from store.models import Product

    published = make_product(status="Published")
    _ = published  # not returned; only the ids matter

    excluded_chains = [
        make_product(status=s) for s in NON_PUBLISHED_STATUSES
    ]

    result_ids = set(call().values_list("pk", flat=True))

    assert published["product"].pk in result_ids, (
        "Published product should have been returned. "
        "The status filter is too strict or misnamed."
    )
    for chain, status_value in zip(excluded_chains, NON_PUBLISHED_STATUSES):
        assert chain["product"].pk not in result_ids, (
            f"{status_value} product leaked into the queryset. "
            "The status filter is missing or too loose."
        )


# ──────────────────────────────────────────────────────────────────
# The nine manager methods
# ──────────────────────────────────────────────────────────────────

class TestAllAvailable:

    def test_status_filter(self, make_product):
        from store.models import Product, ProductVariation
        _assert_published_included_and_others_excluded(
            make_product,
            lambda: Product.products.all_available(variation_model=ProductVariation),
        )


class TestAllAvailableWithStock:

    def test_status_filter(self, make_product):
        from store.models import Product
        # variation_stock=1 ensures the stock>0 branch does not mask
        # the status assertion.
        _assert_published_included_and_others_excluded(
            make_product,
            lambda: Product.products.all_available_with_stock(),
        )


class TestAvailableByCategory:

    def test_status_filter(self, make_product):
        from category.models import Category
        from store.models import Product, ProductVariation

        category = Category.objects.create(
            category_name="PMF Shared Cat",
            slug="pmf-shared-cat",
            product_format="e-product",
        )

        def build(status):
            return make_product(status=status, category=category)

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_by_category(category_slug="pmf-shared-cat", variation_model=ProductVariation)
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_by_category"
            )


class TestAvailableByCategoryWithStock:

    def test_status_filter(self, make_product):
        from category.models import Category
        from store.models import Product

        category = Category.objects.create(
            category_name="PMF Shared Cat Stock",
            slug="pmf-shared-cat-stock",
            product_format="e-product",
        )

        def build(status):
            return make_product(status=status, category=category, variation_stock=1)

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_by_category_with_stock(category_slug="pmf-shared-cat-stock")
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_by_category_with_stock"
            )


class TestAvailableByCategoryFormat:

    def test_status_filter(self, make_product):
        from store.models import Product
        fmt = "e-product"

        def build(status):
            return make_product(status=status, category_format=fmt)

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_by_category_format(category_slug=fmt)
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_by_category_format"
            )


class TestAvailableByCategoryFormatWithStock:

    def test_status_filter(self, make_product):
        from store.models import Product
        fmt = "physical"

        def build(status):
            return make_product(
                status=status, category_format=fmt, variation_stock=1,
            )

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_by_category_format_with_stock(category_slug=fmt)
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_by_category_format_with_stock"
            )


class TestAvailableByColor:

    def test_status_filter(self, make_product):
        from store.models import Product
        color = "RED"

        def build(status):
            return make_product(status=status, color=color)

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_by_color(color=color)
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_by_color"
            )


class TestAvailableWithTags:

    def test_status_filter(self, make_product):
        from store.models import Product
        from taggit.models import Tag
        tag = Tag.objects.create(name="pmf-tag-1")

        def build(status):
            return make_product(status=status, tags=[tag])

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_with_tags(tags_ids=[tag.id])
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_with_tags"
            )


class TestAvailableWithinPriceRange:

    def test_status_filter(self, make_product):
        from store.models import Product
        price_cap = Decimal("20.00")

        def build(status):
            return make_product(status=status, variation_price=Decimal("10.00"))

        published = build("Published")
        excluded = [build(s) for s in NON_PUBLISHED_STATUSES]

        result_ids = set(
            Product.products
            .available_within_price_range(price=price_cap)
            .values_list("pk", flat=True)
        )
        assert published["product"].pk in result_ids
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].pk not in result_ids, (
                f"{status_value} product leaked into available_within_price_range"
            )


# ──────────────────────────────────────────────────────────────────
# filter_products view — builds its own queryset
# ──────────────────────────────────────────────────────────────────

class TestFilterProductsView:

    def test_status_filter(self, client, make_product):
        from category.models import Category
        from store.models import Product

        category = Category.objects.create(
            category_name="PMF Filter Cat",
            slug="pmf-filter-cat",
            product_format="e-product",
        )

        published = make_product(status="Published", category=category)
        excluded = [
            make_product(status=s, category=category)
            for s in NON_PUBLISHED_STATUSES
        ]
        soft_deleted = make_product(status="Published", category=category)
        Product.objects.filter(pk=soft_deleted["product"].pk).update(is_deleted=True)

        url = reverse("filter_products") + "?category=pmf-filter-cat"
        response = client.get(url)

        assert response.status_code == 200
        payload = response.json()
        assert "filtered_products_json" in payload
        returned_names = {p["product_name"] for p in payload["filtered_products_json"]}
        assert published["product"].product_name in returned_names
        for chain, status_value in zip(excluded, NON_PUBLISHED_STATUSES):
            assert chain["product"].product_name not in returned_names, (
                f"{status_value} product leaked into filter_products"
            )
        assert soft_deleted["product"].product_name not in returned_names, (
            "Soft-deleted Published product leaked into filter_products"
        )
