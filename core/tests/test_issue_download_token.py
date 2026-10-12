# core/tests/test_issue_download_token.py
"""
Tests for orders.utils.issue_download_token.

The three customer-purchase paths (complete_zero_due_voucher_order,
confirm_bank_payment_admin_action, capture_paypal_order) all create a
DigitalDownloadToken inline for instant-digital lines, register an
on-commit notification, and flip the line's dispatch flag. This helper
collapses that duplicated block; these tests pin its behaviour so the
three call sites can be swapped over one at a time.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone


@pytest.fixture
def order_with_instant_digital_line(db, django_user_model):
    from category.models import Category
    from store.models import Product, ProductVariation
    from orders.models import Order, OrderProduct

    user = django_user_model.objects.create_user(
        username="token_user",
        email="token-user@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    category = Category.objects.create(
        category_name="Token Digital",
        slug="token-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Token Ebook",
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
        order_number="TOKEN-0001",
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
    return {"order": order, "user": user, "order_product": order_product}


class TestIssueDownloadToken:

    def test_creates_token_bound_to_line_and_order_user(
        self, order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from store.models import DigitalDownloadToken
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = order_with_instant_digital_line

        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        assert isinstance(token, DigitalDownloadToken)
        assert token.order_product == chain["order_product"]
        assert token.user == chain["user"]
        assert token.is_active is True

    def test_expires_at_is_seven_days_out(
        self, order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = order_with_instant_digital_line

        before = timezone.now()
        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])
        after = timezone.now()

        expected_min = before + timedelta(hours=168)
        expected_max = after + timedelta(hours=168)
        assert expected_min <= token.expires_at <= expected_max

    def test_dispatches_notification_on_commit(
        self, order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = order_with_instant_digital_line
        dispatched = []

        with patch.object(
            send_e_product_email_task, "delay",
            side_effect=lambda uid: dispatched.append(uid),
        ):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        assert dispatched == [str(token.id)]

    def test_flips_line_to_dispatched(
        self, order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = order_with_instant_digital_line
        assert chain["order_product"].is_dispatched is False
        assert chain["order_product"].dispatched_at is None

        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                issue_download_token(chain["order_product"])

        chain["order_product"].refresh_from_db()
        assert chain["order_product"].is_dispatched is True
        assert chain["order_product"].dispatched_at is not None

