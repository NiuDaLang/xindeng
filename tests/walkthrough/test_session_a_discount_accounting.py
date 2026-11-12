# tests/walkthrough/test_session_a_discount_accounting.py
"""
Backlog 42 — Session A walkthrough.

Proves that the three building blocks introduced in Session A
compose correctly:

  1. snapshot_line_commission  — snapshots commission onto OrderProduct
  2. line_participates_in_platform_perk — decides who participates
  3. allocate_platform_perk    — splits the campaign discount between
                                  platform (capped at commission) and
                                  artisan

Unit tests in orders/tests/test_session_a.py already prove the rules
in isolation. This file proves the composition: a real Order, real
OrderProduct lines, a real settlement, and the arithmetic that ties
them together.

Fixture ownership:
  - The fixtures live in tests/fixtures/session_a.py so that
    settlements/tests/test_session_a.py (Backlog 43) can import the
    same objects rather than redefine them.
  - The image-byte factories and media-redirect in the project-root
    conftest.py are unrelated to this file; nothing here touches
    media.
"""

from decimal import Decimal

import pytest

from orders.utils import line_participates_in_platform_perk
from settlements.admin import _create_settlement_lines_for_order

from tests.fixtures.session_a import (  # noqa: F401 — fixtures are used by name
    artisan_a,
    participating_variation,
    sale_variation,
    unenrolled_variation,
    walkthrough_order,
    settlement_line,
)


# ──────────────────────────────────────────────────────────────
# 1. Participation gate — enrolment + Semantics A
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_walkthrough_participation_gate(
    campaign_perk,
    participating_variation,
    sale_variation,
    unenrolled_variation,
):
    """
    Three cases, one line each:

      participating  → True   (enrolled, not on sale, 5% commission)
      sale           → False  (enrolled, on sale — Semantics A)
      unenrolled     → False  (never opted in)

    The sale case is the interesting one: enrolment is present, so a
    naive "if enrolled → participate" implementation would wrongly
    include it. Semantics A overrides the enrolment.
    """

    class _Line:
        """Minimal adapter: line_participates_in_platform_perk accepts
        anything with .product_variation and .get_subtotal()."""
        def __init__(self, variation):
            self.product_variation = variation
        def get_subtotal(self):
            return self.product_variation.price

    assert line_participates_in_platform_perk(
        _Line(participating_variation), campaign_perk,
    ) is True

    assert line_participates_in_platform_perk(
        _Line(sale_variation), campaign_perk,
    ) is False

    assert line_participates_in_platform_perk(
        _Line(unenrolled_variation), campaign_perk,
    ) is False


# ──────────────────────────────────────────────────────────────
# 2. Commission snapshot + Invariant 2 clamp
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_walkthrough_discount_attribution_sums_to_order_discount(
    walkthrough_order,
):
    """
    20% campaign on a ¥100 line at 5% commission:

      raw discount      = 100 × 20%           = ¥20.00
      platform absorbs  = min(¥20, ¥5 comm)   = ¥5.00  (clamp)
      artisan absorbs   = ¥20 − ¥5            = ¥15.00
      Order.discount    = ¥20.00

    This is the first test in the suite that exercises Invariant 2
    (platform_absorbed ≤ line commission) end-to-end. The
    commented-out test_allocate_caps_platform_absorbed_at_commission
    in orders/tests/test_session_a.py was waiting on the test_order
    fixture; this test subsumes it.
    """
    line = walkthrough_order.items.get(
        product_variation__product__product_name="Walkthrough Participating",
    )

    assert line.platform_commission_pct == Decimal("5.00")
    assert line.platform_commission_amount == Decimal("5.00")

    assert line.discount_absorbed_by_platform_cny == Decimal("5.00")
    assert line.discount_absorbed_by_artisan_cny == Decimal("15.00")

    assert walkthrough_order.discount == Decimal("20.00")

    # The invariant the handoff's step 2 names:
    attribution_sum = (
        line.discount_absorbed_by_platform_cny
        + line.discount_absorbed_by_artisan_cny
    )
    assert attribution_sum == walkthrough_order.discount


