# store/tests/test_vault_upload_review_queue.py
"""
Pins the admin review queue's listing of order-product-scoped
ArtisanVaultUpload rows.

The 2026-10-21 browser pass confirmed that the queue lists CUSTOM-scoped
uploads (see HANDOFF_2026-10-21, "Browser pass — all seven steps passed",
step 1). The 2026-10-23 session re-verified it. Neither session added a
test, so a future edit to the queue's queryset could drop order-product-
scoped rows without failing anything.

The action-view tests in test_vault_upload_approval.py exercise the
approve/reject gates. This file exercises the *listing* view — a
different query path, and the one the admin uses to find the row before
acting on it.

The queue queryset today is:

    ArtisanVaultUpload.objects
        .filter(status="PENDING")
        .select_related("artisan", "product", "variation",
                        "variation__product")
        .order_by("submitted_at")

No scope filter. This file pins that shape — a future edit that adds
`.filter(order_product__isnull=True)` (to "clean up" the queue) or
`.filter(variation__product__creator=...)` (to "scope it to the
artisan") would silently drop CUSTOM rows without failing anything
else, because no other test exercises this listing path.
"""
from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse

from tests._fakes import make_superuser


# ──────────────────────────────────────────────────────────────────
# Fixture
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def review_queue_setup(db, django_user_model):
    """
    Builds a superuser, an artisan, a digital product, a variation, an
    order, and two PENDING ArtisanVaultUpload rows:

      - one variation-scoped (order_product=None), the INSTANT path
      - one order-product-scoped (order_product set), the CUSTOM path

    Both rows are PENDING. Both must appear in the review queue.
    The two rows share the same variation and product — the queue
    distinguishes them by their `order_product` FK, not by product or
    variation. The template does not render anything scope-specific,
    so the test asserts on the distinguishable `original_filename`
    field, not on a scope badge.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import (
        Product, ProductVariation, ArtisanVaultUpload,
    )
    from orders.models import Order, OrderProduct

    superuser = make_superuser(
        username="queue_admin",
        email="queue-admin@example.com",
    )

    artisan_user = django_user_model.objects.create_user(
        username="queue_artisan",
        email="queue-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    artisan = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Queue Artisan",
        slug="queue-artisan",
        is_verified=True,
    )

    category = Category.objects.create(
        category_name="Queue Digital",
        slug="queue-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Queue Ebook",
        category=category,
        creator=artisan,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
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

    buyer = django_user_model.objects.create_user(
        username="queue_buyer",
        email="queue-buyer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    order = Order.objects.create(
        user=buyer,
        order_number="QUEUE-0001",
        email=buyer.email,
        is_ordered=True,
        order_status="Processing",
    )
    order_product = OrderProduct.objects.create(
        order=order,
        user=buyer,
        product=product,
        product_variation=variation,
        product_price=Decimal("10.00"),
        quantity=1,
        ordered=True,
    )

    variation_scoped = ArtisanVaultUpload.objects.create(
        artisan=artisan,
        product=product,
        variation=variation,
        order_product=None,
        storage_kind="LOCAL",
        staged_filename="queue-variation-scoped.pdf",
        original_filename="instant-book.pdf",
        file_size=128,
        checksum="0" * 64,
        status="PENDING",
    )
    order_product_scoped = ArtisanVaultUpload.objects.create(
        artisan=artisan,
        product=product,
        variation=variation,
        order_product=order_product,
        storage_kind="LOCAL",
        staged_filename="queue-order-product-scoped.pdf",
        original_filename="custom-book.pdf",
        file_size=128,
        checksum="1" * 64,
        status="PENDING",
    )

    return {
        "superuser": superuser,
        "artisan": artisan,
        "variation": variation,
        "order_product": order_product,
        "variation_scoped": variation_scoped,
        "order_product_scoped": order_product_scoped,
    }


def _review_queue_url() -> str:
    return reverse("dashboard", args=["product_review"])


# ──────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────

class TestReviewQueueListsBothScopes:

    def test_variation_scoped_pending_upload_appears_in_queue(
        self, client, review_queue_setup,
    ):
        """
        The INSTANT path. Already implicitly covered by the browser
        pass; pinned here as the baseline the CUSTOM assertion reads
        against.
        """
        client.force_login(review_queue_setup["superuser"])
        response = client.get(_review_queue_url())
        assert response.status_code == 200
        body = response.content.decode()
        assert "instant-book.pdf" in body

    def test_order_product_scoped_pending_upload_appears_in_queue(
        self, client, review_queue_setup,
    ):
        """
        The CUSTOM path. This is the assertion the 2026-10-21 and
        2026-10-23 browser passes made manually. A future edit to the
        queue's queryset that adds .filter(order_product__isnull=True),
        narrows by variation__product__creator, or otherwise drops
        order-product-scoped rows, fails here.
        """
        client.force_login(review_queue_setup["superuser"])
        response = client.get(_review_queue_url())
        assert response.status_code == 200
        body = response.content.decode()
        assert "custom-book.pdf" in body

    def test_both_scopes_appear_together_in_one_render(
        self, client, review_queue_setup,
    ):
        """
        Comparison-shaped: the queue is expected to list both scopes
        side by side in one render. Asserting both in one response
        catches a future query that groups them into separate branches
        and drops one — a failure the two single-assertion tests above
        would each catch individually but not jointly explain.
        """
        client.force_login(review_queue_setup["superuser"])
        response = client.get(_review_queue_url())
        assert response.status_code == 200
        body = response.content.decode()
        assert "instant-book.pdf" in body
        assert "custom-book.pdf" in body