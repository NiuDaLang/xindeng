# orders/tests/test_issue_download_token.py
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
from django.template.loader import render_to_string

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


@pytest.fixture
def guest_order_with_instant_digital_line(db):
    """
    Guest counterpart to order_with_instant_digital_line: Order.user and
    OrderProduct.user are both None, matching the shape produced by
    complete_zero_due_voucher_order, confirm_bank_payment_admin_action,
    and capture_paypal_order for a guest checkout.

    Order.email is set because the guest-purchase contract requires it —
    it is the evidence of purchase and the only identity anchor the
    download gate can fall back to.
    """
    from category.models import Category
    from store.models import Product, ProductVariation
    from orders.models import Order, OrderProduct

    category = Category.objects.create(
        category_name="Guest Token Digital",
        slug="guest-token-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Guest Token Ebook",
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
        user=None,
        order_number="TOKEN-GUEST-0001",
        email="guest-buyer@example.com",
        is_ordered=True,
        order_status="Processing",
    )
    order_product = OrderProduct.objects.create(
        order=order,
        user=None,
        product=product,
        product_variation=variation,
        product_price=Decimal("10.00"),
        quantity=1,
        ordered=True,
    )
    return {
        "order": order,
        "order_product": order_product,
        "product": product,
    }


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
        assert token.email == chain["order"].email

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

    def test_guest_order_creates_token_with_user_none_and_email_snapshot(
        self, guest_order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from store.models import DigitalDownloadToken
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = guest_order_with_instant_digital_line

        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        assert isinstance(token, DigitalDownloadToken)
        assert token.user_id is None
        assert token.email == "guest-buyer@example.com"
        assert token.is_active is True

    def test_email_snapshot_survives_later_order_email_edit(
        self, guest_order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        """
        token.email is a snapshot taken at issue time, not a live
        reference. If the order's email is corrected after issue — a
        typo fix by customer service, say — the token must keep the
        original address, otherwise the gate's identity anchor silently
        drifts away from what was actually delivered.
        """
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = guest_order_with_instant_digital_line

        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        chain["order"].email = "corrected@example.com"
        chain["order"].save(update_fields=["email"])

        token.refresh_from_db()
        assert token.email == "guest-buyer@example.com"


class TestGuestSalutationFallback:
    """
    The e-product notification templates use
    {{ user.username|default:order.email }}. For a guest token, user is
    None, so the |default: filter must fall back to order.email or the
    salutation renders blank.

    This works today by accident of the filter. It is easy to break in a
    future template edit that drops |default:order.email. These tests
    pin the behaviour rather than the implementation.
    """

    def _render(self, template_name, chain, token):
        return render_to_string(
            template_name,
            {
                "token": token,
                "order": chain["order"],
                "product": chain["product"],
                "user": None,
                "download_url": f"/store/digital/download/{token.id}/",
            },
        )

    def test_html_salutation_shows_order_email_for_guest_token(
        self, guest_order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = guest_order_with_instant_digital_line
        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        html = self._render(
            "emails/eproduct_download_notification.html", chain, token,
        )
        assert "Dear guest-buyer@example.com" in html

    def test_txt_salutation_shows_order_email_for_guest_token(
        self, guest_order_with_instant_digital_line, django_capture_on_commit_callbacks,
    ):
        from orders.utils import issue_download_token
        from orders.tasks import send_e_product_email_task

        chain = guest_order_with_instant_digital_line
        with patch.object(send_e_product_email_task, "delay", lambda uid: None):
            with django_capture_on_commit_callbacks(execute=True):
                token = issue_download_token(chain["order_product"])

        text = self._render(
            "emails/eproduct_download_notification.txt", chain, token,
        )
        assert "Dear guest-buyer@example.com" in text