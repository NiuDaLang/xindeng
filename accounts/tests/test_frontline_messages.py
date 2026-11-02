# accounts/tests/test_frontline_messages.py
"""
Tests for the `frontline_messages` branch of the dashboard view
(accounts/views.py::dashboard) and the frontline_thread_mark_settled
view — commit 3b, backlog 32.

Covers:
  1. Non-superadmin is redirected to dashboard/main with Access denied.
  2. Superadmin sees the container on a full page load.
  3. Default list hides settled threads.
  4. ?settled=true shows only settled threads.
  5. ?q=<customer> filters correctly.
  6. ?q=<order_number> filters correctly.
  7. mark_settled POST flips settled_at and removes the row from the
     active list (HX response returns the inner partial).
  8. HTMX request targeting #frontline-messages-main returns the inner
     partial, not the container.

Fixtures mirror test_dashboard_artisan_messages.py for consistency.
FrontlineThread tests reuse the artisan/customer/order_product fixture
chain from creators/tests/test_frontline_thread.py, duplicated here so
accounts tests stay self-contained.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from category.models import Category
from creators.models import (
    ArtisanChatMessage,
    CreatorProfile,
    FrontlineThread,
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
    return make_superuser(
        username="fl-admin", email="fl-admin@example.com",
    )


@pytest.fixture
def non_admin(db):
    return Account.objects.create_user(
        username="fl-nonadmin",
        email="fl-nonadmin@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


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
        user=artisan_user, display_name="FL Artisan", is_verified=True,
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


def _seed_thread(customer, artisan_profile, order_product, artisan_user, *, content="seed"):
    """Create a message + return the auto-created FrontlineThread."""
    ArtisanChatMessage.objects.create(
        artisan=artisan_profile, customer=customer, sender=customer,
        content=content, order_product=order_product,
    )
    return FrontlineThread.objects.get()


def _url(**params):
    base = reverse("dashboard", kwargs={"subpage": "frontline_messages"})
    if not params:
        return base
    from urllib.parse import urlencode
    return f"{base}?{urlencode(params)}"


# ──────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFrontlineMessagesAccess:

    def test_non_superadmin_redirected(self, client, non_admin):
        client.force_login(non_admin)
        response = client.get(_url())
        assert response.status_code == 302
        assert response.url == reverse(
            "dashboard", kwargs={"subpage": "main"}
        )

    def test_superadmin_sees_container(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        _seed_thread(customer, artisan_profile, order_product, artisan_user)
        client.force_login(admin_user)
        response = client.get(_url())
        assert response.status_code == 200
        # Container template renders the subpage marker + main region.
        assert "dashboard_frontline_messages" in response.content.decode()
        assert "frontline-messages-main" in response.content.decode()


@pytest.mark.django_db
class TestFrontlineMessagesFilter:

    def test_default_hides_settled(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = _seed_thread(customer, artisan_profile, order_product, artisan_user)
        thread.mark_settled(by=admin_user)

        client.force_login(admin_user)
        response = client.get(_url())  # default settled=false
        rows = response.context["thread_rows"]
        assert thread.id not in [t.id for t in rows]
        assert response.context["settled_filter"] is False

    def test_settled_true_shows_only_settled(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = _seed_thread(customer, artisan_profile, order_product, artisan_user)
        thread.mark_settled(by=admin_user)

        client.force_login(admin_user)
        response = client.get(_url(settled="true"))
        rows = response.context["thread_rows"]
        assert thread.id in [t.id for t in rows]
        assert response.context["settled_filter"] is True

    def test_search_by_customer_username(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        _seed_thread(customer, artisan_profile, order_product, artisan_user)

        client.force_login(admin_user)
        hit = client.get(_url(q="fl-customer"))
        miss = client.get(_url(q="nobody-matches"))

        assert len(hit.context["thread_rows"]) == 1
        assert len(miss.context["thread_rows"]) == 0

    def test_search_by_order_number(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        _seed_thread(customer, artisan_profile, order_product, artisan_user)

        client.force_login(admin_user)
        hit = client.get(_url(q="FL-ORDER-0001"))
        assert len(hit.context["thread_rows"]) == 1


@pytest.mark.django_db
class TestFrontlineMarkSettled:

    def test_mark_settled_flips_and_removes_from_active(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = _seed_thread(customer, artisan_profile, order_product, artisan_user)
        assert thread.settled_at is None

        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_thread_mark_settled", args=[thread.id]),
            {"action": "settle", "settled_filter": "false"},
        )
        assert response.status_code == 200

        thread.refresh_from_db()
        assert thread.settled_at is not None
        assert thread.settled_by_id == admin_user.id

        # The returned inner partial is the *active* list — the
        # just-settled thread should not appear in it.
        body = response.content.decode()
        assert f"thread={thread.id}" not in body
        # HX-Trigger carries the settlement event.
        trigger = json.loads(response["HX-Trigger"])
        assert "frontlineThreadSettled" in trigger
        assert trigger["frontlineThreadSettled"]["thread_id"] == thread.id


@pytest.mark.django_db
class TestFrontlineHtmxDispatch:

    def test_htmx_target_returns_inner_partial_not_container(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        _seed_thread(customer, artisan_profile, order_product, artisan_user)

        client.force_login(admin_user)
        response = client.get(
            _url(),
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="frontline-messages-main",
        )
        assert response.status_code == 200
        body = response.content.decode()

        # Distinguish inner from container by the *presence of the
        # wrapper elements*, not by the string "frontline-messages-main"
        # — that string appears as an hx-target attribute in both.
        #
        #   Container:  <div id="dashboard_frontline_messages" ...>
        #                 <main id="frontline-messages-main">…</main>
        #               </div>
        #   Inner:      <div class="grid grid-cols-1 lg:grid-cols-[320px_1fr] ...">
        #                 …
        #               </div>
        assert 'id="dashboard_frontline_messages"' not in body
        assert 'id="frontline-messages-main"' not in body
        # Inner partial's grid wrapper is present.
        assert "grid-cols-1 lg:grid-cols-[320px_1fr]" in body

    def test_full_page_load_returns_container(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        """
        Companion to the test above: a full (non-HTMX) GET renders the
        container, which *does* wrap the inner in the two wrapper
        elements. Pins both sides of the dispatch so a future refactor
        can't drift one without the other.
        """
        _seed_thread(customer, artisan_profile, order_product, artisan_user)

        client.force_login(admin_user)
        response = client.get(_url())  # no HX headers
        assert response.status_code == 200
        body = response.content.decode()

        assert 'id="dashboard_frontline_messages"' in body
        assert 'id="frontline-messages-main"' in body
        assert "grid-cols-1 lg:grid-cols-[320px_1fr]" in body
        