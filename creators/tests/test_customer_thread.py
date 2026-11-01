# creators/tests/test_customer_thread.py
"""
Tests for the customer-side customer↔artisan messaging view
(backlog 24, commit 2).

Two views under test:

  * creators.views.customer_thread (GET) — thread render.
  * creators.views.customer_thread_send (POST) — message creation.

Gates pinned here:
  1. Login required (both views).
  2. Member-only: the customer must have at least one CUSTOM order
     line fulfilled by this artisan. Guest orders (Order.user is
     None) never satisfy this; that boundary is what makes the
     feature registered-member-only.
  3. The dropdown offers CUSTOM-only lines. A physical or INSTANT
     order line with this artisan does not appear.
  4. The forged-POST path: a POST naming an OrderProduct the
     customer does not own (e.g. another customer's line) is
     rejected with 404, not silently accepted.
  5. The flip symmetry: opening the customer thread flips incoming
     unread to read, but not the customer's own outbound sends
     (per handoff §A2 — the .exclude is on the reader's side).
  6. order_product is round-tripped through the message: a send
     with order_product_id links the row; a send without it leaves
     the FK null.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from category.models import Category
from creators.models import ArtisanChatMessage, CreatorProfile
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation
from tests._fakes import make_superuser

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="ct-artisan",
        email="ct-artisan@example.com",
        receive_newsletter=False,
        password="a-test-password-1!",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user,
        display_name="CT Artisan",
        is_verified=True,
    )


@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="ct-customer",
        email="ct-customer@example.com",
        receive_newsletter=False,
        password="a-test-password-1!",
        is_active=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="CT Category",
        slug="ct-category",
    )


@pytest.fixture
def custom_product(category, artisan_profile):
    return Product.objects.create(
        product_name="CT Custom Product",
        slug="ct-custom-product",
        description="CT test",
        category=category,
        creator=artisan_profile,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
        is_active=True,
        status="Published",
    )


@pytest.fixture
def custom_variation(custom_product):
    return ProductVariation.objects.create(
        product=custom_product,
        price="100.00",
        stock=1,
    )


@pytest.fixture
def instant_product(category, artisan_profile):
    return Product.objects.create(
        product_name="CT Instant Product",
        slug="ct-instant-product",
        description="CT test",
        category=category,
        creator=artisan_profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_active=True,
        status="Published",
    )


@pytest.fixture
def instant_variation(instant_product):
    return ProductVariation.objects.create(
        product=instant_product,
        price="50.00",
        stock=1,
    )


@pytest.fixture
def customer_order(customer):
    return Order.objects.create(
        user=customer,
        email=customer.email,
        order_number="CT-ORDER-0001",
        is_ordered=True,
        order_status="Processing",
    )


@pytest.fixture
def custom_line(customer_order, custom_product, custom_variation, artisan_profile):
    return OrderProduct.objects.create(
        order=customer_order,
        user=customer_order.user,
        product=custom_product,
        product_variation=custom_variation,
        product_price="100.00",
        quantity=1,
        ordered=True,
        fulfilled_by=artisan_profile,
    )


@pytest.fixture
def instant_line(customer_order, instant_product, instant_variation, artisan_profile):
    return OrderProduct.objects.create(
        order=customer_order,
        user=customer_order.user,
        product=instant_product,
        product_variation=instant_variation,
        product_price="50.00",
        quantity=1,
        ordered=True,
        fulfilled_by=artisan_profile,
    )


@pytest.fixture
def thread_url(artisan_profile):
    return reverse("customer_thread", kwargs={"artisan_slug": artisan_profile.slug})


@pytest.fixture
def send_url(artisan_profile):
    return reverse("customer_thread_send", kwargs={"artisan_slug": artisan_profile.slug})


# ──────────────────────────────────────────────────────────────
# customer_thread (GET)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomerThreadGet:

    def test_anonymous_redirected_to_login(self, client, thread_url, custom_line):
        response = client.get(thread_url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_member_without_line_gets_404(
        self, client, thread_url, customer, artisan_profile,
    ):
        client.force_login(customer)
        response = client.get(thread_url)
        assert response.status_code == 404

    def test_member_with_only_instant_line_gets_404(
        self, client, thread_url, customer, instant_line,
    ):
        """INSTANT-only does not open the thread. CUSTOM-only, per memo."""
        client.force_login(customer)
        response = client.get(thread_url)
        assert response.status_code == 404

    def test_member_with_custom_line_sees_thread(
        self, client, thread_url, customer, custom_line,
    ):
        client.force_login(customer)
        response = client.get(thread_url)
        assert response.status_code == 200
        assert "chat_messages" in response.context
        # Dropdown offers exactly the one CUSTOM line.
        available = list(response.context["available_lines"])
        assert len(available) == 1
        assert available[0].id == custom_line.id

    def test_thread_flips_incoming_unread_to_read(
        self, client, thread_url, customer, artisan_user,
        artisan_profile, custom_line,
    ):
        """
        Opening the thread flips admin-authored (here: artisan-authored)
        unread to read. The .exclude(sender=request.user) means the
        customer's own outbound sends are not flipped — those are the
        artisan's unread, not the customer's.

        Seeding: one artisan-authored (incoming) unread, one
        customer-authored (outbound) unread.
        """
        incoming = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=artisan_user, content="incoming from artisan",
            is_read=False, order_product=custom_line,
        )
        outbound = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="outbound from customer",
            is_read=False, order_product=custom_line,
        )

        client.force_login(customer)
        client.get(thread_url)

        incoming.refresh_from_db()
        outbound.refresh_from_db()
        assert incoming.is_read is True
        assert outbound.is_read is False


# ──────────────────────────────────────────────────────────────
# customer_thread_send (POST)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomerThreadSend:

    def test_anonymous_redirected_to_login(self, client, send_url, custom_line):
        response = client.post(send_url, {"content": "hello"})
        assert response.status_code == 302
        assert "/accounts/login/" in response.url

    def test_member_without_line_gets_404(
        self, client, send_url, customer,
    ):
        client.force_login(customer)
        response = client.post(send_url, {"content": "hello"})
        assert response.status_code == 404

    def test_send_creates_message_with_order_product(
        self, client, send_url, customer, custom_line,
    ):
        client.force_login(customer)
        response = client.post(send_url, {
            "content": "Question about my order",
            "order_product_id": str(custom_line.id),
        })
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(
            artisan=custom_line.fulfilled_by,
            customer=customer,
        )
        assert msg.sender_id == customer.id
        assert msg.is_read is False
        assert msg.order_product_id == custom_line.id

    def test_send_without_order_product_leaves_fk_null(
        self, client, send_url, customer, custom_line,
    ):
        client.force_login(customer)
        response = client.post(send_url, {"content": "Pre-purchase"})
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(customer=customer)
        assert msg.order_product is None

    def test_send_with_foreign_order_product_gets_404(
        self, client, send_url, customer, custom_line,
        category, artisan_profile,
    ):
        """
        Forged POST naming another customer's order line (or a line
        on this artisan that isn't this customer's) is rejected with
        404, not silently accepted with the FK cleared.
        """
        other_customer = Account.objects.create_user(
            username="ct-other", email="ct-other@example.com",
            receive_newsletter=False, password="x",
            is_active=True,
        )
        other_order = Order.objects.create(
            user=other_customer, email=other_customer.email,
            order_number="CT-ORDER-OTHER", is_ordered=True,
        )
        other_line = OrderProduct.objects.create(
            order=other_order, user=other_customer,
            product=custom_line.product,
            product_variation=custom_line.product_variation,
            product_price="100.00", quantity=1, ordered=True,
            fulfilled_by=artisan_profile,
        )

        client.force_login(customer)
        response = client.post(send_url, {
            "content": "forged post",
            "order_product_id": str(other_line.id),
        })
        assert response.status_code == 404
        # No message created.
        assert not ArtisanChatMessage.objects.filter(customer=customer).exists()

    def test_send_with_empty_content_does_not_create(
        self, client, send_url, customer, custom_line,
    ):
        client.force_login(customer)
        response = client.post(send_url, {
            "content": "   ",
            "order_product_id": str(custom_line.id),
        })
        # Redirects back, error message added; no row created.
        assert response.status_code == 302
        assert not ArtisanChatMessage.objects.filter(customer=customer).exists()