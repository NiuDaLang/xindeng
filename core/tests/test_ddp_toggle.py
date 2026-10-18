# core/tests/test_ddp_toggle.py
"""
SiteConfig + is_ddp_enabled() + the calculate_shipping branch.

Background
----------
The DDP-vs-DAP decision lives in docs/物流方案討論稿. Until that
decision is made, checkout runs under DAP (duties at destination)
and the tax estimators in carts/tax.py are not consulted. This
commit adds a SiteConfig singleton with ddp_enabled (default False)
so the switch can be flipped from the admin without a deploy when
the policy decision lands.

Tests cover:
  * SiteConfig enforces pk=1 regardless of how save() is called.
  * is_ddp_enabled() defaults to False when no row exists (fail-closed).
  * is_ddp_enabled() reads the flag from the row.
  * is_ddp_enabled() caches — a second call after a row flip but
    before cache invalidation returns the stale value.
  * SiteConfig.save() invalidates the cache.
  * calculate_shipping dispatches showDapDisclaimer when the flag is
    off, and showDdpDisclaimer when it is on.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.cache import cache
from django.urls import reverse


@pytest.fixture(autouse=True)
def _clear_ddp_cache():
    """Every test starts with a cold cache; otherwise fixtures leak."""
    cache.clear()
    yield
    cache.clear()


# ──────────────────────────────────────────────────────────────────
# SiteConfig model
# ──────────────────────────────────────────────────────────────────

class TestSiteConfigSingleton:

    def test_default_value_is_false(self, db):
        from core.models import SiteConfig
        obj = SiteConfig.get_solo()
        assert obj.ddp_enabled is False

    def test_get_solo_creates_a_row_on_first_access(self, db):
        from core.models import SiteConfig
        assert SiteConfig.objects.count() == 0
        SiteConfig.get_solo()
        assert SiteConfig.objects.count() == 1

    def test_save_forces_pk_one(self, db):
        from core.models import SiteConfig
        obj = SiteConfig(ddp_enabled=True)
        obj.save()
        assert obj.pk == 1
        assert SiteConfig.objects.filter(pk=1).exists()

    def test_second_save_updates_the_same_row(self, db):
        from core.models import SiteConfig
        a = SiteConfig.get_solo()
        a.ddp_enabled = True
        a.save()
        b = SiteConfig.get_solo()
        assert b.pk == 1
        assert b.ddp_enabled is True
        assert SiteConfig.objects.count() == 1


# ──────────────────────────────────────────────────────────────────
# is_ddp_enabled() helper
# ──────────────────────────────────────────────────────────────────

class TestIsDdpEnabled:

    def test_false_when_no_row_exists(self, db):
        """Fail-closed: missing SiteConfig means DAP, not DDP."""
        from core.models import SiteConfig
        from core.settings_helpers import is_ddp_enabled
        assert SiteConfig.objects.count() == 0
        assert is_ddp_enabled() is False

    def test_reads_flag_from_existing_row(self, db):
        from core.models import SiteConfig
        from core.settings_helpers import is_ddp_enabled
        SiteConfig.get_solo()  # creates the row with default False
        assert is_ddp_enabled() is False

        obj = SiteConfig.objects.get(pk=1)
        obj.ddp_enabled = True
        obj.save()
        assert is_ddp_enabled() is True

    def test_caches_the_value(self, db):
        """A second read within TTL returns the cached value."""
        from core.models import SiteConfig
        from core.settings_helpers import is_ddp_enabled
        SiteConfig.objects.create(pk=1, ddp_enabled=False)
        assert is_ddp_enabled() is False

        # Bypass save() to simulate a concurrent mutation that did not
        # go through the invalidation path. The cache should still
        # report the old value.
        SiteConfig.objects.filter(pk=1).update(ddp_enabled=True)
        assert is_ddp_enabled() is False, (
            "Cache should not have been invalidated by a raw .update()."
        )

    def test_save_invalidates_cache(self, db):
        from core.models import SiteConfig
        from core.settings_helpers import is_ddp_enabled
        SiteConfig.objects.create(pk=1, ddp_enabled=False)
        assert is_ddp_enabled() is False  # warms the cache

        obj = SiteConfig.objects.get(pk=1)
        obj.ddp_enabled = True
        obj.save()  # invalidates
        assert is_ddp_enabled() is True


# ──────────────────────────────────────────────────────────────────
# calculate_shipping dispatch
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def physical_cart_for_shipping(db, django_user_model):
    from category.models import Category
    from store.models import Product, ProductVariation
    from carts.models import Cart, CartItem, ShippingCharge

    user = django_user_model.objects.create_user(
        username="ddp_user",
        email="ddp@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    category = Category.objects.create(
        category_name="DDP Physical",
        slug="ddp-physical",
        product_format="physical",
    )
    product = Product.objects.create(
        product_name="DDP Widget",
        slug="ddp-widget",
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
        weight=500,
    )
    cart = Cart.objects.create(user=user, cart_id="ddp-cart")
    CartItem.objects.create(
        cart=cart, user=user,
        product_variation=variation, quantity=1, is_active=True,
    )
    ShippingCharge.objects.create(
        shipped_from="CN",
        zone="test-zone",
        country_code="AU",
        service_name="Test Service",
        min_charge=Decimal("20.00"),
        min_charge_weight=500,
        add_cost_unit_price=Decimal("0.00"),
        add_cost_weight=500,
        other_fee=Decimal("0.00"),
        is_standard=True,
        is_active=True,
    )
    return {"user": user, "product": product, "variation": variation, "cart": cart}


class TestCalculateShippingDispatch:

    def _post_shipping(self, client, chain, *, zone="global", destination="AU"):
        """
        Seed the session keys that the real cart view would have set
        before calculate_shipping is reachable. In a live flow,
        get_or_lock_checkout_rate runs during the cart page render;
        the test bypasses that and seeds directly so the subject
        (the DDP branch) is the only thing under test.
        """
        client.force_login(chain["user"])
        session = client.session
        session["locked_rate"] = "1.0000"
        session.save()

        url = reverse("calculate_shipping")
        return client.post(url, {
            "shipping_accordion": "dropdown",
            "zone": zone,
            "destination": destination,
        })

    def test_dap_disclaimer_dispatched_when_flag_is_off(
        self, client, physical_cart_for_shipping,
    ):
        import json
        from core.models import SiteConfig
        SiteConfig.objects.create(pk=1, ddp_enabled=False)

        response = self._post_shipping(client, physical_cart_for_shipping)
        assert response.status_code == 200
        trigger = json.loads(response["HX-Trigger"])
        assert "showDapDisclaimer" in trigger
        assert "showDdpDisclaimer" not in trigger

    def test_ddp_disclaimer_dispatched_when_flag_is_on(
        self, client, physical_cart_for_shipping,
    ):
        import json
        from core.models import SiteConfig
        SiteConfig.objects.create(pk=1, ddp_enabled=True)

        response = self._post_shipping(client, physical_cart_for_shipping)
        assert response.status_code == 200
        trigger = json.loads(response["HX-Trigger"])
        assert "showDdpDisclaimer" in trigger
        assert "showDapDisclaimer" not in trigger

    def test_china_orders_get_no_disclaimer(
        self, client, physical_cart_for_shipping,
    ):
        import json
        from core.models import SiteConfig
        SiteConfig.objects.create(pk=1, ddp_enabled=False)

        response = self._post_shipping(
            client, physical_cart_for_shipping,
            zone="china", destination="Beijing",
        )
        assert response.status_code == 200
        trigger_header = response.get("HX-Trigger", "")
        if trigger_header:
            trigger = json.loads(trigger_header)
            assert "showDapDisclaimer" not in trigger
            assert "showDdpDisclaimer" not in trigger