# core/tests/test_eproduct_email_window.py
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
def template_context(db, django_user_model):
    """
    Minimal context sufficient to render both template variants. The
    templates dereference token.expires_at, token.order_product.*,
    product.product_name, order.order_number, and user.username.
    """
    from category.models import Category
    from store.models import (
        Product, ProductVariation, DigitalDownloadToken,
    )
    from orders.models import Order, OrderProduct
    from decimal import Decimal

    user = django_user_model.objects.create_user(
        username="window_user",
        email="window@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    category = Category.objects.create(
        category_name="Window Digital",
        slug="window-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Window Ebook",
        category=category,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
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
        order_number="WINDOW-0001",
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
        expires_at=timezone.now() + timedelta(hours=168),
    )
    return {
        "token": token,
        "order": order,
        "product": product,
        "user": user,
        "download_url": f"/store/digital/download/{token.id}/",
    }


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