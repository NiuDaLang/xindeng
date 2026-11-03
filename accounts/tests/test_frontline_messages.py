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
    return FrontlineThread.objects.get(order_product=order_product)


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


@pytest.mark.django_db
class TestFrontlineAdminComposer:
    """
    Commit 3c: admin reply on escalated threads. Gate order matters
    (superadmin → thread exists → thread escalated). The escalated
    gate is 403-status but HTMX-200-body — the swap still needs the
    refreshed inner or the admin's page goes stale.
    """

    def _make_escalated_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        thread.escalate(by=customer)
        thread.refresh_from_db()
        return thread

    def test_no_composer_on_non_escalated_thread(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        """The composer form is absent from a thread that has not
        been escalated; only the read-only notice renders."""
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        assert thread.escalated_at is None

        client.force_login(admin_user)
        response = client.get(
            _url(thread=thread.id, settled="false"),
        )
        assert response.status_code == 200
        body = response.content.decode()
        # Composer form action is absent.
        assert (
            f'/accounts/frontline_threads/{thread.id}/send/'
            not in body
        )
        assert "Read-only until escalated" in body

    def test_composer_renders_on_escalated_thread(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = self._make_escalated_thread(
            customer, artisan_profile, artisan_user, order_product,
        )

        client.force_login(admin_user)
        response = client.get(
            _url(thread=thread.id, settled="false"),
        )
        assert response.status_code == 200
        body = response.content.decode()
        assert (
            f'/accounts/frontline_threads/{thread.id}/send/'
            in body
        )
        # The read-only notice is gone.
        assert "Read-only until escalated" not in body

    def test_post_creates_message_with_correct_shape(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        from creators.models import ArtisanChatMessage

        thread = self._make_escalated_thread(
            customer, artisan_profile, artisan_user, order_product,
        )
        before = ArtisanChatMessage.objects.filter(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        ).count()

        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_message_send", args=[thread.id]),
            {
                "content": "Reviewing this now.",
                "settled_filter": "false",
                "q": "",
            },
        )
        assert response.status_code == 200

        after_qs = ArtisanChatMessage.objects.filter(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        )
        assert after_qs.count() == before + 1

        new_msg = after_qs.order_by("-created_at").first()
        assert new_msg.sender_id == admin_user.id
        assert new_msg.content == "Reviewing this now."
        assert new_msg.is_read is False  # artisan's unread
        assert new_msg.order_product_id == order_product.id

        # Thread timestamp advanced and the settled flag (if any)
        # was cleared by the creators signal.
        thread.refresh_from_db()
        assert thread.last_message_at == new_msg.created_at
        assert thread.settled_at is None

        # HX-Trigger carries the event.
        trigger = json.loads(response["HX-Trigger"])
        assert "frontlineMessageSent" in trigger
        assert trigger["frontlineMessageSent"]["thread_id"] == thread.id

    def test_post_refuses_on_non_escalated_thread(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        """
        Not escalated → 200-body with the flash rendered by the
        alerts include inside the inner partial. No message is
        created. The status is 200 (not 403) because HTMX needs a
        swappable body to actually render the flash — a 403 would
        leave the swap a no-op and the admin staring at their
        stale page.

        The refusal message reaches the user via two paths:
          * The messages framework flash (rendered by the alerts
            include at the top of this partial).
          * Not applicable here — composer_error is only rendered
            inside the is_escalated branch, so it never fires for
            this gate. The alerts flash is the only surface.
        """
        from creators.models import ArtisanChatMessage

        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        assert thread.escalated_at is None
        before = ArtisanChatMessage.objects.filter(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        ).count()

        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_message_send", args=[thread.id]),
            {"content": "should not land", "settled_filter": "false"},
        )

        assert response.status_code == 200
        body = response.content.decode()
        # Flash surfaced by the alerts include inside the inner.
        assert (
            "not escalated" in body.lower()
            or "未升級" in body
        )

        # And no message landed.
        assert ArtisanChatMessage.objects.filter(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        ).count() == before


@pytest.mark.django_db
class TestFrontlineEscalate:
    """
    Commit 3d: customer + artisan escalate buttons.

    Customer POSTs thread_id, artisan POSTs customer_id. The
    artisan-side fan-out (escalate all non-settled threads with
    the customer) needs its own pin because a single Post() call
    flips more than one row in that branch.
    """

    def _escalate_url(self):
        return reverse("escalate_frontline_thread")

    def test_customer_can_escalate_own_thread(
        self, client, customer, artisan_profile, artisan_user,
        order_product,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        assert thread.escalated_at is None

        client.force_login(customer)
        response = client.post(
            self._escalate_url(),
            {"thread_id": thread.id},
        )
        # Redirect back to customer_thread.
        assert response.status_code == 302
        expected = reverse("customer_thread", kwargs={"artisan_slug": artisan_profile.slug})
        assert response.url.startswith(expected)
        assert f"order_product={order_product.id}" in response.url

        thread.refresh_from_db()
        assert thread.escalated_at is not None
        assert thread.escalated_by_id == customer.id

    def test_artisan_can_escalate_thread(
        self, client, customer, artisan_user, artisan_profile,
        order_product,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        assert thread.escalated_at is None

        client.force_login(artisan_user)
        response = client.post(
            self._escalate_url(),
            {"customer_id": customer.id},
        )
        assert response.status_code == 302
        expected = reverse("a_dashboard_messages")
        assert response.url.startswith(expected)
        assert f"customer={customer.id}" in response.url

        thread.refresh_from_db()
        assert thread.escalated_at is not None
        assert thread.escalated_by_id == artisan_user.id

    def test_escalation_is_idempotent(
        self, client, customer, artisan_profile, artisan_user,
        order_product,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )

        client.force_login(customer)
        client.post(self._escalate_url(), {"thread_id": thread.id})
        thread.refresh_from_db()
        first_escalated_at = thread.escalated_at
        assert first_escalated_at is not None

        # Second POST: no state change.
        response = client.post(
            self._escalate_url(), {"thread_id": thread.id},
        )
        assert response.status_code == 302
        thread.refresh_from_db()
        assert thread.escalated_at == first_escalated_at

    def test_non_participant_gets_404(
        self, client, customer, artisan_profile, artisan_user,
        order_product, db,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )

        other_customer = Account.objects.create_user(
            username="fl-other",
            email="fl-other@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(other_customer)
        response = client.post(
            self._escalate_url(), {"thread_id": thread.id},
        )
        assert response.status_code == 404

        # State unchanged.
        thread.refresh_from_db()
        assert thread.escalated_at is None

    def test_artisan_escalates_all_non_settled_threads_with_customer(
        self, client, customer, artisan_user, artisan_profile,
        order_product, product, variation, order,
    ):
        """
        Two threads between the same artisan and customer (two
        different order lines). Artisan's POST with customer_id
        escalates both.
        """
        from orders.models import OrderProduct

        thread_a = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )

        # Second order line, second thread.
        line_b = OrderProduct.objects.create(
            order=order, user=order.user,
            product=product, product_variation=variation,
            product_price="10.00", quantity=1, ordered=True,
            fulfilled_by=artisan_profile,
        )
        thread_b = _seed_thread(
            customer, artisan_profile, line_b, artisan_user,
        )

        assert thread_a.id != thread_b.id

        client.force_login(artisan_user)
        response = client.post(
            self._escalate_url(),
            {"customer_id": customer.id},
        )
        assert response.status_code == 302

        thread_a.refresh_from_db()
        thread_b.refresh_from_db()
        assert thread_a.escalated_at is not None
        assert thread_b.escalated_at is not None
        assert thread_a.escalated_by_id == artisan_user.id
        assert thread_b.escalated_by_id == artisan_user.id

    def test_artisan_escalate_when_all_already_escalated_is_noop(
        self, client, customer, artisan_user, artisan_profile,
        order_product,
    ):
        thread = _seed_thread(
            customer, artisan_profile, order_product, artisan_user,
        )
        thread.escalate(by=customer)
        thread.refresh_from_db()
        first = thread.escalated_at

        client.force_login(artisan_user)
        response = client.post(
            self._escalate_url(),
            {"customer_id": customer.id},
        )
        # Still redirects back to the artisan messages panel.
        assert response.status_code == 302
        expected = reverse("a_dashboard_messages")
        assert response.url.startswith(expected)
        assert f"customer={customer.id}" in response.url

        thread.refresh_from_db()
        assert thread.escalated_at == first
        # The customer's escalation is preserved (not overwritten
        # by the artisan's already-noop call).
        assert thread.escalated_by_id == customer.id