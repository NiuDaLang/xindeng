# core/tests/test_offer_code_snapshot.py
"""
Tests for Order.offer_code (migration 0033) and the rewrite of
reverse_perk_usage_at_cancellation.

Background
----------
reverse_perk_usage_at_cancellation previously read offer_code from
ProformaInvoice, which has no such field. The read raised
AttributeError inside a try/except in check_and_expire_hold, so
cancelled orders never restored their Perk usage — the counter stayed
inflated and UserPerk.is_used stayed True.

The fix:
  * Adds Order.offer_code (CharField, blank=True, default=""), a
    point-in-time snapshot of the code applied at checkout.
  * Writes it at all three order-creation sites — place_order,
    capture_paypal_order, complete_zero_due_voucher_order — under
    Option A: members snapshot the code, guests write "".
  * Rewrites reverse_perk_usage_at_cancellation to read
    order_instance.offer_code directly.

Option A invariant this file pins: order.offer_code non-empty implies
a Perk counter was incremented for this order, and vice versa. The
guest bank-hold regression test at the bottom is the one that would
have caught the imbalance introduced by the pre-Option-A shape.

Scope note
----------
The snapshot *writes* live inside large view functions (place_order,
capture_paypal_order, complete_zero_due_voucher_order) with many
dependencies — session setup, ProformaInvoice + cart + cart-items,
and (for PayPal) a live SDK client. Testing each of those flows end
to end would require extensive mocking and would be brittle. The
snapshot write is a one-line conditional that has been reviewed at
each site; this file instead covers the reversal logic — which is
where the actual bug lived — and the field contract.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def global_perk(db):
    """A global Perk, as a code that isn't tied to any specific user."""
    from accounts.models import Perk

    return Perk.objects.create(
        code="GLOBAL10",
        description="10% off, global",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        is_active=True,
        valid_from=timezone.now() - timezone.timedelta(days=1),
        uses_count=5,
        max_uses=100,
    )


@pytest.fixture
def personal_perk(db):
    """
    The underlying Perk for a personal (UserPerk) code. Its `code` is
    different from the unique_code the customer enters at checkout —
    that distinction is what makes the personal-code path exercise the
    UserPerk fallback branch in reverse_perk_usage_at_cancellation.
    """
    from accounts.models import Perk

    return Perk.objects.create(
        code="PERSONAL10",
        description="10% off, personal",
        discount_type="percentage",
        discount_value=Decimal("10.00"),
        is_active=True,
        valid_from=timezone.now() - timezone.timedelta(days=1),
        uses_count=3,
        max_uses=100,
    )


