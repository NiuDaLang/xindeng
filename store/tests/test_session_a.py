# store/tests/test_session_a.py
from decimal import Decimal
import pytest
from django.contrib.auth import get_user_model
from store.models import Product, ProductVariation, VariationCampaignEnrolment
from accounts.models import Perk
from django.utils import timezone

Account = get_user_model()

@pytest.mark.django_db
def test_commission_below_floor_warns_in_admin_form(sample_variation):
    """The admin form's clean() refuses commission < 3.4 without acknowledgement."""
    from store.admin import ProductVariationAdminForm
    from django import forms

    form = ProductVariationAdminForm(instance=sample_variation)
    form.cleaned_data = {
        'platform_commission_pct': Decimal('2.0'),
        # acknowledge_net_loss not present
    }
    with pytest.raises(forms.ValidationError) as exc_info:
        form.clean()
    assert 'platform_commission_pct' in exc_info.value.message_dict


def test_commission_below_floor_passes_with_acknowledgement(sample_variation):
    from store.admin import ProductVariationAdminForm

    form = ProductVariationAdminForm(instance=sample_variation)
    form.cleaned_data = {
        'platform_commission_pct': Decimal('2.0'),
        'acknowledge_net_loss': True,
    }
    result = form.clean()  # should not raise
    assert result['platform_commission_pct'] == Decimal('2.0')


@pytest.mark.django_db
def test_enrolment_unique_per_variation_per_perk(campaign_perk, sample_variation):
    VariationCampaignEnrolment.objects.create(
        variation=sample_variation, perk=campaign_perk,
    )
    with pytest.raises(Exception):
        VariationCampaignEnrolment.objects.create(
            variation=sample_variation, perk=campaign_perk,
        )