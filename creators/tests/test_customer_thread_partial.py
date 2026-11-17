# creators/tests/test_customer_thread_partial.py
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation
from category.models import Category
from accounts.models import UserProfile
from creators.models import CreatorProfile, ArtisanChatMessage

Account = get_user_model()

@pytest.fixture
def buyer(db):
    user = Account.objects.create_user(
        username="buyer", email="buyer@test.com", password="pw", receive_newsletter=False
    )
    user.is_active = True
    user.save()
    UserProfile.objects.create(user=user)
    return user

@pytest.fixture
def artisan(db):
    user = Account.objects.create_user(
        username="artisan", email="artisan@test.com", password="pw", receive_newsletter=False
    )
    user.is_active = True
    user.save()
    return CreatorProfile.objects.create(user=user, display_name="Test Artisan", slug="test-artisan", is_verified=True)

@pytest.fixture
def custom_line(db, buyer, artisan):
    cat = Category.objects.create(category_name="Test Category", slug="test-cat")
    order = Order.objects.create(user=buyer, email="buyer@test.com", order_number="TEST-123", is_ordered=True)
    
    product = Product.objects.create(
        product_name="Custom", 
        category=cat, 
        is_digital=True, 
        digital_fulfillment_type="CUSTOM"
    )
    variation = ProductVariation.objects.create(product=product, price=100, stock=10)
    
    return OrderProduct.objects.create(
        order=order, product=product, product_variation=variation, fulfilled_by=artisan, quantity=1
    )

@pytest.mark.django_db
class TestCustomerThreadPartial:
    def test_login_required(self, client, artisan):
        url = reverse('customer_thread_partial', kwargs={'artisan_slug': artisan.slug})
        response = client.get(url)
        assert response.status_code == 302

    def test_404_if_no_custom_line(self, client, buyer, artisan):
        client.force_login(buyer, backend='django.contrib.auth.backends.ModelBackend')
        
        url = reverse('customer_thread_partial', kwargs={'artisan_slug': artisan.slug})
        response = client.get(url)
        assert response.status_code == 404

    def test_renders_partial_and_flips_unread(self, client, buyer, artisan, custom_line):
        msg = ArtisanChatMessage.objects.create(
            artisan=artisan, customer=buyer, sender=artisan.user, 
            content="Partial test", order_product=custom_line, is_read=False
        )
        
        client.force_login(buyer, backend='django.contrib.auth.backends.ModelBackend')
        
        url = reverse('customer_thread_partial', kwargs={'artisan_slug': artisan.slug})
        response = client.get(f"{url}?order_product={custom_line.id}")
        
        assert response.status_code == 200
        assert "Partial test" in response.content.decode()
        msg.refresh_from_db()
        assert msg.is_read is True