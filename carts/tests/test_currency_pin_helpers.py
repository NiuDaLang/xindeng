# carts/tests/test_currency_pin_helpers.py
"""
Pin-ordering tests for the foreign-amount helpers in carts.utils.

These tests exist because of 3f-bis-followup-8a: before this session,
update_total_payable (and its siblings) read session['locked_rate']
directly, so any caller that had not already pinned — update_cart_item_qty,
delete_cart_item, add_wish_to_cart, add_to_cart_htmx — read whatever
the *previous* request pinned, and the currency figures stayed one
switch behind.

Each test pins a *known* rate directly into session rather than going
through get_or_lock_checkout_rate, so the test exercises the pin-ordering
logic, not the rate-fetch logic (which is non-deterministic under test —
it reads Redis or a static fallback).

Fixture setup requires receive_newsletter=False on Account.objects.create_user
— see MyAccountManager.create_user's non-standard signature and
tests/_fakes.py::make_superuser, which does the same. Gotcha 44.
"""
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

import pytest
from django.test import Client

from accounts.models import Account
from carts.models import Cart, CartItem
from carts.utils import (
    calculate_foreign_amount,
    update_applied_voucher,
    update_costs_oobs,
    update_total_payable,
)
from store.models import Category, Product, ProductVariation


def _make_request_with_session(client, path='/carts/cart/'):
    """
    Run a real GET so CartMiddleware / CurrencyMiddleware / session
    middleware have all run, then hand back the request object. The
    session is the one Django wrote; setting session values on it
    persists for subsequent utility calls against the same object.
    """
    response = client.get(path)
    assert response.status_code in (200, 302), (
        f"GET {path} returned {response.status_code}; expected 200 or 302"
    )
    return response.wsgi_request


