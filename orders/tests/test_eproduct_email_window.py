# orders/tests/test_eproduct_email_window.py
"""
The e-product download notification must quote a 7-day window, not the
48-hour text that predates the change to timedelta(hours=168).

These tests render the templates directly rather than invoking the
Celery task, so no mail backend or broker is needed.
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.template.loader import render_to_string
from django.utils import timezone


@pytest.fixture
def _make_template_context(db, django_user_model):
    """
    Factory for the minimal context sufficient to render both template
    variants. Parameterised by fulfillment type so the INSTANT and
    CUSTOM fixtures below cannot drift: any field other than
    digital_fulfillment_type is identical by construction.

    The two fixtures exist as named wrappers (template_context,
    custom_template_context) rather than as a parametrised test so the
    INSTANT tests read the same as they did before the CUSTOM branch
    was added. A future third fulfillment type gets a third wrapper,
    not a third copy of this body.
    """
    from category.models import Category
    from store.models import (
        Product, ProductVariation, DigitalDownloadToken,
    )
    from orders.models import Order, OrderProduct
    from decimal import Decimal

    _counter = {"n": 0}

    def _make(*, fulfillment_type: str):
        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"window_user_{n}",
            email=f"window-{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        category = Category.objects.create(
            category_name=f"Window Digital {n}",
            slug=f"window-digital-{n}",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name=f"Window Ebook {n}",
            category=category,
            is_digital=True,
            digital_fulfillment_type=fulfillment_type,
            is_physical=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
        )
        order = Order.objects.create(
            user=user,
            order_number=f"WINDOW-{n:04d}",
            email=user.email,
            is_ordered=True,
            order_status="Processing",
        )
        order_product = OrderProduct.objects.create(
            order=order,
            user=user,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
        )
        token = DigitalDownloadToken.objects.create(
            user=user,
            order_product=order_product,
            # The TTL is chosen by the call site, not the template;
            # any future value is fine here. Use a value that is not
            # the INSTANT default so a test that accidentally asserts
            # on the expires_at timestamp rather than the static copy
            # would visibly disagree with the 7-day assertion.
            expires_at=timezone.now() + timedelta(hours=8760),
        )
        return {
            "token": token,
            "order": order,
            "product": product,
            "user": user,
            "download_url": f"/store/digital/download/{token.id}/",
        }

    return _make


@pytest.fixture
def template_context(_make_template_context):
    """INSTANT-fulfillment context — the original fixture's shape."""
    return _make_template_context(fulfillment_type="INSTANT")


@pytest.fixture
def custom_template_context(_make_template_context):
    """CUSTOM-fulfillment context — same shape, one field changed."""
    return _make_template_context(fulfillment_type="CUSTOM")


class TestEproductEmailWindow:

    def test_html_template_states_seven_days(self, template_context):
        html = render_to_string(
            "emails/eproduct_download_notification.html", template_context,
        )
        assert "7 days" in html
        assert "7 天" in html
        assert "48 hours" not in html
        assert "48 小時" not in html

    def test_plain_template_states_seven_days(self, template_context):
        text = render_to_string(
            "emails/eproduct_download_notification.txt", template_context,
        )
        assert "7 days" in text
        assert "7 天" in text
        assert "48 hours" not in text
        assert "48 小時" not in text

    def test_html_template_states_one_year_for_custom(self, custom_template_context):
        html = render_to_string(
            "emails/eproduct_download_notification.html", custom_template_context,
        )
        assert "one year" in html
        assert "一年" in html
        assert "7 days" not in html
        assert "7 天" not in html

    def test_plain_template_states_one_year_for_custom(self, custom_template_context):
        text = render_to_string(
            "emails/eproduct_download_notification.txt", custom_template_context,
        )
        assert "one year" in text
        assert "一年" in text
        assert "7 days" not in text
        assert "7 天" not in text
