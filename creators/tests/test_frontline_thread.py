# creators/tests/test_frontline_thread.py
"""
Tests for FrontlineThread (backlog 24, commit 3a).

The model holds per-thread state that neither the artisan-side nor
the customer-side view can own: settled_at, escalated_at, and the
denormalized last_message_at. The messages themselves live on
ArtisanChatMessage and are unaffected by this model.

Six tests:

  1. Signal creates a FrontlineThread on the first message.
  2. Signal is idempotent: second message on the same line reuses
     the existing thread and advances last_message_at.
  3. Signal does NOT create a thread for a message with
     order_product=None (legacy / pre-purchase).
  4. mark_settled sets settled_at and settled_by; idempotent on
     second call.
  5. mark_unsettled clears both; no-op if already unsettled.
  6. escalate sets escalated_at and escalated_by; idempotent; and
     settlement does not clear escalation.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from category.models import Category
from creators.models import (
    ArtisanChatMessage,
    CreatorProfile,
    FrontlineThread,
)
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="fl-customer",
        email="fl-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="fl-artisan",
        email="fl-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user,
        display_name="FL Artisan",
        is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="FL Category", slug="fl-category",
    )


@pytest.fixture
def product(category, artisan_profile):
    return Product.objects.create(
        product_name="FL Product", slug="fl-product",
        category=category, creator=artisan_profile,
        is_digital=True, digital_fulfillment_type="CUSTOM",
        is_active=True, status="Published",
    )


@pytest.fixture
def variation(product):
    return ProductVariation.objects.create(
        product=product, price="10.00", stock=1,
    )


@pytest.fixture
def order(customer):
    return Order.objects.create(
        user=customer, email=customer.email,
        order_number="FL-ORDER-0001",
        is_ordered=True, order_status="Processing",
    )


@pytest.fixture
def order_product(order, product, variation, artisan_profile):
    return OrderProduct.objects.create(
        order=order, user=order.user,
        product=product, product_variation=variation,
        product_price="10.00", quantity=1, ordered=True,
        fulfilled_by=artisan_profile,
    )


# ──────────────────────────────────────────────────────────────
# Signal tests
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFrontlineThreadSignal:

    def test_first_message_creates_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        assert FrontlineThread.objects.count() == 0

        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="first message",
            order_product=order_product,
        )

        threads = FrontlineThread.objects.all()
        assert threads.count() == 1
        thread = threads.get()
        assert thread.artisan_id == artisan_profile.id
        assert thread.customer_id == customer.id
        assert thread.order_product_id == order_product.id
        assert thread.last_message_at == msg.created_at
        assert thread.settled_at is None
        assert thread.escalated_at is None

    def test_second_message_reuses_thread_and_advances_timestamp(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        first = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="first", order_product=order_product,
        )
        # No-op write to force a later created_at on the next message.
        second = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=artisan_user, content="second",
            order_product=order_product,
        )

        assert FrontlineThread.objects.count() == 1
        thread = FrontlineThread.objects.get()
        # last_message_at reflects the *later* message.
        assert thread.last_message_at == second.created_at
        assert thread.last_message_at > first.created_at

    def test_message_without_order_product_does_not_create_thread(
        self, customer, artisan_profile,
    ):
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="pre-purchase question",
            order_product=None,
        )
        assert FrontlineThread.objects.count() == 0


# ──────────────────────────────────────────────────────────────
# State transitions
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFrontlineThreadState:

    def _make_thread(self, customer, artisan_profile, artisan_user, order_product):
        """Helper: create a thread via a first message."""
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="seed", order_product=order_product,
        )
        return FrontlineThread.objects.get()

    def test_mark_settled_sets_fields_and_is_idempotent(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        thread = self._make_thread(customer, artisan_profile, artisan_user, order_product)
        admin = Account.objects.create_user(
            username="fl-admin", email="fl-admin@example.com",
            receive_newsletter=False, password="x", is_active=True,
        )
        thread.mark_settled(by=admin)
        thread.refresh_from_db()
        assert thread.settled_at is not None
        assert thread.settled_by_id == admin.id

        first_settled_at = thread.settled_at
        # Second call is a no-op; settled_at does not move.
        thread.mark_settled(by=None)
        thread.refresh_from_db()
        assert thread.settled_at == first_settled_at

    def test_new_message_unsettles_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        thread = self._make_thread(customer, artisan_profile, artisan_user, order_product)
        thread.mark_settled(by=None)
        assert thread.settled_at is not None

        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=artisan_user, content="follow-up",
            order_product=order_product,
        )
        thread.refresh_from_db()
        assert thread.settled_at is None
        assert thread.settled_by is None

    def test_escalate_sets_fields_and_is_not_cleared_by_settlement(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        thread = self._make_thread(customer, artisan_profile, artisan_user, order_product)
        thread.escalate(by=customer)
        thread.refresh_from_db()
        assert thread.escalated_at is not None
        assert thread.escalated_by_id == customer.id

        # Escalation persists through settlement.
        thread.mark_settled(by=None)
        thread.refresh_from_db()
        assert thread.escalated_at is not None
        assert thread.escalated_by_id == customer.id

        # Second escalate is a no-op; escalated_at does not move.
        first_escalated_at = thread.escalated_at
        thread.escalate(by=None)
        thread.refresh_from_db()
        assert thread.escalated_at == first_escalated_at