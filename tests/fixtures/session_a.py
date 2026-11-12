# tests/fixtures/session_a.py
"""
Canonical Session A test scaffolding.

Shared between:
  * tests/walkthrough/test_session_a_discount_accounting.py
    (the composition test — proves the building blocks compose)
  * settlements/tests/test_session_a.py
    (the settlement-side unit tests, uncommented this session)

The fixtures are imported, not inherited via conftest.py, so that
the walkthrough and the settlement unit tests point at exactly the
same objects. Two fixture definitions would drift; this file is the
one definition.

Not a test module — no test_* functions here. See tests/README.md
for the project's test-helper conventions.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone

from accounts.models import Account, Perk
from category.models import Category
from creators.models import CreatorProfile
from orders.models import Order, OrderProduct
from orders.utils import allocate_platform_perk, snapshot_line_commission
from settlements.admin import _create_settlement_lines_for_order
from store.models import (
    Product,
    ProductVariation,
    VariationCampaignEnrolment,
)


@pytest.fixture
def artisan_a(db):
    """
    A verified CreatorProfile with a linked Account.

    One per walkthrough order. The account is a plain member (not a
    superuser) — settlement creation is admin-triggered and takes
    admin_user=None, so artisan_a never needs admin privileges.
    """
    user = Account.objects.create_user(
        username="artisan_a",
        email="artisan_a@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    return CreatorProfile.objects.create(
        user=user,
        display_name="Artisan A",
        is_verified=True,
    )


@pytest.fixture
def _category(db):
    return Category.objects.create(category_name="Walkthrough", slug="walkthrough")


@pytest.fixture
def _physical_product_base(artisan_a, _category):
    """
    A shared factory for the three variations the walkthrough builds.
    Each caller passes the fields that make it distinct; the common
    shape (published, physical, active) lives here.
    """
    def _make(name: str) -> Product:
        return Product.objects.create(
            product_name=name,
            category=_category,
            creator=artisan_a,
            status="Published",
            is_physical=True,
            is_digital=False,
            is_voucher=False,
            is_active=True,
        )
    return _make


@pytest.fixture
def participating_variation(_physical_product_base, campaign_perk):
    """
    Enrolled, not on artisan sale, 5% commission.

    This is the variation that participates in the campaign. The
    fixture creates the enrolment row directly — the artisan-facing
    enrolment UI does not exist yet (Backlog 44); the admin
    registration added this session is the sanctioned seed path.
    """
    product = _physical_product_base("Walkthrough Participating")
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("100.00"),
        original_price=Decimal("100.00"),   # not on sale
        stock=10,
        platform_commission_pct=Decimal("5.00"),
    )
    VariationCampaignEnrolment.objects.create(
        variation=variation,
        perk=campaign_perk,
        enrolled_by=None,   # admin-seeded; null is correct
    )
    return variation


@pytest.fixture
def sale_variation(_physical_product_base, campaign_perk):
    """
    Enrolled but on artisan sale (price < original_price).

    Also 5% commission. Enrolment is created even though Semantics A
    excludes this line from participation — the walkthrough needs to
    prove the enrolment exists and the exclusion still applies. This
    is the interesting case.
    """
    product = _physical_product_base("Walkthrough On Sale")
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("80.00"),
        original_price=Decimal("100.00"),   # artisan sale
        stock=10,
        platform_commission_pct=Decimal("5.00"),
    )
    VariationCampaignEnrolment.objects.create(
        variation=variation,
        perk=campaign_perk,
        enrolled_by=None,
    )
    return variation


@pytest.fixture
def unenrolled_variation(_physical_product_base):
    """
    Same commission as the others (5%), but no enrolment row.

    Proves the enrolment gate: an otherwise-eligible SKU does not
    participate simply because it never opted in.
    """
    product = _physical_product_base("Walkthrough Not Enrolled")
    return ProductVariation.objects.create(
        product=product,
        price=Decimal("100.00"),
        original_price=Decimal("100.00"),
        stock=10,
        platform_commission_pct=Decimal("5.00"),
    )


@pytest.fixture
def walkthrough_order(
    db,
    artisan_a,
    participating_variation,
    sale_variation,
    unenrolled_variation,
    campaign_perk,
):
    """
    A two-line Order, constructed the way place_order constructs it:

      1. Create Order + OrderProduct rows with fulfilled_by set.
      2. Run snapshot_line_commission on every line (as place_order does).
      3. Run allocate_platform_perk(order, perk) (as place_order does).

    Three variations are built by the fixtures, but only two go onto
    the Order. The unenrolled_variation is referenced in
    test_walkthrough_participation_gate — it's a real object with a
    real enrolment-absent state, not a third OrderProduct. This keeps
    Order.discount arithmetic simple (two lines, one participating).

    Currency is pinned to HKD at a fixed rate so the foreign-field
    assertions in the settlement tests are deterministic. HKD is
    non-integer (2 decimals), matching the walkthrough's expected
    figures.
    """
    order = Order.objects.create(
        order_number="WALKTHROUGH-001",
        email="buyer@example.com",
        country="HK",
        product_total=Decimal("180.00"),   # 100 + 80
        discount=Decimal("0.00"),          # set by allocate_platform_perk
        total_due=Decimal("180.00"),       # recomputed by allocate_platform_perk? no — left as-is
        currency_code="HKD",
        locked_exchange_rate=Decimal("1.0800"),
        is_ordered=True,
        order_status="Processing",
    )

    line_participating = OrderProduct.objects.create(
        order=order,
        user=None,
        product=participating_variation.product,
        product_variation=participating_variation,
        quantity=1,
        product_price=participating_variation.price,
        ordered=True,
        fulfilled_by=artisan_a,
    )
    line_on_sale = OrderProduct.objects.create(
        order=order,
        user=None,
        product=sale_variation.product,
        product_variation=sale_variation,
        quantity=1,
        product_price=sale_variation.price,
        ordered=True,
        fulfilled_by=artisan_a,
    )

    # Match place_order's composition: snapshot commission first,
    # then allocate the campaign discount across participating lines.
    for op in (line_participating, line_on_sale):
        snapshot_line_commission(op, op.product_variation)
    allocate_platform_perk(order, campaign_perk)

    # allocate_platform_perk writes Order.discount but does not touch
    # total_due (that's the checkout view's job). For a walkthrough
    # whose assertions are about attribution — not payment — leaving
    # total_due at the pre-discount figure would be misleading. Set it
    # to product_total - discount so the order reads as "paid in full
    # after the campaign."
    order.total_due = order.product_total - order.discount
    order.save(update_fields=["total_due"])

    return order


@pytest.fixture
def settlement_line(walkthrough_order):
    """
    The single ArtisanSettlementLine for walkthrough_order, after
    every line on the order has been dispatched.

    Dispatch is done here (not in walkthrough_order) so that the
    settlement-deferral test can exercise the pre-dispatch state
    against the same order fixture.
    """
    for op in walkthrough_order.items.all():
        op.is_dispatched = True
        op.dispatch_mode = OrderProduct.DispatchMode.VIA_PLATFORM_HUB
        op.dispatched_at = timezone.now()
        op.dispatch_mode_chosen_at = timezone.now()
        op.save(update_fields=[
            "is_dispatched", "dispatch_mode",
            "dispatched_at", "dispatch_mode_chosen_at",
        ])
    result = _create_settlement_lines_for_order(walkthrough_order, admin_user=None)
    assert len(result["created"]) == 1, (
        f"Expected exactly one settlement line, got {len(result['created'])}. "
        f"Warnings: {result['warnings']}"
    )
    return result["created"][0]