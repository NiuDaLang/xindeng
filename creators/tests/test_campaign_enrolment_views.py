# creators/tests/test_campaign_enrolment_views.py

import pytest
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from accounts.models import Perk
from store.models import VariationCampaignEnrolment
from tests._fakes import make_superuser


@pytest.fixture
def artisan_user(db):
    """Create a user and an associated verified CreatorProfile."""
    user = make_superuser(username="test_artisan", email="artisan@example.com")
    # Assuming CreatorProfile is created via signal or explicitly here:
    from creators.models import CreatorProfile
    profile, _ = CreatorProfile.objects.get_or_create(
        user=user, 
        defaults={"display_name": "Test Artisan", "is_verified": True}
    )
    return user


@pytest.fixture
def published_product(db, artisan_user):
    """Create a Published product with one variation owned by the artisan."""
    from category.models import Category
    from store.models import Product, ProductVariation
    
    cat = Category.objects.create(category_name="Test Cat", slug="test-cat")
    product = Product.objects.create(
        product_name="Test Product", 
        category=cat, 
        status="Published",
        creator=artisan_user.creator_profile,
        is_physical=False,
        is_digital=True,
        is_active=True,
    )
    variation = ProductVariation.objects.create(
        product=product, 
        price=Decimal('100'), 
        original_price=Decimal('100'),
        stock=10, 
        platform_commission_pct=Decimal('5.0'),
        images='test/image.jpg',
    )
    return product, variation


@pytest.fixture
def future_perk(db):
    """Create an OPT_IN campaign that hasn't started yet."""
    return Perk.objects.create(
        code="TESTFUTURE",
        description="Future Campaign",
        discount_type="percentage",
        discount_value=Decimal('10'),
        valid_from=timezone.now() + timezone.timedelta(days=2),
        valid_to=timezone.now() + timezone.timedelta(days=10),
        funding_source='PLATFORM',
        platform_funding_share_pct=Decimal('100'),
        enrolment_mode='OPT_IN_BY_ARTISAN',
        enrolment_deadline=timezone.now() + timezone.timedelta(days=1),
        is_active=True,
    )


@pytest.mark.django_db
class TestCampaignEnrolmentViews:

    def test_dashboard_product_campaigns_renders(self, client, artisan_user, published_product, future_perk):
        """GET: Ensure the modal renders successfully with the new product_pk URL."""
        product, _ = published_product
        client.force_login(artisan_user)
        
        url = reverse('a_dashboard_product_campaigns', args=[product.id])
        response = client.get(url)
        
        assert response.status_code == 200
        assert "Campaigns｜活動" in response.content.decode()
        assert "Test Product" in response.content.decode()

    def test_enrol_campaign_from_modal(self, client, artisan_user, published_product, future_perk):
        """POST: Enrol, asserting DB mutation and correct partial re-render."""
        product, variation = published_product
        client.force_login(artisan_user)
        
        url = reverse('a_dashboard_variation_enrol_campaign', args=[product.id, variation.id, future_perk.id])
        
        # Simulate the HTMX request from the modal
        response = client.post(url, HTTP_HX_TARGET="campaign-modal-content")
        
        assert response.status_code == 200
        # Check DB
        assert VariationCampaignEnrolment.objects.filter(variation=variation, perk=future_perk).exists()
        # Check that we re-rendered the MODAL, not the variation cards partial
        content = response.content.decode()
        assert "Campaigns｜活動" in content
        assert "Enrolled｜已參加" in content
        
    def test_unenrol_campaign_from_modal(self, client, artisan_user, published_product, future_perk):
        """POST: Un-enrol, asserting DB deletion and correct partial re-render."""
        product, variation = published_product
        client.force_login(artisan_user)
        
        # Seed the enrolment
        enrolment = VariationCampaignEnrolment.objects.create(
            variation=variation, perk=future_perk, enrolled_by=artisan_user
        )
        
        url = reverse('a_dashboard_variation_unenrol_campaign', args=[product.id, variation.id, enrolment.id])
        
        response = client.post(url, HTTP_HX_TARGET="campaign-modal-content")
        
        assert response.status_code == 200
        assert not VariationCampaignEnrolment.objects.filter(id=enrolment.id).exists()
        
        content = response.content.decode()
        assert "Campaigns｜活動" in content
        assert "Opt in｜加入" in content

    def test_unenrol_lockout_guard(self, client, artisan_user, published_product, future_perk):
        """POST: Attempt un-enrol after campaign has started, expect lockout badge."""
        product, variation = published_product
        client.force_login(artisan_user)
        
        # Make campaign valid NOW
        future_perk.valid_from = timezone.now() - timezone.timedelta(days=1)
        future_perk.save()
        
        enrolment = VariationCampaignEnrolment.objects.create(
            variation=variation, perk=future_perk, enrolled_by=artisan_user
        )
        
        url = reverse('a_dashboard_variation_unenrol_campaign', args=[product.id, variation.id, enrolment.id])
        response = client.post(url, HTTP_HX_TARGET="campaign-modal-content")
        
        assert response.status_code == 200
        # DB row must survive the refused un-enrol
        assert VariationCampaignEnrolment.objects.filter(id=enrolment.id).exists()
        
        # The modal must re-render, showing the lockout badge rather than the Leave button
        content = response.content.decode()
        assert "Campaigns｜活動" in content
        assert "Locked｜已鎖定" in content
        assert "Leave｜退出" not in content

