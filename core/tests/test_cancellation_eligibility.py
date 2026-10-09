# core/tests/test_cancellation_eligibility.py
"""
Eligibility-rule tests for Order.evaluate_cancellation_details and
Order.can_be_cancelled_online.

These are the customer-facing rules. They are deliberately bypassed by
OrderAdmin.save_model, which lets support staff process refunds on
orders that self-service would refuse.

Located under core/tests/ only because pytest.ini sets
testpaths = core/tests. Consider moving to orders/tests/ in a future
session alongside a pytest.ini update.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────
# Order factory
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def build_order(db, django_user_model):
    """
    Builds an Order with one or more OrderProduct lines.

    lines: list of dicts, each with keys:
        product_kind: 'digital_instant' | 'digital_custom'
                    | 'physical' | 'voucher'
        is_claimed: bool (default False) — digital lines only
        is_dispatched: bool (default False) — physical lines only
        is_partially_used: bool (default False) — voucher lines only
        price: Decimal (default 10.00)

    Order-level kwargs:
        discount: Decimal (default 0)
        days_old: int — backdates Order.created_at (default 0)
        order_status: str (default 'Processing')

    Returns a dict with 'order', 'user', and 'lines' (list of the
    OrderProduct instances created, in the same order as the specs).
    """
    from category.models import Category
    from store.models import Product, ProductVariation
    from orders.models import Order, OrderProduct

    _counter = {"n": 0}

    def _build(
        *,
        lines=None,
        discount=Decimal("0.00"),
        days_old=0,
        order_status="Processing",
    ):
        if lines is None:
            lines = [{"product_kind": "digital_instant"}]

        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"canceluser{n}",
            email=f"cancel{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )

        order = Order.objects.create(
            user=user,
            order_number=f"TEST-CANCEL-{n:04d}",
            email=user.email,
            is_ordered=True,
            order_status=order_status,
            discount=discount,
            total_due=Decimal("10.00"),
        )

        if days_old:
            # Order.created_at is auto_now_add, so update() bypasses it.
            Order.objects.filter(pk=order.pk).update(
                created_at=timezone.now() - timedelta(days=days_old)
            )
            order.refresh_from_db()

        order_products = []

        for i, spec in enumerate(lines):
            product_kind = spec.get("product_kind", "digital_instant")
            is_digital = product_kind.startswith("digital")
            is_physical = product_kind == "physical"
            is_voucher = product_kind == "voucher"
            fulfillment_type = (
                "INSTANT" if product_kind == "digital_instant" else "CUSTOM"
            )

            category = Category.objects.create(
                category_name=f"Category {n}-{i}",
                slug=f"cat-{n}-{i}",
                product_format="e-product" if is_digital else "physical",
            )

            product = Product.objects.create(
                product_name=f"Product {n}-{i}",
                category=category,
                is_digital=is_digital,
                digital_fulfillment_type=fulfillment_type,
                is_physical=is_physical,
                is_voucher=is_voucher,
                is_active=True,
                status="Published",
            )

            price = spec.get("price", Decimal("10.00"))
            variation = ProductVariation.objects.create(
                product=product,
                price=price,
                stock=1 if is_digital else 10,
                is_available=True,
            )

            order_product = OrderProduct.objects.create(
                order=order,
                user=user,
                product=product,
                product_variation=variation,
                product_price=price,
                quantity=1,
                ordered=True,
                is_claimed=spec.get("is_claimed", False),
                is_dispatched=spec.get("is_dispatched", False),
                is_partially_used=spec.get("is_partially_used", False),
            )
            order_products.append(order_product)

        return {"order": order, "user": user, "lines": order_products}

    return _build


# ──────────────────────────────────────────────────────────────────
# evaluate_cancellation_details — the rules
# ──────────────────────────────────────────────────────────────────

class TestEvaluateCancellationDetails:

    def test_unclaimed_instant_digital_is_eligible(self, build_order):
        b = build_order(lines=[{"product_kind": "digital_instant", "is_claimed": False}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is True
        assert fee == Decimal("0.00")

    def test_claimed_instant_digital_is_blocked(self, build_order):
        b = build_order(lines=[{"product_kind": "digital_instant", "is_claimed": True}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "claimed" in msg.lower()

    def test_digital_seven_day_window_exceeded_is_blocked(self, build_order):
        b = build_order(
            lines=[{"product_kind": "digital_instant", "is_claimed": False}],
            days_old=8,
        )
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "window" in msg.lower() or "7" in msg

    def test_digital_at_day_seven_still_eligible(self, build_order):
        # The check is `> 7`, so exactly 7 days is still within the window.
        b = build_order(
            lines=[{"product_kind": "digital_instant", "is_claimed": False}],
            days_old=7,
        )
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is True

    def test_dispatched_physical_is_blocked(self, build_order):
        b = build_order(lines=[{"product_kind": "physical", "is_dispatched": True}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "dispatched" in msg.lower()

    def test_undispatched_physical_is_eligible(self, build_order):
        b = build_order(lines=[{"product_kind": "physical", "is_dispatched": False}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is True

    def test_custom_digital_is_not_subject_to_claim_block(self, build_order):
        # Only INSTANT digital lines are gated by is_claimed. Custom
        # (manual-fulfilment) digital orders fall through to the standard
        # eligibility path and are allowed here.
        b = build_order(lines=[{"product_kind": "digital_custom", "is_claimed": True}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is True

    def test_partially_used_voucher_is_blocked(self, build_order):
        b = build_order(lines=[{"product_kind": "voucher", "is_partially_used": True}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "voucher" in msg.lower() or "禮品券" in msg

    def test_unused_voucher_is_eligible(self, build_order):
        b = build_order(lines=[{"product_kind": "voucher", "is_partially_used": False}])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is True

    def test_discount_present_blocks_self_service(self, build_order):
        # Policy: any order with a positive discount requires manual review.
        b = build_order(
            lines=[{"product_kind": "physical"}],
            discount=Decimal("5.00"),
        )
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "promotional" in msg.lower() or "discount" in msg.lower()

    def test_already_cancelled_order_is_blocked(self, build_order):
        b = build_order(order_status="Cancelled")
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "cancelled" in msg.lower() or "already" in msg.lower()

    def test_already_refunded_order_is_blocked(self, build_order):
        b = build_order(order_status="Refunded")
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False

    def test_empty_order_is_blocked(self, db, django_user_model):
        from orders.models import Order

        user = django_user_model.objects.create_user(
            username="emptyorder",
            email="empty@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        order = Order.objects.create(
            user=user,
            order_number="TEST-CANCEL-EMPTY",
            email=user.email,
            is_ordered=True,
            order_status="Processing",
        )
        eligible, fee, msg = order.evaluate_cancellation_details()
        assert eligible is False
        assert "no items" in msg.lower() or "無商品" in msg

    def test_mixed_cart_claimed_digital_blocks_entire_order(self, build_order):
        # Even though the physical line is not dispatched, the claimed
        # digital line on the same order blocks self-service cancellation
        # for the whole order. This is the interaction the roadmap
        # explicitly calls out.
        b = build_order(lines=[
            {"product_kind": "physical", "is_dispatched": False},
            {"product_kind": "digital_instant", "is_claimed": True},
        ])
        eligible, fee, msg = b["order"].evaluate_cancellation_details()
        assert eligible is False
        assert "claimed" in msg.lower()


# ──────────────────────────────────────────────────────────────────
# can_be_cancelled_online — the boolean wrapper
# ──────────────────────────────────────────────────────────────────

class TestCanBeCancelledOnline:

    def test_true_when_eligible(self, build_order):
        b = build_order(lines=[{"product_kind": "physical"}])
        assert b["order"].can_be_cancelled_online is True

    def test_false_when_claimed_digital(self, build_order):
        b = build_order(lines=[{"product_kind": "digital_instant", "is_claimed": True}])
        assert b["order"].can_be_cancelled_online is False

    def test_false_when_discount_present(self, build_order):
        b = build_order(
            lines=[{"product_kind": "physical"}],
            discount=Decimal("1.00"),
        )
        assert b["order"].can_be_cancelled_online is False