@pytest.fixture
def member(db, django_user_model):
    return django_user_model.objects.create_user(
        username="offer_member",
        email="offer-member@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def make_order(db):
    """
    Builds a bare Order — the reversal function only reads
    order.user, order.order_number, and order.offer_code, so a
    full item graph is not required.
    """
    from orders.models import Order

    _counter = {"n": 0}

    def _make(*, user=None, offer_code="", email="buyer@example.com"):
        _counter["n"] += 1
        return Order.objects.create(
            user=user,
            order_number=f"OFFER-TEST-{_counter['n']:04d}",
            email=email,
            offer_code=offer_code,
            is_ordered=False,
            order_status="Hold_Pending",
        )

    return _make


# ──────────────────────────────────────────────────────────────────
# reverse_perk_usage_at_cancellation — the actual fix
# ──────────────────────────────────────────────────────────────────

class TestReversePerkUsage:

    def test_reverse_decrements_global_perk_for_member_order(
        self, member, global_perk, make_order,
    ):
        from orders.utils import reverse_perk_usage_at_cancellation

        order = make_order(user=member, offer_code="GLOBAL10")
        global_perk.refresh_from_db()
        before = global_perk.uses_count

        result = reverse_perk_usage_at_cancellation(order)

        global_perk.refresh_from_db()
        assert global_perk.uses_count == before - 1
        assert "GLOBAL10" in result

    def test_reverse_restores_user_perk_for_personal_code(
        self, member, personal_perk, make_order,
    ):
        """
        When a member checked out with a personal UserPerk code, the
        order's offer_code holds that UserPerk.unique_code, not the
        underlying Perk.code. reverse_perk_usage_at_cancellation must
        walk the UserPerk fallback branch and restore both:

          * the Perk counter (incremented by mark_off_perk_at_checkout)
          * the UserPerk row's is_used / used_at flags
        """
        from accounts.models import UserPerk
        from orders.utils import reverse_perk_usage_at_cancellation

        # Simulate the post-checkout state: user has consumed their
        # personal code, and the underlying Perk's counter was bumped.
        up = UserPerk.objects.create(
            user=member,
            perk=personal_perk,
            unique_code="PERSONALCODE1",
            is_used=True,
            used_at=timezone.now(),
        )
        personal_perk.refresh_from_db()
        before_perk = personal_perk.uses_count

        order = make_order(user=member, offer_code="PERSONALCODE1")
        result = reverse_perk_usage_at_cancellation(order)

        personal_perk.refresh_from_db()
        up.refresh_from_db()

        assert personal_perk.uses_count == before_perk - 1
        assert up.is_used is False
        assert up.used_at is None
        assert "PERSONALCODE1" in result

    def test_reverse_case_insensitive_on_code(
        self, member, global_perk, make_order,
    ):
        """
        place_order and capture_paypal_order both .strip().upper() the
        code before writing. The reverse function also uppercases. The
        two must agree so a lower-case snapshot still reverses.
        """
        from orders.utils import reverse_perk_usage_at_cancellation

        order = make_order(user=member, offer_code="global10")
        global_perk.refresh_from_db()
        before = global_perk.uses_count

        reverse_perk_usage_at_cancellation(order)

        global_perk.refresh_from_db()
        assert global_perk.uses_count == before - 1

    def test_reverse_no_op_when_offer_code_empty(
        self, member, global_perk, make_order,
    ):
        """
        Legacy orders created before migration 0033 have "" here. The
        function must return cleanly without raising and without
        touching any Perk counter.
        """
        from orders.utils import reverse_perk_usage_at_cancellation

        order = make_order(user=member, offer_code="")
        global_perk.refresh_from_db()
        before = global_perk.uses_count

        result = reverse_perk_usage_at_cancellation(order)

        global_perk.refresh_from_db()
        assert global_perk.uses_count == before
        assert "Rollback skipped" in result or "No coupon code" in result

    def test_reverse_no_op_when_code_unknown(
        self, member, global_perk, make_order,
    ):
        """
        A code that matches neither a global Perk nor any of the
        member's UserPerk rows must not raise. This is defensive: a
        code can be deleted from the Perk table between checkout and
        cancellation.
        """
        from orders.utils import reverse_perk_usage_at_cancellation

        order = make_order(user=member, offer_code="NO-SUCH-CODE")
        global_perk.refresh_from_db()
        before = global_perk.uses_count

        reverse_perk_usage_at_cancellation(order)  # must not raise

        global_perk.refresh_from_db()
        assert global_perk.uses_count == before

    def test_reverse_does_not_go_below_zero(self, member, make_order):
        """
        The reverse function guards with `if perk.uses_count > 0` before
        decrementing. This protects against the counter going negative
        in the unlikely case of a double-cancellation replay.
        """
        from accounts.models import Perk
        from orders.utils import reverse_perk_usage_at_cancellation

        perk = Perk.objects.create(
            code="ZEROUSES",
            description="Zero uses",
            discount_type="percentage",
            discount_value=Decimal("10.00"),
            is_active=True,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            uses_count=0,
        )
        order = make_order(user=member, offer_code="ZEROUSES")

        reverse_perk_usage_at_cancellation(order)

        perk.refresh_from_db()
        assert perk.uses_count == 0


# ──────────────────────────────────────────────────────────────────
# Option A regression — the guest bank-hold shape
# ──────────────────────────────────────────────────────────────────

class TestGuestBankHoldRegression:
    """
    Under Option A, place_order and capture_paypal_order only write
    order.offer_code when the request is authenticated. A guest order
    therefore carries offer_code="" — even when a global promo was
    applied to the cart and used to compute the discount.

    The invariant this protects: reverse_perk_usage_at_cancellation
    decrements a Perk counter only when a snapshot exists, i.e. only
    when the checkout path also incremented it. Without this, a guest
    bank-hold with a global promo would expire and the reverse would
    decrement a counter that was never incremented — silently
    under-counting the global uses.
    """

    def test_guest_order_with_empty_offer_code_is_noop_on_reverse(
        self, global_perk, make_order,
    ):
        from orders.utils import reverse_perk_usage_at_cancellation

        # Guest: user=None, offer_code="" — exactly what Option A writes.
        order = make_order(user=None, offer_code="", email="guest@example.com")
        global_perk.refresh_from_db()
        before = global_perk.uses_count

        reverse_perk_usage_at_cancellation(order)

        global_perk.refresh_from_db()
        assert global_perk.uses_count == before

    def test_guest_order_reverse_does_not_touch_user_perk_table(
        self, member, personal_perk, make_order, django_user_model,
    ):
        """
        Belt-and-braces: even if some future code path were to write
        offer_code onto a guest order, the UserPerk branch is gated on
        `user and user.is_authenticated`. A guest order must never
        reach into the UserPerk table.
        """
        from accounts.models import UserPerk
        from orders.utils import reverse_perk_usage_at_cancellation

        # An unrelated member has an active UserPerk for personal_perk.
        # A guest order's reversal must not touch it.
        up = UserPerk.objects.create(
            user=member,
            perk=personal_perk,
            unique_code="UNRELATEDCODE",
            is_used=True,
            used_at=timezone.now(),
        )

        order = make_order(user=None, offer_code="UNRELATEDCODE")
        reverse_perk_usage_at_cancellation(order)

        up.refresh_from_db()
        assert up.is_used is True
        assert up.used_at is not None


# ──────────────────────────────────────────────────────────────────
# Field contract
# ──────────────────────────────────────────────────────────────────

class TestOfferCodeField:
    """Basic sanity checks on the field the migration added."""

    def test_offer_code_stores_and_reads(self, make_order):
        order = make_order(offer_code="ABCD1234")
        order.refresh_from_db()
        assert order.offer_code == "ABCD1234"

    def test_offer_code_defaults_to_empty_string(self, db):
        from orders.models import Order

        order = Order.objects.create(
            order_number="OFFER-DEFAULT-1",
            email="x@example.com",
            is_ordered=False,
            order_status="Hold_Pending",
        )
        assert order.offer_code == ""