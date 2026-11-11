# settlements/tests/test_session_a.py

import pytest
from decimal import Decimal
from settlements.admin import _create_settlement_lines_for_order
from orders.models import OrderProduct
from django.utils import timezone


# @pytest.mark.django_db
# def test_settlement_deferred_until_artisan_dispatches(test_order, artisan_a):
#     """Artisan A's settlement is not created until all their lines dispatched."""
#     # ... create OrderProducts for artisan_a, none dispatched ...
#     result = _create_settlement_lines_for_order(test_order, admin_user=None)
#     assert len(result['created']) == 0
#     assert len(result['warnings']) > 0
#     # ... dispatch one of two lines ...
#     result = _create_settlement_lines_for_order(test_order, admin_user=None)
#     assert len(result['created']) == 0  # still pending
#     # ... dispatch the second ...
#     result = _create_settlement_lines_for_order(test_order, admin_user=None)
#     assert len(result['created']) == 1


# @pytest.mark.django_db
# def test_settlement_sums_commission_and_discount(test_order, artisan_a):
#     """Aggregations sum commission, discount, and populate mode mix."""
#     # ... setup order lines with commission/discount on each ...
#     result = _create_settlement_lines_for_order(test_order, admin_user=None)
#     line = result['created'][0]
#     assert line.platform_commission_amount == Decimal('10.00')
#     assert line.discount_absorbed_by_artisan == Decimal('15.00')
#     assert line.discount_absorbed_by_platform == Decimal('5.00')
#     assert 'DIRECT' in line.shipping_mode_mix


# @pytest.mark.django_db
# def test_net_payable_formula(settlement_line):
#     """net_payable_to_artisan subtracts commission + artisan discount."""
#     # ... with known values ...
#     expected = (
#         settlement_line.gross_payable_to_artisan
#         - settlement_line.platform_commission_amount
#         - settlement_line.discount_absorbed_by_artisan
#     )
#     assert settlement_line.net_payable_to_artisan == expected