@pytest.mark.django_db
def test_walkthrough_sale_line_has_commission_but_no_discount(
    walkthrough_order,
):
    """
    The sale line was enrolled but excluded by Semantics A. Two
    things are true simultaneously:

      * Its commission is snapshotted normally (5% of ¥80 = ¥4.00).
        Commission is not conditional on participation — the platform
        earns commission on every sale.
      * Its discount attribution is zero. The artisan is already
        funding the sale; the platform does not stack the campaign
        on top.

    Confusing these two is the most likely misreading of Session A:
    "the sale line is excluded" does not mean "the sale line has no
    commission." It means "the sale line has no campaign discount."
    """
    line = walkthrough_order.items.get(
        product_variation__product__product_name="Walkthrough On Sale",
    )

    assert line.platform_commission_pct == Decimal("5.00")
    assert line.platform_commission_amount == Decimal("4.00")   # 80 × 5%

    assert line.discount_absorbed_by_platform_cny == Decimal("0.00")
    assert line.discount_absorbed_by_artisan_cny == Decimal("0.00")
    assert line.applied_perk_code == ""


# ──────────────────────────────────────────────────────────────
# 3. Settlement deferral (Backlog 43's first clause)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_walkthrough_settlement_deferred_until_dispatch(walkthrough_order):
    """
    Before dispatch, _create_settlement_lines_for_order creates
    nothing and warns once. The per-artisan dispatch gate (Session A
    Option C) is what enforces this.
    """
    result = _create_settlement_lines_for_order(walkthrough_order, admin_user=None)

    assert len(result["created"]) == 0
    assert len(result["skipped"]) == 0
    assert len(result["warnings"]) == 1
    assert "awaiting dispatch" in result["warnings"][0]


# ──────────────────────────────────────────────────────────────
# 4. Settlement aggregation + mode mix
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_walkthrough_dispatch_then_settle(settlement_line):
    """
    Every line on the walkthrough order dispatched (the fixture
    dispatches all lines with VIA_HUB). _create_settlement_lines_for_order
    produces exactly one line for artisan_a.

    Aggregates:

      product_revenue            = 100 + 80         = ¥180.00
      platform_commission_amount = 5 + 4            = ¥9.00
      discount_absorbed_by_platform = 5 + 0         = ¥5.00
      discount_absorbed_by_artisan  = 15 + 0        = ¥15.00
      shipping_mode_mix                             = "VIA_HUB x2"
    """
    assert settlement_line.product_revenue == Decimal("180.00")
    assert settlement_line.platform_commission_amount == Decimal("9.00")
    assert settlement_line.discount_absorbed_by_platform == Decimal("5.00")
    assert settlement_line.discount_absorbed_by_artisan == Decimal("15.00")
    assert settlement_line.shipping_mode_mix == "VIA_HUB x2"
    assert settlement_line.applied_perk_codes == "XMAS2026"


# ──────────────────────────────────────────────────────────────
# 5. net_payable formula (Backlog 43's third clause)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_walkthrough_net_payable_formula(settlement_line):
    """
    Assert net_payable_to_artisan equals the model's own formula,
    spelled out the long way. With zero shipping variance and zero
    website margin, this reduces to:

      gross − commission − discount_absorbed_by_artisan

    where gross = product_revenue + shipping_charged_to_customer
                = 180 + 0 = ¥180.00.

    Expected: 180 − 9 − 15 = ¥156.00.
    """
    expected_gross = settlement_line.product_revenue + settlement_line.shipping_charged_to_customer
    expected_net = (
        expected_gross
        - settlement_line.platform_commission_amount
        - settlement_line.discount_absorbed_by_artisan
        - settlement_line.website_margin_amount
        - settlement_line.shipping_paid_by_website
        - settlement_line.tax_paid_by_website
        + settlement_line.shipping_paid_by_artisan
        + settlement_line.tax_paid_by_artisan
        - settlement_line.shipping_shortfall_absorbed_by_artisan
        + settlement_line.shipping_surplus_returned_to_artisan
        + settlement_line.other_costs
    )
    assert settlement_line.net_payable_to_artisan == expected_net
    assert expected_net == Decimal("156.00")