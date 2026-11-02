# orders/tests/test_delivery_mode.py
"""
Tests for Order.delivery_mode — the property backing the ledger's
"Delivery Type" badge.

Five cases:

  1. CUSTOM-only → "custom".
  2. INSTANT-only → "instant".
  3. Mixed CUSTOM + INSTANT → "custom" (the whole order is still
     waiting on something; "auto-fulfilled" would be a lie for the
     CUSTOM part).
  4. Mixed physical + CUSTOM → "physical" (tracking is the more
     actionable signal on the ledger).
  5. Voucher-only → "voucher".

The property is also used by commit 3's escalation button and by the
future pre-purchase flow, so pinning its four branches here is worth
doing once, cleanly.
"""

import pytest
from django.contrib.auth import get_user_model

from category.models import Category
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation

Account = get_user_model()


@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="dm-customer",
        email="dm-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="DM Category",
        slug="dm-category",
    )


def _make_order(customer, number):
    return Order.objects.create(
        user=customer,
        email=customer.email,
        order_number=number,
        is_ordered=True,
        order_status="Processing",
    )


def _add_line(order, category, *, product_kind, line_no):
    """
    Creates a Product + ProductVariation + OrderProduct on `order`,
    with flags matching `product_kind`.

    `line_no` disambiguates product names/slugs when an order holds
    multiple lines; the tests below pass 1, 2, ... per order.
    """
    slug = f"dm-{product_kind}-{line_no}"
    flags = {"is_physical": False, "is_digital": False, "is_voucher": False}
    if product_kind == "physical":
        flags["is_physical"] = True
    elif product_kind == "custom":
        flags["is_digital"] = True
    elif product_kind == "instant":
        flags["is_digital"] = True
    elif product_kind == "voucher":
        flags["is_voucher"] = True
    else:
        raise ValueError(f"Unknown product_kind {product_kind!r}")

    kwargs = {
        "product_name": f"DM {product_kind.title()} {line_no}",
        "slug": slug,
        "category": category,
        "is_active": True,
        "status": "Published",
        **flags,
    }
    if product_kind == "custom":
        kwargs["digital_fulfillment_type"] = "CUSTOM"
    elif product_kind == "instant":
        kwargs["digital_fulfillment_type"] = "INSTANT"

    product = Product.objects.create(**kwargs)
    variation = ProductVariation.objects.create(
        product=product, price="10.00", stock=1,
    )
    return OrderProduct.objects.create(
        order=order, user=order.user,
        product=product, product_variation=variation,
        product_price="10.00", quantity=1, ordered=True,
    )


@pytest.mark.django_db
class TestOrderDeliveryMode:

    def test_custom_only_reports_custom(self, customer, category):
        order = _make_order(customer, "DM-ORDER-0001")
        _add_line(order, category, product_kind="custom", line_no=1)
        assert order.delivery_mode == "custom"

    def test_instant_only_reports_instant(self, customer, category):
        order = _make_order(customer, "DM-ORDER-0002")
        _add_line(order, category, product_kind="instant", line_no=1)
        assert order.delivery_mode == "instant"

    def test_mixed_custom_and_instant_reports_custom(self, customer, category):
        order = _make_order(customer, "DM-ORDER-0003")
        _add_line(order, category, product_kind="instant", line_no=1)
        _add_line(order, category, product_kind="custom", line_no=2)
        assert order.delivery_mode == "custom"

    def test_physical_wins_over_custom(self, customer, category):
        order = _make_order(customer, "DM-ORDER-0004")
        _add_line(order, category, product_kind="custom", line_no=1)
        _add_line(order, category, product_kind="physical", line_no=2)
        assert order.delivery_mode == "physical"

    def test_voucher_only_reports_voucher(self, customer, category):
        order = _make_order(customer, "DM-ORDER-0005")
        _add_line(order, category, product_kind="voucher", line_no=1)
        assert order.delivery_mode == "voucher"