@pytest.fixture
def pinned_hkd_request(db):
    """
    A request whose session is pinned to HKD at a known rate, with a
    cart containing one line item. The cookie default is HKD
    (CurrencyMiddleware default), so get_currency_format() returns HKD
    without extra setup.
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
        username='pinner',
        email='pin@example.com',
        password='x',
        receive_newsletter=False,
        is_active=True,
    )
    client = Client()
    client.force_login(user)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(
        cart=cart, product_variation=variation, quantity=1,
    )

    request = _make_request_with_session(client, path='/carts/cart/')
    request.session['locked_rate'] = '0.1100'
    request.session['locked_currency_code'] = 'HKD'
    # Relative, not fixed. A hardcoded '2026-11-07T00:00:00+00:00'
    # expires 24h later (RATE_LOCK_HOURS) and the helper re-pins to
    # the live rate, at which point <×0.2 assertions fail. See gotcha 92.
    request.session['locked_at'] = timezone.now().isoformat()
    request.session['rate_expiry_timestamp'] = int(
        (timezone.now() + timedelta(hours=24)).timestamp() * 1000
    )
    request.session.save()
    return request, cart


class TestUpdateTotalPayableRepinsOnCurrencySwitch:

    def test_update_total_payable_repins_on_currency_change(self, pinned_hkd_request):
        request, cart = pinned_hkd_request

        # First call: HKD at 0.11.
        _html, fmt_cny, fmt_fx = update_total_payable(request, cart)
        assert fmt_cny != '0.00'
        # At 0.11, HK$ figure is ~11% of the CNY figure.
        assert (
            Decimal(fmt_fx.replace(',', ''))
            < Decimal(fmt_cny.replace(',', '')) * Decimal('0.2')
        )

        # Assert the render tracks whatever the session's post-call rate
        # is. Don't assert on a magnitude tied to a specific rate — the
        # fixture's seeded rate is only 'the current rate' while the pin
        # is fresh, and the live rate will move. See gotcha 93.
        used_rate = Decimal(request.session['locked_rate'])
        cny_amount = Decimal(fmt_cny.replace(',', ''))
        fx_amount = Decimal(fmt_fx.replace(',', ''))
        expected_fx = (cny_amount * used_rate).quantize(Decimal('0.01'))
        assert abs(fx_amount - expected_fx) <= Decimal('0.01')

        # Switch to CNY. Stale 0.1100 in session; the helper must override.
        request.COOKIES['user_currency'] = 'CNY'
        request.session['locked_rate'] = '0.1100'
        request.session['locked_currency_code'] = 'HKD'
        request.session.save()

        _html2, fmt_cny2, fmt_fx2 = update_total_payable(request, cart)
        # In CNY the two figures are identical.
        assert (
            Decimal(fmt_fx2.replace(',', ''))
            == Decimal(fmt_cny2.replace(',', ''))
        )

    def test_update_applied_voucher_repins_on_currency_change(self, pinned_hkd_request):
        request, cart = pinned_hkd_request
        # voucher_applied (500) > new_total_payable (~100), so the
        # "voucher exceeds payable" branch fires and rewrites the
        # session's foreign figure to the capped payable amount.
        request.session['applied_voucher'] = {
            'applied_voucher_amount': '500.00',
            'applied_voucher_amount_foreign': '55.00',  # 500 × 0.11
        }
        request.session.save()

        # Establish a first-pin (HKD at 0.11).
        update_total_payable(request, cart)

        # Switch to CNY; leave stale HKD values in session.
        request.COOKIES['user_currency'] = 'CNY'
        request.session['locked_rate'] = '0.1100'
        request.session['locked_currency_code'] = 'HKD'
        request.session.save()

        update_applied_voucher(request, cart)
        # new_total_payable_foreign == 100 × 1.0 = 100.00.
        # Without the pin, this would still be 100 × 0.11 = 11.00.
        written_fx = request.session['applied_voucher']['applied_voucher_amount_foreign']
        assert Decimal(written_fx.replace(',', '')) == Decimal('100.00')


class TestCalculateForeignAmountFallsBackOnFirstCall:

    def test_calculate_foreign_amount_does_not_raise_on_first_call(self, pinned_hkd_request):
        """
        Before 8a, calculate_foreign_amount did
        session.get('locked_rate') → None, then Decimal(str(None)...)
        → InvalidOperation. The helper pins first, so this passes.
        """
        request, _cart = pinned_hkd_request
        # Wipe the pinned state to simulate a first-in-request call.
        request.session.pop('locked_rate', None)
        request.session.pop('locked_currency_code', None)
        request.session.pop('locked_at', None)
        request.session.pop('rate_expiry_timestamp', None)
        request.session.save()

        # Cookie defaults to HKD; the helper pins on first use.
        symbol, formatted = calculate_foreign_amount(request, Decimal('100.00'))
        assert symbol  # non-empty
        assert formatted  # non-empty


class TestUpdateCostsOobsRepinsAfterQuantityChange:

    def test_update_costs_oobs_repins_after_currency_switch(self, pinned_hkd_request):
        """
        The deeper 8a bug: update_cart_item_qty calls update_costs_oobs,
        which calls update_applied_voucher BEFORE update_total_payable.
        If only update_total_payable is patched, the voucher line stays
        stale after the switch. The helper version patches both.
        """
        request, cart = pinned_hkd_request
        request.session['applied_voucher'] = {
            'applied_voucher_amount': '500.00',
            'applied_voucher_amount_foreign': '55.00',
        }
        request.session.save()

        # Establish a first-pin (HKD at 0.11).
        update_total_payable(request, cart)

        # Simulate switch to CNY, then a quantity-change OOB run.
        request.COOKIES['user_currency'] = 'CNY'
        request.session['locked_rate'] = '0.1100'
        request.session['locked_currency_code'] = 'HKD'
        request.session.save()

        oob_updates, _triggers = update_costs_oobs(
            request, cart,
            is_integer=False,
            foreign_currency_code='CNY',
            foreign_currency_symbol='¥',
            locked_rate='0.1100',  # stale — argument is not consulted for the rate
        )
        joined = ''.join(str(u) for u in oob_updates)
        assert 'total_payable_amount_foreign' in joined
        # The voucher session's foreign figure was refreshed to the
        # CNY-scale value (100.00, not 11.00).
        written_fx = request.session['applied_voucher']['applied_voucher_amount_foreign']
        assert Decimal(written_fx.replace(',', '')) == Decimal('100.00')


class TestPinPreservationAcrossCurrencySwitches:
    """
    3f-bis-followup-11: session pin preservation per currency.

    When the user switches away from a currency and back, the remembered
    pin from the first visit is restored — same rate, same locked_at,
    same expiry — provided it has not itself expired. An expired
    remembered pin falls through to a fresh fetch.

    These tests seed session['last_pin_per_currency'] and the flat keys
    directly rather than going through get_or_lock_checkout_rate for the
    seed step, so the assertions are about the restore path, not about
    what get_current_rate happens to return under test.
    """

    def _seed_remembered_hkd(self, request, rate='0.1100', hours_valid=24):
        """Put an HKD entry in the dict with a future expiry."""
        from datetime import timedelta as _td
        locked_at = timezone.now()
        expires_ms = int((locked_at + _td(hours=hours_valid)).timestamp() * 1000)
        pins = request.session.get('last_pin_per_currency', {}) or {}
        pins['HKD'] = {
            'rate': rate,
            'locked_at': locked_at.isoformat(),
            'expires_ms': expires_ms,
        }
        request.session['last_pin_per_currency'] = pins
        request.session.save()
        return locked_at

    def _seed_expired_remembered_hkd(self, request, rate='0.1100'):
        """Put an HKD entry in the dict whose own expiry is in the past."""
        from datetime import timedelta as _td
        locked_at = timezone.now() - _td(hours=48)
        expires_ms = int((locked_at + _td(hours=24)).timestamp() * 1000)  # past
        pins = request.session.get('last_pin_per_currency', {}) or {}
        pins['HKD'] = {
            'rate': rate,
            'locked_at': locked_at.isoformat(),
            'expires_ms': expires_ms,
        }
        request.session['last_pin_per_currency'] = pins
        request.session.save()
        return locked_at

    def _pin_jpy(self, request, rate='0.0480'):
        """Write a JPY pin into the flat keys, simulating an active switch."""
        request.session['locked_rate'] = rate
        request.session['locked_at'] = timezone.now().isoformat()
        request.session['locked_currency_code'] = 'JPY'
        request.session['rate_expiry_timestamp'] = int(
            (timezone.now() + timedelta(hours=24)).timestamp() * 1000
        )
        request.session.save()

    def test_switch_back_restores_previous_pin(self, pinned_hkd_request):
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        self._seed_remembered_hkd(request, rate='0.1100')
        self._pin_jpy(request, rate='0.0480')

        rate = get_or_lock_checkout_rate(request, 'HKD')

        # Restored — the rate is the remembered one, not a fresh fetch.
        assert rate == Decimal('0.1100')
        assert request.session['locked_rate'] == '0.1100'
        assert request.session['locked_currency_code'] == 'HKD'

    def test_switch_back_preserves_locked_at_display(self, pinned_hkd_request):
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        remembered_locked_at = self._seed_remembered_hkd(request, rate='0.1100')
        remembered_iso = remembered_locked_at.isoformat()
        self._pin_jpy(request)

        get_or_lock_checkout_rate(request, 'HKD')

        # The locked_at written back is the remembered one, not now().
        # This is the display-correctness point: the header ⓘ Swal shows
        # the moment of the original pin, not the moment of the switch-back.
        assert request.session['locked_at'] == remembered_iso

    def test_expired_remembered_pin_is_not_restored(self, pinned_hkd_request):
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        self._seed_expired_remembered_hkd(request, rate='0.1100')
        self._pin_jpy(request)

        rate = get_or_lock_checkout_rate(request, 'HKD')

        # The stale 0.1100 was not restored. Whatever get_current_rate
        # returns, it is not the remembered value — and crucially the
        # flat keys have been overwritten with a fresh pin.
        assert rate != Decimal('0.1100') or request.session['locked_rate'] != '0.1100'
        # And the expired entry was pruned as part of the fresh write.
        pins = request.session.get('last_pin_per_currency', {}) or {}
        assert 'HKD' in pins
        assert pins['HKD']['expires_ms'] > int(timezone.now().timestamp() * 1000)

    def test_cny_bypass_does_not_write_dict(self, pinned_hkd_request):
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        self._seed_remembered_hkd(request, rate='0.1100')

        get_or_lock_checkout_rate(request, 'CNY')

        pins = request.session.get('last_pin_per_currency', {}) or {}
        assert 'CNY' not in pins

    def test_dict_pruned_of_expired_entries(self, pinned_hkd_request):
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        # Seed one expired remembered pin for a currency we are NOT about
        # to pin, and a fresh JPY pin.
        self._seed_expired_remembered_hkd(request, rate='0.1100')
        self._pin_jpy(request)

        # A fresh EUR pin triggers the write path, which prunes.
        get_or_lock_checkout_rate(request, 'EUR')

        pins = request.session.get('last_pin_per_currency', {}) or {}
        assert 'HKD' not in pins       # expired, pruned
        assert 'EUR' in pins           # freshly written
        assert pins['EUR']['expires_ms'] > int(timezone.now().timestamp() * 1000)

    def test_reuse_path_backfills_dict_on_first_reuse(self, pinned_hkd_request):
        """
        Pre-existing flat-key pins (from before this code shipped) are
        invisible to the dict on first reuse. The reuse branch backfills
        the dict so the *next* switch-away-and-back hits the restore path.
        Without this, a session that started life on the old code would
        miss once per currency after the deploy.
        """
        from carts.utils import get_or_lock_checkout_rate

        request, _cart = pinned_hkd_request
        
        # Simulate a legacy session: flat keys are present, but the dict
        # has been wiped (or never existed). We reset the flat keys back
        # to the fixture's known 0.1100 rate to override whatever the
        # cart view fetched during setup.
        request.session.pop('last_pin_per_currency', None)
        request.session['locked_rate'] = '0.1100'
        request.session['locked_currency_code'] = 'HKD'
        request.session['locked_at'] = timezone.now().isoformat()
        request.session['rate_expiry_timestamp'] = int(
            (timezone.now() + timedelta(hours=24)).timestamp() * 1000
        )
        request.session.save()

        get_or_lock_checkout_rate(request, 'HKD')  # reuse, not refresh

        pins = request.session.get('last_pin_per_currency', {}) or {}
        assert 'HKD' in pins
        assert pins['HKD']['rate'] == '0.1100'
        assert pins['HKD']['locked_at'] == request.session['locked_at']