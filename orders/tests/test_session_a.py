# orders/tests/test_session_a.py

import pytest
from decimal import Decimal
from accounts.models import Perk
from orders.utils import line_participates_in_platform_perk, allocate_platform_perk
from store.models import VariationCampaignEnrolment
from django.utils import timezone


@pytest.mark.django_db
def test_sale_sku_excluded_from_platform_perk(campaign_perk, sample_variation):
    """Artisan sale (price < original_price) excludes the line even if enrolled."""
    sample_variation.original_price = Decimal('150')
    sample_variation.price = Decimal('100')  # on sale
    sample_variation.save()
    VariationCampaignEnrolment.objects.create(
        variation=sample_variation, perk=campaign_perk,
    )

    class _Line:
        product_variation = sample_variation
        def get_subtotal(self): return Decimal('100')

    assert line_participates_in_platform_perk(_Line(), campaign_perk) is False


@pytest.mark.django_db
def test_zero_commission_excluded(campaign_perk, sample_variation):
    sample_variation.platform_commission_pct = Decimal('0.00')
    sample_variation.save()
    class _Line:
        product_variation = sample_variation
        def get_subtotal(self): return Decimal('100')
    assert line_participates_in_platform_perk(_Line(), campaign_perk) is False


@pytest.mark.django_db
def test_late_enrolment_excluded(campaign_perk, sample_variation):
    """Enrolment after the deadline → line not eligible."""
    # Simulate late enrolment by setting enrolled_at in the past
    # relative to a tightened deadline.
    campaign_perk.enrolment_deadline = timezone.now() - timezone.timedelta(days=1)
    campaign_perk.save()
    VariationCampaignEnrolment.objects.create(
        variation=sample_variation, perk=campaign_perk,
    )
    class _Line:
        product_variation = sample_variation
        def get_subtotal(self): return Decimal('100')
    # enrolled_at = now(), which is after the (past) deadline
    assert line_participates_in_platform_perk(_Line(), campaign_perk) is False


# @pytest.mark.django_db
# def test_allocate_caps_platform_absorbed_at_commission(
#     campaign_perk, sample_variation, test_order,
# ):
#     """
#     20% platform campaign on a 5%-commission SKU:
#     platform absorbs at most 5%, excess shifts to artisan.
#     """
#     sample_variation.platform_commission_pct = Decimal('5.0')
#     sample_variation.save()
#     VariationCampaignEnrolment.objects.create(
#         variation=sample_variation, perk=campaign_perk,
#     )
#     # ... create OrderProduct line, call snapshot_line_commission,
#     # call allocate_platform_perk, assert:
#     # line.discount_absorbed_by_platform_cny == Decimal('5.00')
#     # line.discount_absorbed_by_artisan_cny == Decimal('15.00')