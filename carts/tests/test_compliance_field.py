# carts/tests/test_compliance_field.py
"""
KR/TW customs-ID requirement on the checkout form.

Background
----------
calculate_korea_tax and calculate_taiwan_tax in carts/tax.py both
return requires_pccc / requires_ezway_id, and the Order and
ProformaInvoice models both carry a destination_tax_id field for it.
But ProformaInvoiceForm.Meta.fields never included the field, so the
checkout form never rendered it and never required it. A Korean or
Taiwanese customer could complete checkout without a PCCC / EZ WAY
number, and the parcel would be refused at the border.

The pre-flight on the dev DB found one historical KR/TW order
missing the field (test data, not a real customer). That order stays
as-is — the fix prevents new ones, it does not retroactively reject
old ones.

Tests cover:
  * KR requires the field; blank is rejected.
  * KR with a field value succeeds and persists to the Order.
  * TW requires the field; blank is rejected.
  * Other destinations (HK as the control) do not require it.
  * Digital-only modes do not require it (country is popped from
    the form in those modes).
  * The value propagates from the form through place_order to the
    Order row.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


# ──────────────────────────────────────────────────────────────────
# Minimal physical-cart fixture: enough to reach the place_order
# branch that constructs an Order from a ProformaInvoice.
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def physical_cart(db, django_user_model):
    from category.models import Category
    from store.models import Product, ProductVariation
    from carts.models import Cart, CartItem

    user = django_user_model.objects.create_user(
        username="compliance_user",
        email="compliance@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    category = Category.objects.create(
        category_name="Compliance Physical",
        slug="compliance-physical",
        product_format="physical",
    )
    product = Product.objects.create(
        product_name="Compliance Widget",
        slug="compliance-widget",
        category=category,
        is_digital=False,
        is_physical=True,
        is_active=True,
        status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=10,
        is_available=True,
    )
    cart = Cart.objects.create(user=user, cart_id="compliance-cart")
    CartItem.objects.create(
        cart=cart,
        user=user,
        product_variation=variation,
        quantity=1,
        is_active=True,
    )
    return {"user": user, "product": product, "variation": variation, "cart": cart}


# ──────────────────────────────────────────────────────────────────
# Form-level: the requirement lives in clean_destination_tax_id
# ──────────────────────────────────────────────────────────────────

def _build_form(country, *, destination_tax_id=None, mode="PHYSICAL"):
    from carts.forms import ProformaInvoiceForm

    data = {
        "email": "buyer@example.com",
        "recipient_first_name": "Test",
        "recipient_last_name": "Buyer",
        "recipient_mobile_area": "+86",
        "recipient_mobile_number": "12345678",
        "address_line_1": "1 Test Street",
        "city": "Test City",
        "state_province_region": "Test Region",
        "country": country,
        "postal_code": "12345",
    }
    if destination_tax_id is not None:
        data["destination_tax_id"] = destination_tax_id
    return ProformaInvoiceForm(data, display_mode=mode)


class TestFormLevelRequirement:

    def test_kr_without_destination_tax_id_is_invalid(self):
        form = _build_form("KR")
        assert not form.is_valid()
        assert "destination_tax_id" in form.errors

    def test_kr_with_destination_tax_id_is_valid(self):
        form = _build_form("KR", destination_tax_id="P123456789012")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["destination_tax_id"] == "P123456789012"

    def test_tw_without_destination_tax_id_is_invalid(self):
        form = _build_form("TW")
        assert not form.is_valid()
        assert "destination_tax_id" in form.errors

    def test_tw_with_destination_tax_id_is_valid(self):
        form = _build_form("TW", destination_tax_id="A123456789")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["destination_tax_id"] == "A123456789"

    def test_hk_without_destination_tax_id_is_valid(self):
        """Control: HK is not on the requirement list."""
        form = _build_form("HK")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["destination_tax_id"] == ""

    def test_au_without_destination_tax_id_is_valid(self):
        """Control: AU is not on the requirement list either."""
        form = _build_form("AU")
        assert form.is_valid(), form.errors

    def test_whitespace_only_id_is_treated_as_missing(self):
        form = _build_form("KR", destination_tax_id="   ")
        assert not form.is_valid()
        assert "destination_tax_id" in form.errors

    def test_digital_only_mode_does_not_require_the_field(self):
        """
        VOUCHER_ONLY pops country from the form, so the clean method
        sees no country and does not enforce the requirement. Same for
        EPRODUCT_ONLY. Neither ships a physical parcel.
        """
        form = _build_form("KR", mode="VOUCHER_ONLY")
        # Note: the form may still be invalid for other reasons (email
        # validators, etc.), so we only assert no destination_tax_id
        # error. A full-validity check would require more fixture
        # completeness than this test's scope warrants.
        assert "destination_tax_id" not in form.errors


# ──────────────────────────────────────────────────────────────────
# Integration: the value reaches the Order row through place_order
# ──────────────────────────────────────────────────────────────────

class TestPlaceOrderPropagation:

    def test_kr_destination_tax_id_propagates_proforma_to_order(
        self, client, physical_cart,
    ):
        """
        The load-bearing assertion: a non-empty destination_tax_id on
        the ProformaInvoice must reach the Order through place_order's
        get_or_create defaults.

        Without this, a future refactor could drop the field from the
        place_order defaults and the parcel would be refused at the
        border with no test catching it. The field exists on Order
        regardless of whether it is populated, so `hasattr` is not
        sufficient.
        """
        from carts.models import ProformaInvoice
        from orders.models import Order

        chain = physical_cart
        client.force_login(chain["user"])

        pi = ProformaInvoice.objects.create(
            user=chain["user"],
            cart=chain["cart"],
            proforma_order_number="COMPLIANCE-KR-PLACE-0001",
            email=chain["user"].email,
            country="KR",
            state_province_region="Test Region",
            destination_tax_id="P123456789012",
            currency_code="HKD",
            locked_exchange_rate=Decimal("1.0000"),
            payment_method="BANK_TRANSFER",
            is_ordered=False,
            display_mode="PHYSICAL",
        )

        url = reverse("place_order", args=[pi.proforma_order_number])
        response = client.post(url, {"payment_method": "BANK_TRANSFER"})
        assert response.status_code in (301, 302), (
            f"place_order did not redirect; status={response.status_code}. "
            f"Response (first 500 chars): {response.content[:500]!r}"
        )

        order = Order.objects.get(order_number=pi.proforma_order_number)
        assert order.destination_tax_id == "P123456789012", (
            "destination_tax_id did not propagate from ProformaInvoice "
            "to Order through place_order's get_or_create defaults."
        )