# creators/tests/test_artisan_message_images.py
"""
Image-attachment support on ArtisanChatMessage. Commit 3f, backlog
24 §images.

Six tests, one per failure mode worth pinning:

  1. Model: image field exists, is nullable, upload_to is
     "artisan_chat_images/", blank=True.
  2. Customer-side send: sending with an image and no content
     succeeds (the widened content-OR-image guard).
  3. Customer-side send: sending with neither content nor image
     rejects with the empty-message flash.
  4. Artisan-side send: same pair (image succeeds, empty rejects).
  5. Admin composer: image-only message on an escalated thread
     succeeds.
  6. Integration: an image-only message still fires the
     creators.signals.maintain_frontline_thread signal — the
     thread's last_message_at advances. This is the load-bearing
     check that the widened guard did not accidentally skip the
     signal path (which fires on every save, independent of
     content shape, but is worth pinning explicitly since the
     empty-content guard is the only branch that could
     accidentally suppress it if the create is bypassed).

Fixtures mirror creators/tests/test_customer_thread.py and
accounts/tests/test_frontline_messages.py, duplicated so this file
is self-contained.
"""

import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

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
    return make_superuser(username="ami-admin", email="ami-admin@example.com")


@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="ami-customer",
        email="ami-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="ami-artisan",
        email="ami-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user, display_name="AMI Artisan", is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="AMI Category", slug="ami-category",
    )


@pytest.fixture
def product(category, artisan_profile):
    return Product.objects.create(
        product_name="AMI Product", slug="ami-product",
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
        order_number="AMI-ORDER-0001",
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


def _png_upload(name="preview.png", size=(300, 300), color=(10, 100, 200)):
    """A small PNG SimpleUploadedFile for image-attachment tests."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return SimpleUploadedFile(
        name, buf.getvalue(), content_type="image/png",
    )


# ──────────────────────────────────────────────────────────────
# Test 1: model field shape
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_artisanchatmessage_image_field_shape():
    from django.db.models import ImageField

    field = ArtisanChatMessage._meta.get_field("image")
    assert isinstance(field, ImageField)
    assert field.null is True
    assert field.blank is True
    assert field.upload_to == "artisan_chat_images/"


# ──────────────────────────────────────────────────────────────
# Tests 2 & 3: customer-side send
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomerThreadImageSend:

    def _send_url(self, artisan_profile):
        return reverse(
            "customer_thread_send",
            kwargs={"artisan_slug": artisan_profile.slug},
        )

    def test_image_only_message_succeeds(
        self, client, customer, artisan_profile, order_product,
    ):
        client.force_login(customer)
        response = client.post(
            self._send_url(artisan_profile),
            {
                "content": "",
                "image": _png_upload(),
                "order_product_id": order_product.id,
            },
        )
        # Redirect back to the thread.
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        )
        assert msg.content == ""
        assert msg.image
        assert msg.image.name.startswith("artisan_chat_images/")
        assert msg.image.name.endswith(".png")

    def test_neither_content_nor_image_rejects(
        self, client, customer, artisan_profile, order_product,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(customer)
        response = client.post(
            self._send_url(artisan_profile),
            {
                "content": "",
                "order_product_id": order_product.id,
            },
        )
        # Redirect (empty-message path uses messages.error + redirect).
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before


# ──────────────────────────────────────────────────────────────
# Test 4: artisan-side send
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanPanelImageSend:

    def _send_url(self, customer):
        return reverse(
            "a_dashboard_messages_send", args=[customer.id],
        )

    def test_image_only_message_succeeds(
        self, client, customer, artisan_user, artisan_profile,
    ):
        client.force_login(artisan_user)
        response = client.post(
            self._send_url(customer),
            {"content": "", "image": _png_upload()},
        )
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(
            artisan=artisan_profile,
            customer=customer,
            sender=artisan_user,
        )
        assert msg.content == ""
        assert msg.image

    def test_neither_content_nor_image_rejects(
        self, client, customer, artisan_user, artisan_profile,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(artisan_user)
        response = client.post(
            self._send_url(customer),
            {"content": ""},
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before


# ──────────────────────────────────────────────────────────────
# Test 5: admin composer (escalated thread)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFrontlineAdminImageSend:

    def _escalated_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="seed", order_product=order_product,
        )
        thread = FrontlineThread.objects.get(order_product=order_product)
        thread.escalate(by=customer)
        return thread

    def test_image_only_admin_message_succeeds(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = self._escalated_thread(
            customer, artisan_profile, artisan_user, order_product,
        )
        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_message_send", args=[thread.id]),
            {
                "content": "",
                "image": _png_upload(),
                "settled_filter": "false",
            },
        )
        assert response.status_code == 200

        admin_msg = ArtisanChatMessage.objects.filter(
            sender=admin_user,
        ).order_by("-created_at").first()
        assert admin_msg is not None
        assert admin_msg.content == ""
        assert admin_msg.image


# ──────────────────────────────────────────────────────────────
# Test 6: signal still fires on image-only messages
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_image_only_message_advances_frontline_thread_timestamp(
    client, customer, artisan_profile, artisan_user, order_product,
):
    """
    The empty-content guard lives in the *view*, not the *create*.
    An image-only message reaches the create with a non-empty image
    field and empty content — same save path, same signal. Pin that
    the thread's last_message_at advances.
    """
    # Seed a first message so the thread exists (or use the auto
    # get_or_create on the image-only message — the signal fires
    # whether or not the thread already exists).
    client.force_login(customer)
    response = client.post(
        reverse(
            "customer_thread_send",
            kwargs={"artisan_slug": artisan_profile.slug},
        ),
        {
            "content": "",
            "image": _png_upload(),
            "order_product_id": order_product.id,
        },
    )
    assert response.status_code == 302

    thread = FrontlineThread.objects.get(order_product=order_product)
    image_only_msg = ArtisanChatMessage.objects.filter(
        customer=customer, order_product=order_product,
    ).latest("created_at")
    assert thread.last_message_at == image_only_msg.created_at