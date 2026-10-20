# creators/tests/test_artisan_orders_dashboard.py
"""
Tests for the artisan Orders dashboard.

Two behaviour contracts are pinned here:

  1. Pending lines are bucketed by product type. Only physical lines
     are dispatchable from this dashboard; CUSTOM digital lines need a
     different fulfilment path (admin-mediated delivery), and INSTANT
     digital lines auto-fulfil at payment time so the artisan has no
     action at all.

  2. dashboard_dispatch_line rejects non-physical lines. Previously the
     view accepted any OrderProduct owned by the artisan and wrote a
     TrackingNumber — which meant an artisan could mark an INSTANT
     digital line as dispatched, flipping is_dispatched without the
     customer ever receiving a download token.

Plus a small structural guard: creators.views must not re-define
artisan_dashboard_context. The sidebar's counters come from
creators.context; a local duplicate would silently drift.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone


@pytest.fixture
def artisan_orders_setup(db, django_user_model):
    """
    One verified artisan, one customer, one Order with three
    OrderProduct lines attributed to the artisan:

      * physical          — dispatchable via tracking-number form
      * CUSTOM digital    — file produced by artisan, delivered via admin
      * INSTANT digital   — auto-fulfilled at payment; no artisan action

    Each line is deliberately is_dispatched=False, matching the shape
    that would result if a mixed-cart checkout settled and the artisan
    then opened their Orders tab.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation
    from orders.models import Order, OrderProduct

    artisan_user = django_user_model.objects.create_user(
        username="artisan_ord",
        email="artisan-ord@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Orders Artisan",
        slug="orders-artisan",
        is_verified=True,
    )
    customer = django_user_model.objects.create_user(
        username="ord_customer",
        email="ord-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )

    cat_physical = Category.objects.create(
        category_name="Physical Cat",
        slug="physical-cat",
        product_format="physical",
    )
    cat_digital = Category.objects.create(
        category_name="Digital Cat",
        slug="digital-cat",
        product_format="e-product",
    )

    physical_product = Product.objects.create(
        product_name="Physical Item",
        category=cat_physical,
        creator=profile,
        is_physical=True,
        is_digital=False,
        is_active=True,
        status="Published",
    )
    physical_variation = ProductVariation.objects.create(
        product=physical_product,
        price=Decimal("10.00"),
        stock=10,
        is_available=True,
    )

    custom_product = Product.objects.create(
        product_name="Custom Digital",
        category=cat_digital,
        creator=profile,
        is_physical=False,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
        is_active=True,
        status="Published",
    )
    custom_variation = ProductVariation.objects.create(
        product=custom_product,
        price=Decimal("20.00"),
        stock=1,
        is_available=True,
    )

    instant_product = Product.objects.create(
        product_name="Instant Digital",
        category=cat_digital,
        creator=profile,
        is_physical=False,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_active=True,
        status="Published",
    )
    instant_variation = ProductVariation.objects.create(
        product=instant_product,
        price=Decimal("30.00"),
        stock=1,
        is_available=True,
    )

    order = Order.objects.create(
        user=customer,
        order_number="ORD-ARTISAN-0001",
        email=customer.email,
        is_ordered=True,
        order_status="Processing",
    )

    physical_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=physical_product,
        product_variation=physical_variation,
        product_price=Decimal("10.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )
    custom_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=custom_product,
        product_variation=custom_variation,
        product_price=Decimal("20.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )
    instant_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=instant_product,
        product_variation=instant_variation,
        product_price=Decimal("30.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )

    return {
        "artisan_user": artisan_user,
        "profile": profile,
        "customer": customer,
        "order": order,
        "physical_line": physical_line,
        "custom_line": custom_line,
        "instant_line": instant_line,
    }


class TestPendingBuckets:

    def test_physical_line_is_in_pending_physical(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        ids = {line.id for line in response.context["pending_physical"]}
        assert chain["physical_line"].id in ids

    def test_custom_digital_line_is_in_pending_custom_digital(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        ids = {line.id for line in response.context["pending_custom_digital"]}
        assert chain["custom_line"].id in ids

    def test_instant_digital_line_is_in_neither_pending_bucket(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        physical_ids = {line.id for line in response.context["pending_physical"]}
        custom_ids = {line.id for line in response.context["pending_custom_digital"]}

        assert chain["instant_line"].id not in physical_ids
        assert chain["instant_line"].id not in custom_ids


class TestDispatchLineGuard:

    def test_physical_line_dispatch_still_works(
        self, client, artisan_orders_setup,
    ):
        """
        Regression guard: the guard added for digital lines must not
        break the physical-line flow.
        """
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["physical_line"]
        assert line.is_dispatched is False

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SF-12345", "carrier": "SF Express"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is True
        assert line.dispatched_at is not None
        assert TrackingNumber.objects.filter(
            order_product=line, tracking_code="SF-12345",
        ).exists()

    def test_custom_digital_line_dispatch_is_rejected(
        self, client, artisan_orders_setup,
    ):
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["custom_line"]

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SHOULD-NOT", "carrier": "X"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is False
        assert line.dispatched_at is None
        assert not TrackingNumber.objects.filter(order_product=line).exists()

    def test_instant_digital_line_dispatch_is_rejected(
        self, client, artisan_orders_setup,
    ):
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["instant_line"]

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SHOULD-NOT", "carrier": "X"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is False
        assert not TrackingNumber.objects.filter(order_product=line).exists()


class TestContextConsolidation:
    """
    Structural guards: the shared context builder lives in
    creators.context, and the sidebar count reflects only actionable
    lines (physical + custom digital), not every undispatched line.
    """

    def test_no_local_artisan_dashboard_context_in_views(self):
        from creators import views

        assert not hasattr(views, "_artisan_dashboard_context"), (
            "Duplicate _artisan_dashboard_context found in creators.views. "
            "Use creators.context.artisan_dashboard_context instead."
        )

    def test_sidebar_count_reflects_only_actionable_lines(
        self, rf, artisan_orders_setup,
    ):
        from creators.context import artisan_dashboard_context

        chain = artisan_orders_setup
        request = rf.get("/")
        request.user = chain["artisan_user"]

        ctx = artisan_dashboard_context(request)
        # physical + custom digital = 2; INSTANT digital is excluded.
        assert ctx["pending_dispatch_count"] == 2
        assert ctx["unread_messages_count"] == 0
        assert ctx["profile"] == chain["profile"]


class TestOrdersPanelTemplate:
    """
    The template must reflect the view's bucket split. Before commit 2
    it still iterated the old `pending_lines` context key, which the
    view no longer provides, so the pending tab rendered empty even
    when actionable lines existed.
    """

    def _get_panel_html(self, client, chain):
        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200
        return response.content.decode()

    def test_physical_line_renders_tracking_form(
        self, client, artisan_orders_setup,
    ):
        html = self._get_panel_html(client, artisan_orders_setup)
        assert 'name="tracking_code"' in html

    def test_custom_digital_line_renders_manage_file_link(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        html = self._get_panel_html(client, chain)
        expected_url = reverse(
            "a_dashboard_product_edit",
            args=[chain["custom_line"].product.id],
        )
        assert expected_url in html

    def test_custom_digital_line_does_not_render_tracking_form(
        self, client, artisan_orders_setup,
    ):
        """
        Scope the assertion to the pending panel: the physical line
        renders a tracking form in the same page, so a naive "no
        tracking_code input exists" check would be wrong. Slice the
        pending panel between its data-panel marker and the next one.
        """
        html = self._get_panel_html(client, artisan_orders_setup)
        start = html.find('data-panel="pending"')
        assert start != -1, "pending tab panel marker missing"
        end = html.find('data-panel="dispatched"', start)
        assert end != -1, "dispatched tab panel marker missing"
        pending_html = html[start:end]

        assert pending_html.count('name="tracking_code"') == 1, (
            "Exactly one tracking form should render in pending — the "
            "physical line's. A second means the custom-digital card "
            "regressed to the old unconditional form."
        )

    def test_instant_digital_line_absent_from_response(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        html = self._get_panel_html(client, chain)
        # The INSTANT line has never been dispatched and is excluded
        # from every panel, so its product name should not appear.
        assert chain["instant_line"].product.product_name not in html