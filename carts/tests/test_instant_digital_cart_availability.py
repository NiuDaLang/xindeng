# carts/tests/test_instant_digital_cart_availability.py
"""
Instant-digital variations are effectively infinite stock. Cart
quantity must not be subtracted from their displayed availability,
otherwise adding one to the cart makes the product page look sold
out. Physical and CUSTOM-digital lines must still show the cart
reservation normally.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.fixture
def instant_digital_product(db):
    from category.models import Category
    from store.models import Product, ProductVariation

    cat = Category.objects.create(
        category_name="ID Digital", slug="id-digital", product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Instant Ebook", slug="instant-ebook", category=cat,
        is_digital=True, digital_fulfillment_type="INSTANT",
        is_physical=False, is_voucher=False, is_active=True, status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product, price=Decimal("10.00"), stock=1, is_available=True,
    )
    return {"product": product, "variation": variation}


@pytest.fixture
def physical_product(db):
    from category.models import Category
    from store.models import Product, ProductVariation

    cat = Category.objects.create(
        category_name="Phys Cat", slug="phys-cat", product_format="physical",
    )
    product = Product.objects.create(
        product_name="Physical Widget", slug="physical-widget", category=cat,
        is_digital=False, is_physical=True, is_active=True, status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product, price=Decimal("20.00"), stock=5, is_available=True,
    )
    return {"product": product, "variation": variation}


class TestInstantDigitalAvailability:

    def test_product_view_does_not_subtract_cart_quantity(
        self, client, instant_digital_product, django_user_model,
    ):
        from carts.models import Cart, CartItem

        chain = instant_digital_product
        user = django_user_model.objects.create_user(
            username="inst_user", email="inst@example.com",
            receive_newsletter=False, password="x", is_active=True,
        )
        cart = Cart.objects.create(user=user, cart_id="inst-cart")
        CartItem.objects.create(
            cart=cart, user=user,
            product_variation=chain["variation"], quantity=1,
        )
        client.force_login(user)

        url = reverse("product", args=[
            chain["product"].category.slug, chain["product"].slug,
        ])
        response = client.get(url)
        assert response.status_code == 200

        variation = next(
            v for v in response.context["variations"]
            if v.id == chain["variation"].id
        )
        assert variation.available_production_stock == 1
        assert variation.in_cart is True

    def test_cart_quantity_capped_at_one(
        self, client, instant_digital_product, django_user_model,
    ):
        from carts.models import Cart, CartItem

        chain = instant_digital_product
        user = django_user_model.objects.create_user(
            username="cap_user", email="cap@example.com",
            receive_newsletter=False, password="x", is_active=True,
        )
        Cart.objects.create(user=user, cart_id="cap-cart")
        client.force_login(user)

        payload = {
            "product_id": chain["product"].id,
            "selected_variation": chain["variation"].id,
            "quantity": 1,
        }
        client.post(reverse("add_to_cart_htmx"), payload)
        client.post(reverse("add_to_cart_htmx"), payload)

        item = CartItem.objects.get(
            product_variation=chain["variation"], user=user,
        )
        assert item.quantity == 1


class TestPhysicalStockStillDecrements:

    def test_physical_line_display_still_shows_cart_subtraction(
        self, client, physical_product, django_user_model,
    ):
        from carts.models import Cart, CartItem

        chain = physical_product
        user = django_user_model.objects.create_user(
            username="phys_user", email="phys@example.com",
            receive_newsletter=False, password="x", is_active=True,
        )
        cart = Cart.objects.create(user=user, cart_id="phys-cart")
        CartItem.objects.create(
            cart=cart, user=user,
            product_variation=chain["variation"], quantity=2,
        )
        client.force_login(user)

        url = reverse("product", args=[
            chain["product"].category.slug, chain["product"].slug,
        ])
        response = client.get(url)
        assert response.status_code == 200

        variation = next(
            v for v in response.context["variations"]
            if v.id == chain["variation"].id
        )
        assert variation.available_production_stock == 3
