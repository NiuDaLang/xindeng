# creators/tests/test_artisan_message_fks.py
"""
Unit tests for the two FKs added in backlog 24, commit 1:

  * ArtisanChatMessage.order_product
  * ArtisanAdminMessage.source_chat_message

Both are nullable, on_delete=SET_NULL, and back the "no orphaned
messages" guardrail and the "escalate to platform" link recorded in
the 2026-10-31 handoff §6 and refined in the 2026-11-01 handoff
§6 (member-only boundary).

Each test asserts three things:

  1. A row can be created with the FK unset (the pre-purchase /
     admin-initiated case).
  2. A row can be created with the FK set, and the value round-
     trips through the DB.
  3. Deleting the target flips the FK to None on the surviving
     row (the SET_NULL contract), not CASCADE.

Creation of the target (OrderProduct) needs a lot of fixture
scaffolding because the model is a deep FK chain. This file uses
the project's minimal viable construction: Account → CreatorProfile
→ Category → Product → ProductVariation → Order → OrderProduct.
A future factory refactor can collapse this; the tests below are
deliberately explicit so the FK contract is readable in one file.

The ArtisanChatMessage test's customer and sender Accounts are
plain members. The ArtisanAdminMessage test's sender is the
superuser; per tests/README.md, a "superuser" fixture must set
both is_admin and is_superadmin, which make_superuser does.

Guest case pinned by absence: test_order_product_fk_accepts_null
creates a message with no order_product. The "guest order cannot
be linked" boundary is enforced in the view layer (commit 2's
dropdown filter on order__user=request.user) and pinned by that
view's tests, not here.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from category.models import Category
from creators.models import (
    ArtisanAdminMessage,
    ArtisanChatMessage,
    CreatorProfile,
)
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation
from tests._fakes import make_superuser

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    return make_superuser(username="fk-admin", email="fk-admin@example.com")


@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="fk-customer",
        email="fk-customer@example.com",
        receive_newsletter=False,
        password="a-test-password-1!",
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="fk-artisan",
        email="fk-artisan@example.com",
        receive_newsletter=False,
        password="a-test-password-1!",
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(user=artisan_user)


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="FK Test Category",
        slug="fk-test-category",
    )


@pytest.fixture
def product(category, artisan_profile):
    return Product.objects.create(
        product_name="FK Test Product",
        slug="fk-test-product",
        description="FK test description",
        category=category,
        creator=artisan_profile,
        is_active=True,
        status="Published",
    )


@pytest.fixture
def variation(product):
    return ProductVariation.objects.create(
        product=product,
        price="10.00",
        stock=5,
    )


@pytest.fixture
def order(customer):
    return Order.objects.create(
        user=customer,
        email=customer.email,
        order_number="FK-TEST-0001",
        is_ordered=True,
        order_status="Processing",
    )


@pytest.fixture
def order_product(order, product, variation):
    return OrderProduct.objects.create(
        order=order,
        user=order.user,
        product=product,
        product_variation=variation,
        product_price="10.00",
        quantity=1,
        ordered=True,
    )


# ──────────────────────────────────────────────────────────────
# ArtisanChatMessage.order_product
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanChatMessageOrderProductFK:

    def test_order_product_fk_accepts_null(
        self, artisan_profile, customer,
    ):
        """
        Pre-purchase "Ask this artisan" case: no order behind the
        message. The FK must accept null, and the value must round-
        trip as None.
        """
        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="Pre-purchase question",
            order_product=None,
        )
        msg.refresh_from_db()
        assert msg.order_product is None

    def test_order_product_fk_round_trips(
        self, artisan_profile, customer, order_product,
    ):
        """
        Linked case: the FK is set, the value survives a round-trip,
        and the reverse related_name resolves back to the message.
        """
        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="Question about order line",
            order_product=order_product,
        )
        msg.refresh_from_db()
        assert msg.order_product_id == order_product.id

        # Reverse accessor: OrderProduct.customer_thread_messages
        assert list(order_product.customer_thread_messages.all()) == [msg]

    def test_order_product_fk_is_set_null_on_delete(
        self, artisan_profile, customer, order_product,
    ):
        """
        SET_NULL contract: deleting the OrderProduct leaves the
        message intact with its FK flipped to None. CASCADE would
        destroy the message, which the migration comment argues
        against. Pinned here so a future on_delete change fails
        loudly.
        """
        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="Message that must survive order deletion",
            order_product=order_product,
        )
        order_product.delete()

        msg.refresh_from_db()
        assert msg.order_product is None
        # And the message itself still exists:
        assert ArtisanChatMessage.objects.filter(pk=msg.pk).exists()


# ──────────────────────────────────────────────────────────────
# ArtisanAdminMessage.source_chat_message
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanAdminMessageSourceChatMessageFK:

    def test_source_chat_message_fk_accepts_null(
        self, artisan_profile, admin_user,
    ):
        """
        Admin-initiated thread: no source customer message. The FK
        must accept null.
        """
        msg = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile,
            sender=admin_user,
            content="Admin-initiated message",
            source_chat_message=None,
        )
        msg.refresh_from_db()
        assert msg.source_chat_message is None

    def test_source_chat_message_fk_round_trips(
        self, artisan_profile, customer, admin_user, order_product,
    ):
        """
        Escalation case: a customer↔artisan message is linked as the
        source of an admin escalation. The FK round-trips, and the
        reverse accessor resolves back.
        """
        source = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="Customer message being escalated",
            order_product=order_product,
        )
        escalation = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile,
            sender=admin_user,
            content="Admin escalation of the customer message",
            source_chat_message=source,
        )
        escalation.refresh_from_db()
        assert escalation.source_chat_message_id == source.id

        # Reverse accessor: ArtisanChatMessage.escalated_admin_messages
        assert list(source.escalated_admin_messages.all()) == [escalation]

    def test_source_chat_message_fk_is_set_null_on_delete(
        self, artisan_profile, customer, admin_user, order_product,
    ):
        """
        SET_NULL contract: deleting the source customer message
        leaves the escalation intact with its FK flipped to None.
        """
        source = ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="Source message that will be deleted",
            order_product=order_product,
        )
        escalation = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile,
            sender=admin_user,
            content="Escalation that must survive",
            source_chat_message=source,
        )
        source.delete()

        escalation.refresh_from_db()
        assert escalation.source_chat_message is None
        assert ArtisanAdminMessage.objects.filter(pk=escalation.pk).exists()