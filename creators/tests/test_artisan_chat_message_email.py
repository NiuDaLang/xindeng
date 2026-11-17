# creators/tests/test_artisan_chat_message_email.py

import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation
from category.models import Category
from accounts.models import UserProfile
from creators.models import CreatorProfile, ArtisanChatMessage, FrontlineThread

Account = get_user_model()

@pytest.fixture
def buyer(db):
    user = Account.objects.create_user(
        username="buyer", email="buyer@test.com", password="pw", receive_newsletter=False
    )
    UserProfile.objects.create(user=user)
    return user

@pytest.fixture
def artisan(db):
    user = Account.objects.create_user(
        username="artisan", email="artisan@test.com", password="pw", receive_newsletter=False
    )
    return CreatorProfile.objects.create(user=user, display_name="Artisan", slug="artisan-slug", is_verified=True)

@pytest.fixture
def admin(db):
    user = Account.objects.create_superuser(username="admin", email="admin@test.com", password="pw")
    UserProfile.objects.create(user=user)
    return user

@pytest.fixture
def custom_line(db, buyer, artisan):
    cat = Category.objects.create(category_name="Test Category", slug="test-cat-2")
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
# 🌟 PATCH THE CELERY TASK, NOT THE UTILS FUNCTION
@patch("creators.tasks.send_artisan_chat_message_email_task.delay")
class TestArtisanChatEmailDispatch:
    def test_pre_purchase_message_does_not_trigger_email(self, mock_delay, buyer, artisan):
        ArtisanChatMessage.objects.create(
            artisan=artisan, customer=buyer, sender=buyer, content="Pre-purchase", order_product=None
        )
        mock_delay.assert_not_called()

    def test_buyer_message_emails_artisan(self, mock_delay, buyer, artisan, custom_line, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks(execute=True):
            ArtisanChatMessage.objects.create(
                artisan=artisan, customer=buyer, sender=buyer, 
                content="Need an update", order_product=custom_line
            )
        mock_delay.assert_called_once()

    def test_escalated_thread_emails_admin_too(self, mock_delay, buyer, artisan, admin, custom_line, django_capture_on_commit_callbacks):
        thread = FrontlineThread.objects.create(
            artisan=artisan, customer=buyer, order_product=custom_line
        )
        thread.escalate(by=buyer)
        
        with django_capture_on_commit_callbacks(execute=True):
            ArtisanChatMessage.objects.create(
                artisan=artisan, customer=buyer, sender=buyer, 
                content="Escalated question", order_product=custom_line
            )
            
        mock_delay.assert_called_once()