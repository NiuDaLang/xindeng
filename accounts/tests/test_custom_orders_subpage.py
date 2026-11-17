# accounts/tests/test_custom_orders_subpage.py
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
    # 🌟 FORCE ACTIVE
    user.is_active = True
    user.save()
    UserProfile.objects.create(user=user)
    return user

@pytest.fixture
def artisan(db):
    user = Account.objects.create_user(
        username="artisan", email="artisan@test.com", password="pw", receive_newsletter=False
    )
    # 🌟 FORCE ACTIVE
    user.is_active = True
    user.save()
    return CreatorProfile.objects.create(user=user, display_name="Test Artisan", is_verified=True)

@pytest.fixture
def custom_line(db, buyer, artisan):
    cat = Category.objects.create(category_name="Test Category", slug="test-cat")
    order = Order.objects.create(user=buyer, email="buyer@test.com", order_number="TEST-123", is_ordered=True)
    
    product = Product.objects.create(
        product_name="Custom Painting", 
        category=cat, 
        is_digital=True, 
        digital_fulfillment_type="CUSTOM"
    )
    variation = ProductVariation.objects.create(product=product, price=100, stock=10)
    
    return OrderProduct.objects.create(
        order=order, product=product, product_variation=variation, fulfilled_by=artisan, quantity=1
    )

@pytest.mark.django_db
class TestCustomOrdersSubpage:
    def test_login_required(self, client):
        url = reverse('dashboard', kwargs={'subpage': 'custom_orders'})
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

    def test_only_lists_custom_lines(self, client, buyer, custom_line):
        cat = custom_line.product.category
        
        inst_order = Order.objects.create(user=buyer, email="b@test.com", order_number="TEST-456", is_ordered=True)
        inst_prod = Product.objects.create(
            product_name="Instant Book", 
            category=cat,
            is_digital=True, 
            digital_fulfillment_type="INSTANT"
        )
        inst_var = ProductVariation.objects.create(product=inst_prod, price=50, stock=10)
        OrderProduct.objects.create(order=inst_order, product=inst_prod, product_variation=inst_var, quantity=1)

        # 🌟 Use force_login with is_active=True
        client.force_login(buyer, backend='django.contrib.auth.backends.ModelBackend')
        
        url = reverse('dashboard', kwargs={'subpage': 'custom_orders'})
        response = client.get(url)
        
        assert response.status_code == 200
        assert "Custom Painting" in response.content.decode()
        assert "Instant Book" not in response.content.decode()

    def test_unread_annotation(self, client, buyer, artisan, custom_line):
        ArtisanChatMessage.objects.create(
            artisan=artisan, customer=buyer, sender=artisan.user, 
            content="Here is your update", order_product=custom_line, is_read=False
        )
        
        client.force_login(buyer, backend='django.contrib.auth.backends.ModelBackend')
        
        url = reverse('dashboard', kwargs={'subpage': 'custom_orders'})
        response = client.get(url)
        
        assert response.status_code == 200
        line = response.context['custom_order_lines'].first()
        assert line.unread_thread == 1