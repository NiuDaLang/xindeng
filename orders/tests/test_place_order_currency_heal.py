# orders/tests/test_place_order_currency_heal.py
"""
8b: place_order() self-heals ProformaInvoice when the cookie currency
has changed since the invoice was created.

The bug (surfaced during the 8a walkthrough): the user switches currency
on the cart, then clicks through to place_order. The template label
follows the cookie (foreign_currency_code from context) but the figures
on the page come from proforma_invoice.total_due_foreign, which is frozen
at the rate from the checkout() POST. Label says CNY, figures are HKD.

The heal recomputes all six *_foreign fields from their CNY base × the
fresh rate, writes them back, and updates locked_exchange_rate and
currency_code to match. Recomputing total_due_foreign from
total_due × fresh_rate (not by summing the recomputed component fields)
matches update_total_payable's shape and avoids a rounding mismatch at
the .xx5 boundary — F60.
"""
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from accounts.models import Account
from carts.models import Cart, CartItem, ProformaInvoice
from store.models import Category, Product, ProductVariation


def _make_invoice(currency_code='HKD', locked_rate='0.1100'):
    """
    Build a ProformaInvoice with all six *_foreign fields pre-populated
    at the given rate, so we can assert on the exact post-heal values.
    """
    Category.objects.create(
        category_name='Test', slug='test', product_format='physical',
    )
    product = Product.objects.create(
        product_name='Test Product',
        slug='test-product',
        category=Category.objects.get(slug='test'),
        is_active=True,
        is_physical=True,
        status='Published',
    )
    variation = ProductVariation.objects.create(
        product=product, price=Decimal('100.00'), stock=10,
    )

    user = Account.objects.create_user(
        username='buyer',
        email='buyer@example.com',
        password='x',
        receive_newsletter=False,
        is_active=True,
    )
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(
        cart=cart, product_variation=variation, quantity=2,
    )

    rate = Decimal(locked_rate)
    invoice = ProformaInvoice.objects.create(
        cart=cart,
        user=user,
        proforma_order_number='HK-TESTINV',
        email='buyer@example.com',
        country='HK',
        cart_total=Decimal('200.00'),
        shipping_cost=Decimal('20.00'),
        discount=Decimal('10.00'),
        tax=Decimal('0.00'),
        voucher_applied=Decimal('0.00'),
        total_due=Decimal('210.00'),
        cart_total_foreign=Decimal('200.00') * rate,
        shipping_cost_amount_foreign=Decimal('20.00') * rate,
        discount_amount_foreign=Decimal('10.00') * rate,
        tax_amount_foreign=Decimal('0.00'),
        applied_voucher_amount_foreign=Decimal('0.00'),
        total_due_foreign=Decimal('210.00') * rate,
        locked_exchange_rate=rate,
        currency_code=currency_code,
        is_ordered=False,
    )
    return invoice, user


@pytest.mark.django_db
class TestPlaceOrderHealsProformaOnCurrencySwitch:

    def test_heals_to_cny(self):
        invoice, user = _make_invoice(currency_code='HKD', locked_rate='0.1100')
        client = Client()
        client.force_login(user)
        client.cookies['user_currency'] = 'CNY'

        response = client.get(reverse('place_order', args=[invoice.proforma_order_number]))
        assert response.status_code == 200

        invoice.refresh_from_db()
        assert invoice.currency_code == 'CNY'
        assert invoice.locked_exchange_rate == Decimal('1.0000')
        # In CNY the two figures are identical at 2dp.
        assert invoice.cart_total_foreign == invoice.cart_total
        assert invoice.shipping_cost_amount_foreign == invoice.shipping_cost
        assert invoice.discount_amount_foreign == invoice.discount
        assert invoice.total_due_foreign == invoice.total_due

    def test_heals_to_jpy_integer_precision(self):
        """JPY is an INTEGER_CURRENCIES member; the heal must quantize to 0 dp."""
        invoice, user = _make_invoice(currency_code='HKD', locked_rate='0.1100')
        client = Client()
        client.force_login(user)
        client.cookies['user_currency'] = 'JPY'

        response = client.get(reverse('place_order', args=[invoice.proforma_order_number]))
        assert response.status_code == 200

        invoice.refresh_from_db()
        assert invoice.currency_code == 'JPY'
        # JPY figures are integral.
        assert invoice.total_due_foreign == invoice.total_due_foreign.to_integral_value()
        assert invoice.cart_total_foreign == invoice.cart_total_foreign.to_integral_value()

    def test_does_not_heal_when_currency_matches(self):
        """No write when currency_code already agrees with the cookie."""
        invoice, user = _make_invoice(currency_code='HKD', locked_rate='0.1100')
        original_rate = invoice.locked_exchange_rate
        original_updated = invoice.updated_at

        client = Client()
        client.force_login(user)
        client.cookies['user_currency'] = 'HKD'

        response = client.get(reverse('place_order', args=[invoice.proforma_order_number]))
        assert response.status_code == 200

        invoice.refresh_from_db()
        assert invoice.currency_code == 'HKD'
        assert invoice.locked_exchange_rate == original_rate
        # auto_now=True bumps updated_at on any save; unchanged means no save.
        assert invoice.updated_at == original_updated

    def test_rate_expiry_timestamp_reaches_context(self):
        """
        Regression guard for the rate_expiry_time -> rate_expiry_timestamp
        typo fix. Without the fix, context['rate_expiry_timestamp'] == 0
        because the view reads the wrong session key.
        """
        invoice, user = _make_invoice(currency_code='HKD', locked_rate='0.1100')
        client = Client()
        client.force_login(user)
        client.cookies['user_currency'] = 'HKD'

        # Seed the session key that checkout() would have written.
        session = client.session
        session['rate_expiry_timestamp'] = 1234567890000
        session.save()

        response = client.get(reverse('place_order', args=[invoice.proforma_order_number]))
        assert response.status_code == 200
        # Was 0 before the typo fix (view read 'rate_expiry_time').
        assert response.context['rate_expiry_timestamp'] == 1234567890000