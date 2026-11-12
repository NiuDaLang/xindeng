# settlements/tests/test_session_a.py

import pytest
from decimal import Decimal

from settlements.admin import _create_settlement_lines_for_order
from tests.fixtures.session_a import (  # noqa: F401 — fixtures used by name
    artisan_a,
    participating_variation,
    sale_variation,
    unenrolled_variation,
    walkthrough_order,
    settlement_line,
)


@pytest.mark.django_db
def test_settlement_deferred_until_artisan_dispatches(walkthrough_order):
    """Artisan A's settlement is not created until all their lines dispatched."""
    result = _create_settlement_lines_for_order(walkthrough_order, admin_user=None)
    assert len(result["created"]) == 0
    assert len(result["warnings"]) > 0

    # Dispatch one of two lines — still pending.
    line = walkthrough_order.items.first()
    line.is_dispatched = True
    line.save(update_fields=["is_dispatched"])

    result = _create_settlement_lines_for_order(walkthrough_order, admin_user=None)
    assert len(result["created"]) == 0

    # Dispatch the second — now settles.
    for remaining in walkthrough_order.items.filter(is_dispatched=False):
        remaining.is_dispatched = True
        remaining.save(update_fields=["is_dispatched"])

    result = _create_settlement_lines_for_order(walkthrough_order, admin_user=None)
    assert len(result["created"]) == 1


@pytest.mark.django_db
def test_settlement_sums_commission_and_discount(settlement_line):
    """Aggregations sum commission, discount, and populate mode mix."""
    assert settlement_line.platform_commission_amount == Decimal("9.00")
    assert settlement_line.discount_absorbed_by_artisan == Decimal("15.00")
    assert settlement_line.discount_absorbed_by_platform == Decimal("5.00")
    assert "VIA_HUB" in settlement_line.shipping_mode_mix


@pytest.mark.django_db
def test_net_payable_formula(settlement_line):
    """net_payable_to_artisan subtracts commission + artisan discount."""
    expected = (
        settlement_line.gross_payable_to_artisan
        - settlement_line.platform_commission_amount
        - settlement_line.discount_absorbed_by_artisan
    )
    assert settlement_line.net_payable_to_artisan == expected