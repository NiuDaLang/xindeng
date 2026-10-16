# core/tests/test_checkout_conflict_responses.py
"""
Backend response-shape tests for the three checkout-path defects named
in the handoff, plus one fourth found during the test-writing pass.

Contracts pinned here:

  1. capture_paypal_order rejects quantity > 1 for instant-digital
     lines. place_order already enforces this via a ValueError; the
     PayPal path does not. A forged POST or a stale cart can push a
     quantity-2 instant-digital line through to OrderProduct creation.
     The fix mirrors place_order's guard, landing in the existing
     `except ValueError as stock_err` handler, which returns 200 with
     status=STOCK_CONFLICT and the PayPal capture ID.

  2. capture_paypal_order handles ValidationError from
     mark_off_perk_at_checkout. The perk's max_uses can be consumed
     between apply_offer and capture; the raise currently lands in the
     outer `except Exception`, which returns 500. PayPal has already
     charged by that point. The fix returns 200 with status=
     OFFER_CONFLICT and the capture ID.

  3. complete_zero_due_voucher_order handles the same ValidationError.
     Same missing handler, but the view is @login_required and no
     external charge happens, so the response carries no transaction_id.

  4. (found during test authoring) complete_zero_due_voucher_order
     reports *insufficient voucher balance* as STOCK_CONFLICT. The
     except ValueError handler around the view catches the
     ValueError raised by execute_atomic_voucher_deduction when the
     user's voucher pool is short, and labels it as a stock conflict.
     The customer sees "an item ran out of stock" for a failure that
     has nothing to do with stock. Split into VOUCHER_BALANCE_CONFLICT.

Scope note on email dispatch
-----------------------------
Both views register transaction.on_commit callbacks for email
dispatch. Under pytest-django's outer atomic those silently drop.
That matches the 2026-10-15 E2E decision — the test's job is the DB
state and the response shape, not the notification pipeline.

Scope note on the quantity-guard fixture
-----------------------------------------
The instant-digital quantity tests deliberately plant a state that
ProductVariation.save() would reject: an instant-digital variation
with stock > 1. The exposure the handoff names — "a stale cart or a
forged POST" — is exactly a state the normal save() invariant would
never have produced. To exercise the per-item guard specifically (and
not the pre-loop stock race-condition check, which fires first on a
stock=1 variation), the fixture must plant that state directly.

The fixture uses ProductVariation.objects.filter(...).update(stock=...)
rather than .save(), because .save() would restore stock=1 for an
instant-digital variation and defeat the test's purpose. This is
deliberate, and the docstring in the fixture repeats the rationale so
a future reader doesn't "clean up" the .update() into a .save().

Located under core/tests/ to match pytest.ini's testpaths.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def capture_response_body():
    """
    The minimal JSON body the PayPal SDK returns from a successful
    capture_order call. Only the fields capture_paypal_order reads:

        purchase_units[0].payments.captures[0].id
            -> transaction_id (the *capture* ID, PayPal's traceable ID)
        purchase_units[0].payments.captures[0].status
            -> payment_status
        purchase_units[0].payments.captures[0].amount.value
        purchase_units[0].payments.captures[0].amount.currency_code
        id
            -> capture_res_data["id"] (the *order* ID, distinct from
               the capture ID above — see the Payment creation in
               capture_paypal_order for the split)
    """
    return {
        "id": "PAYPAL-ORDER-ID-0001",
        "payer": {"payer_id": "PAYER-ABC123"},
        "purchase_units": [
            {
                "payments": {
                    "captures": [
                        {
                            "id": "PAYPAL-CAPTURE-ID-0001",
                            "status": "COMPLETED",
                            "amount": {
                                "value": "10.00",
                                "currency_code": "HKD",
                            },
                        }
                    ]
                }
            }
        ],
    }


@pytest.fixture
def instant_digital_chain(db, django_user_model):
    """
    Buyer + digital product + one instant-fulfilment variation + a
    ProformaInvoice with a live (is_ordered=False) Cart holding one
    CartItem on that variation.

    `variation_stock` lets a caller plant stock values that
    ProductVariation.save() would not have produced. See the module
    docstring for the rationale.
    """
    from category.models import Category
    from store.models import Product, ProductVariation
    from carts.models import Cart, CartItem, ProformaInvoice

    _counter = {"n": 0}

    def _make(*, quantity: int = 1, variation_stock: int | None = None):
        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"capture_user_{n}",
            email=f"capture-{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        category = Category.objects.create(
            category_name=f"Capture Digital {n}",
            slug=f"capture-digital-{n}",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name=f"Capture Ebook {n}",
            category=category,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_voucher=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
        )
        if variation_stock is not None and variation_stock != 1:
            # Bypass save()'s instant-digital stock invariant. See the
            # module docstring: the exposure this fixture plants is
            # exactly a state save() would never produce.
            ProductVariation.objects.filter(pk=variation.pk).update(
                stock=variation_stock
            )
            variation.refresh_from_db()

        cart = Cart.objects.create(cart_id=f"capture-cart-{n}", user=user)
        CartItem.objects.create(
            cart=cart,
            user=user,
            product_variation=variation,
            quantity=quantity,
            is_active=True,
        )
        invoice = ProformaInvoice.objects.create(
            user=user,
            cart=cart,
            proforma_order_number=f"CAPTURE-INV-{n:04d}",
            email=user.email,
            currency_code="HKD",
            locked_exchange_rate=Decimal("1.0000"),
            cart_total=Decimal("10.00") * quantity,
            cart_total_foreign=Decimal("10.00") * quantity,
            total_due=Decimal("10.00") * quantity,
            total_due_foreign=Decimal("10.00") * quantity,
            is_ordered=False,
            display_mode="EPRODUCT_ONLY",
            country="XX",
            state_province_region="Digital",
        )
        return {
            "user": user,
            "product": product,
            "variation": variation,
            "cart": cart,
            "invoice": invoice,
        }

    return _make


@pytest.fixture
def make_voucher_pool(db):
    """
    Create CustomerVoucher rows for a user summing to >= the given
    amount, so execute_atomic_voucher_deduction has something to
    draw on. Without this, the voucher-deduction step in
    complete_zero_due_voucher_order raises ValueError before control
    ever reaches mark_off_perk_at_checkout, and the OFFER_CONFLICT
    test can't reach the code it's meant to exercise.
    """
    from accounts.models import CustomerVoucher

    def _make(user, amount: Decimal):
        CustomerVoucher.objects.create(
            owner=user,
            value=amount,
            balance=amount,
            purchaser_email=user.email,
            registered_email=user.email,
            is_claimed=True,
            is_used=False,
        )

    return _make


@pytest.fixture
def mock_capture(monkeypatch, capture_response_body):
    """
    Patch orders.paypal so that:
      - client.orders.capture_order(...) returns a 200 SDK-like wrapper
      - APIHelper.json_serialize(<wrapper>.body) round-trips the dict
    """
    import json
    from orders import paypal

    fake_controller = MagicMock()
    fake_controller.capture_order.return_value = MagicMock(
        status_code=200,
        body=capture_response_body,
    )
    fake_client = MagicMock()
    fake_client.orders = fake_controller

    monkeypatch.setattr(paypal, "client", fake_client)
    monkeypatch.setattr(
        paypal.APIHelper,
        "json_serialize",
        lambda obj: json.dumps(obj),
        raising=False,
    )
    return fake_controller


# ──────────────────────────────────────────────────────────────────
# Bug #1 — quantity-1 guard on instant-digital lines
# ──────────────────────────────────────────────────────────────────

class TestCapturePaypalQuantityGuard:

    def test_quantity_two_instant_digital_returns_stock_conflict(
        self, client, instant_digital_chain, mock_capture,
    ):
        """
        A forged POST with quantity=2 on an instant-digital line must
        raise ValueError inside the per-item loop, which the existing
        `except ValueError as stock_err` handler catches and converts
        to a 200 STOCK_CONFLICT response.

        variation_stock=2 disables the pre-loop race-condition check
        (`variation.stock < item.quantity`), so the test exercises the
        per-item quantity guard specifically. See module docstring.
        """
        from orders.models import Order, OrderProduct

        chain = instant_digital_chain(quantity=2, variation_stock=2)
        invoice = chain["invoice"]

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        response = client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "STOCK_CONFLICT"
        assert payload["transaction_id"] == "PAYPAL-CAPTURE-ID-0001"
        assert payload["order_number"] == invoice.proforma_order_number

        # The line was not created. The atomic block rolled back.
        order = Order.objects.filter(
            order_number=invoice.proforma_order_number
        ).first()
        if order is not None:
            assert not OrderProduct.objects.filter(order=order).exists()

    def test_quantity_two_does_not_reach_order_product_create(
        self, client, instant_digital_chain, mock_capture, monkeypatch,
    ):
        """
        The per-item quantity guard must fire before
        OrderProduct.objects.create. Asserted by spying on create and
        asserting it was not called — a clearer failure message than
        inferring it from the response shape.
        """
        from orders.models import OrderProduct

        chain = instant_digital_chain(quantity=2, variation_stock=2)
        invoice = chain["invoice"]

        called = {"create": False}
        real_create = OrderProduct.objects.create

        def spy_create(*args, **kwargs):
            called["create"] = True
            return real_create(*args, **kwargs)

        monkeypatch.setattr(OrderProduct.objects, "create", spy_create)

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert called["create"] is False, (
            "OrderProduct.objects.create ran for a quantity=2 "
            "instant-digital line — the per-item quantity guard is "
            "missing before the create call in capture_paypal_order."
        )

    def test_quantity_one_still_creates_the_line(
        self, client, instant_digital_chain, mock_capture,
    ):
        """
        Regression guard: the fix must not break the quantity-1 path
        the E2E suite already covers via the bank-transfer route.
        """
        from orders.models import Order, OrderProduct

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        response = client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "SUCCESS"

        order = Order.objects.get(order_number=invoice.proforma_order_number)
        assert OrderProduct.objects.filter(order=order, quantity=1).exists()


# ──────────────────────────────────────────────────────────────────
# Bug #2 — ValidationError handler in capture_paypal_order
# ──────────────────────────────────────────────────────────────────

class TestCapturePaypalValidationErrorHandler:

    def test_validation_error_from_mark_off_returns_offer_conflict(
        self, client, instant_digital_chain, mock_capture, monkeypatch,
    ):
        """
        ValidationError from mark_off_perk_at_checkout must produce a
        200 OFFER_CONFLICT carrying the capture ID, not a 500.
        """
        from orders import paypal
        from orders.models import Order

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        def boom(*args, **kwargs):
            raise ValidationError("Perk max_uses exhausted.")

        monkeypatch.setattr(paypal, "mark_off_perk_at_checkout", boom)

        session = client.session
        session["offer_applied"] = {"offer_code": "SOME-CODE"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        response = client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200, (
            "ValidationError from mark_off_perk_at_checkout should be "
            "caught and returned as 200 OFFER_CONFLICT, not 500."
        )
        payload = response.json()
        assert payload["status"] == "OFFER_CONFLICT"
        assert payload["transaction_id"] == "PAYPAL-CAPTURE-ID-0001"
        assert "title" in payload and "text" in payload

        # The Order row was not created — the atomic block rolled back.
        assert not Order.objects.filter(
            order_number=invoice.proforma_order_number
        ).exists()

    def test_validation_error_does_not_hit_generic_exception_handler(
        self, client, instant_digital_chain, mock_capture, monkeypatch, caplog,
    ):
        """
        The generic `except Exception as e: logger.exception(...)` must
        not fire. Asserted via the logger record text — the generic
        handler logs "💥 Capture Processing Exception".
        """
        from orders import paypal

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        def boom(*args, **kwargs):
            raise ValidationError("Perk max_uses exhausted.")

        monkeypatch.setattr(paypal, "mark_off_perk_at_checkout", boom)

        session = client.session
        session["offer_applied"] = {"offer_code": "SOME-CODE"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")

        with caplog.at_level(logging.ERROR, logger="orders.paypal"):
            client.post(
                f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
                f"&invoice={invoice.proforma_order_number}"
            )

        for record in caplog.records:
            assert "Capture Processing Exception" not in record.getMessage(), (
                "ValidationError leaked past the specific handler and "
                "hit the generic except Exception — the OFFER_CONFLICT "
                "handler is not wired up."
            )

    def test_mark_off_perk_at_checkout_called_exactly_once(
        self, client, instant_digital_chain, mock_capture, monkeypatch,
    ):
        """
        Guard-test pinning an invariant the code should already satisfy:
        capture_paypal_order must call mark_off_perk_at_checkout exactly
        once per capture.

        The failure mode this catches: a duplicate call to mark_off
        (e.g. from a bad edit that keeps both an old and a new block).
        On the first call the UserPerk is flipped is_used=True; on the
        second call PerkEvaluator.get_eligibility_status returns
        ALREADY_USED and mark_off raises ValidationError. The customer
        sees OFFER_CONFLICT for a valid, unused offer.

        This is the class of test the 2026-10-16 handoff's meta-note
        named as valuable: a bug that *would* be caught, rather than
        one that *was*. It passes on the current code (where the
        duplicate has been removed) and would have failed on the
        intermediate state.
        """
        from orders import paypal

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        call_log = []

        def spy_mark_off(user, code):
            call_log.append((user.id, code))
            # Do NOT call the real function — its side effects
            # (Perk counter increment, UserPerk flip) would need a
            # fixture more elaborate than this test warrants, and the
            # assertion is about call *count*, not outcome.

        monkeypatch.setattr(paypal, "mark_off_perk_at_checkout", spy_mark_off)

        session = client.session
        session["offer_applied"] = {"offer_code": "SOME-CODE"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        response = client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200
        assert response.json()["status"] == "SUCCESS", (
            "The capture should have succeeded with a valid offer "
            "present. A non-SUCCESS status here suggests the spy wasn't "
            "invoked correctly or the surrounding fixture is wrong."
        )
        assert len(call_log) == 1, (
            f"mark_off_perk_at_checkout was called {len(call_log)} times; "
            f"expected exactly 1. A duplicate call would flip the "
            f"UserPerk on the first invocation and then fail with "
            f"ALREADY_USED on the second, producing a spurious "
            f"OFFER_CONFLICT for a valid offer."
        )
        assert call_log[0][1] == "SOME-CODE"


# ──────────────────────────────────────────────────────────────────
# Bug #3 — ValidationError handler in complete_zero_due_voucher_order
# ──────────────────────────────────────────────────────────────────

class TestCompleteZeroDueVoucherValidationErrorHandler:

    def test_validation_error_returns_offer_conflict_without_transaction_id(
        self, client, instant_digital_chain, make_voucher_pool, monkeypatch,
    ):
        """
        complete_zero_due_voucher_order is @login_required and settles
        via voucher balance, so there is no external charge and no
        capture ID to report. The OFFER_CONFLICT response carries title
        and text but not transaction_id.

        The voucher pool is seeded so execute_atomic_voucher_deduction
        succeeds and control reaches the monkeypatched
        mark_off_perk_at_checkout. Without the pool, the preceding
        deduction raises ValueError and the test can't reach its
        subject.
        """
        from orders import views as orders_views
        from orders.models import Order
        from carts.models import ProformaInvoice

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        ProformaInvoice.objects.filter(pk=invoice.pk).update(
            total_due=Decimal("0.00"),
            total_due_foreign=Decimal("0.00"),
            voucher_applied=Decimal("10.00"),
        )
        invoice.refresh_from_db()

        make_voucher_pool(chain["user"], Decimal("10.00"))

        def boom(*args, **kwargs):
            raise ValidationError("Perk max_uses exhausted.")

        monkeypatch.setattr(orders_views, "mark_off_perk_at_checkout", boom)

        session = client.session
        session["offer_applied"] = {"offer_code": "SOME-CODE"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("complete_zero_due_voucher_order")
        response = client.post(
            f"{url}?invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "OFFER_CONFLICT"
        assert "title" in payload and "text" in payload
        # No external charge happened, so no capture ID.
        assert "transaction_id" not in payload

        assert not Order.objects.filter(
            order_number=invoice.proforma_order_number
        ).exists()


# ──────────────────────────────────────────────────────────────────
# Bug #4 — insufficient voucher balance misreported as STOCK_CONFLICT
# ──────────────────────────────────────────────────────────────────

class TestZeroDueVoucherBalanceConflict:

    def test_insufficient_voucher_balance_is_not_reported_as_stock_conflict(
        self, client, instant_digital_chain,
    ):
        """
        When the user's voucher balance can't cover the total,
        execute_atomic_voucher_deduction raises ValueError. The
        existing handler labels this STOCK_CONFLICT — which tells the
        customer "an item ran out of stock" for a failure that has
        nothing to do with stock.

        Asserts the desired VOUCHER_BALANCE_CONFLICT response shape.
        Fails against the current backend; commit 2 delivers the fix.
        """
        from carts.models import ProformaInvoice
        from orders.models import Order

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        # Point the invoice at zero due and a voucher_applied the user
        # cannot actually cover — no CustomerVoucher rows are created.
        ProformaInvoice.objects.filter(pk=invoice.pk).update(
            total_due=Decimal("0.00"),
            total_due_foreign=Decimal("0.00"),
            voucher_applied=Decimal("10.00"),
        )
        invoice.refresh_from_db()

        client.force_login(chain["user"])
        url = reverse("complete_zero_due_voucher_order")
        response = client.post(
            f"{url}?invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "VOUCHER_BALANCE_CONFLICT", (
            "Insufficient voucher balance must not be reported as "
            "STOCK_CONFLICT. The customer-facing message for a stock "
            "shortage tells them to check product availability; the "
            "message for a voucher shortfall must tell them to check "
            "their wallet."
        )
        assert "title" in payload and "text" in payload

        # The Order was not created — the atomic block rolled back.
        assert not Order.objects.filter(
            order_number=invoice.proforma_order_number
        ).exists()


class TestCapturePaypalVoucherBalanceHandler:

    def test_voucher_balance_error_returns_voucher_balance_conflict(
        self, client, instant_digital_chain, mock_capture, monkeypatch,
    ):
        """
        A VoucherBalanceError raised from execute_atomic_voucher_deduction
        on the PayPal capture path must produce a 200
        VOUCHER_BALANCE_CONFLICT carrying the capture ID, not a 500.

        The failure mode: a voucher-applied cart reaches capture after
        the balance was consumed between apply_voucher and the capture
        call. execute_atomic_voucher_deduction raises VoucherBalanceError.
        VoucherBalanceError inherits directly from Exception (not
        ValueError, not ValidationError), so without a specific clause
        it falls through to the generic `except Exception` and returns
        500 — after PayPal has already charged.
        """
        from orders import paypal
        from orders.models import Order

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        def boom(*args, **kwargs):
            from orders.utils import VoucherBalanceError
            raise VoucherBalanceError("Insufficient voucher balance.")

        monkeypatch.setattr(
            paypal, "execute_atomic_voucher_deduction", boom
        )

        # The voucher path is entered only when the session carries a
        # non-zero applied_voucher_amount.
        session = client.session
        session["applied_voucher"] = {"applied_voucher_amount": "10.00"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("capture_paypal_order")
        response = client.post(
            f"{url}?paypal_order_id=PAYPAL-ORDER-ID-0001"
            f"&invoice={invoice.proforma_order_number}"
        )

        assert response.status_code == 200, (
            "VoucherBalanceError from execute_atomic_voucher_deduction "
            "should be caught and returned as 200 "
            "VOUCHER_BALANCE_CONFLICT, not 500."
        )
        payload = response.json()
        assert payload["status"] == "VOUCHER_BALANCE_CONFLICT"
        assert payload["transaction_id"] == "PAYPAL-CAPTURE-ID-0001"
        assert "title" in payload and "text" in payload

        assert not Order.objects.filter(
            order_number=invoice.proforma_order_number
        ).exists()


class TestPlaceOrderVoucherBalanceHandler:

    def test_voucher_balance_error_redirects_with_message(
        self, client, instant_digital_chain, monkeypatch,
    ):
        """
        place_order is the bank-transfer path — pre-charge, no money
        moved. A VoucherBalanceError here must land in a messages.error
        + redirect, not a 500.
        """
        from orders import views as orders_views

        chain = instant_digital_chain(quantity=1)
        invoice = chain["invoice"]

        def boom(*args, **kwargs):
            from orders.utils import VoucherBalanceError
            raise VoucherBalanceError("Insufficient voucher balance.")

        monkeypatch.setattr(
            orders_views, "execute_atomic_voucher_deduction", boom
        )

        session = client.session
        session["applied_voucher"] = {"applied_voucher_amount": "10.00"}
        session.save()

        client.force_login(chain["user"])
        url = reverse("place_order", args=[invoice.proforma_order_number])
        response = client.post(url, {
            "payment_method": "BANK_TRANSFER",
        })

        # A redirect back to the referer (or cart) is the intended
        # response; a 500 is the bug.
        assert response.status_code in (301, 302), (
            "VoucherBalanceError on the bank-transfer path should "
            "produce a messages.error + redirect, not a 500."
        )
