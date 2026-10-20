# orders/tests/test_currency_adjustment.py
"""
Type contracts for INTERNAL_CURRENCY_ADJUSTMENT and
DEFAULT_EXCHANGE_RATE_VS_CNY.

Background
----------
INTERNAL_CURRENCY_ADJUSTMENT was a float (1.05). Every value in
DEFAULT_EXCHANGE_RATE_VS_CNY was `float * float`, so those values were
floats. get_current_rate wraps them in Decimal(str(...)) at the point
of use, which defused the type mismatch at that call site — but only
because every consumer happened to wrap correctly.

The change: the constant is now Decimal("1.05"), and every dict value
is Decimal(str(<literal>)) * INTERNAL_CURRENCY_ADJUSTMENT, so the
dict is Decimal-valued end-to-end. get_current_rate wraps the one
float-introducing expression (the Redis-cache division) in
float(INTERNAL_CURRENCY_ADJUSTMENT) before quantizing, and drops a
now-redundant Decimal(str(...)) in the fallback path.

The public signature of get_current_rate is unchanged: it still
returns a float. Changing that would break callers across carts/ and
orders/ that treat the return value as a plain numeric type; see the
new backlog item for that audit.

These tests pin:

  * The constant is Decimal.
  * Every value in DEFAULT_EXCHANGE_RATE_VS_CNY is Decimal.
  * get_current_rate still returns float (signature preservation).
  * get_current_rate produces sensible values on cache hit and miss.
"""

from __future__ import annotations

from decimal import Decimal

import pytest


class TestConstantTypes:

    def test_adjustment_is_decimal(self):
        from accounts.data import INTERNAL_CURRENCY_ADJUSTMENT
        assert isinstance(INTERNAL_CURRENCY_ADJUSTMENT, Decimal)
        assert INTERNAL_CURRENCY_ADJUSTMENT == Decimal("1.05")

    def test_all_default_rates_are_decimal(self):
        from accounts.data import DEFAULT_EXCHANGE_RATE_VS_CNY
        assert DEFAULT_EXCHANGE_RATE_VS_CNY, "dict must not be empty"
        non_decimal = {
            k: type(v).__name__
            for k, v in DEFAULT_EXCHANGE_RATE_VS_CNY.items()
            if not isinstance(v, Decimal)
        }
        assert non_decimal == {}, (
            f"non-Decimal values in DEFAULT_EXCHANGE_RATE_VS_CNY: {non_decimal}"
        )

    def test_every_value_includes_the_adjustment_multiplier(self):
        """
        The dict values are literal * INTERNAL_CURRENCY_ADJUSTMENT, so
        every value should be larger than its bare literal by exactly
        the multiplier. Sanity-check two representative keys: HKD
        (typical decimal) and JPY (large-magnitude).
        """
        from accounts.data import (
            DEFAULT_EXCHANGE_RATE_VS_CNY, INTERNAL_CURRENCY_ADJUSTMENT,
        )
        # HKD base rate is 1.1196.
        assert DEFAULT_EXCHANGE_RATE_VS_CNY["HKD"] == (
            Decimal("1.1196") * INTERNAL_CURRENCY_ADJUSTMENT
        )
        # JPY base rate is 22.49.
        assert DEFAULT_EXCHANGE_RATE_VS_CNY["JPY"] == (
            Decimal("22.49") * INTERNAL_CURRENCY_ADJUSTMENT
        )


class TestGetCurrentRatePreservesFloatSignature:

    def test_returns_float_on_cache_hit(self, settings):
        """
        With a warm cache, get_current_rate divides the two cached
        values (floats from JSON) and quantizes. The return type must
        remain float, because carts/ and orders/ both consume it as a
        plain numeric.
        """
        from django.core.cache import cache
        from orders.utils import get_current_rate

        cache.set("exchange_rates", {"CNH": 7.20, "HKD": 7.80}, timeout=60)
        rate = get_current_rate(base_currency_code="CNY", target_currency_code="HKD")
        assert isinstance(rate, float)
        assert rate > 0

    def test_returns_float_on_cache_miss(self, settings):
        """
        With an empty cache, get_current_rate falls back to
        DEFAULT_EXCHANGE_RATE_VS_CNY. The return type must still be
        float — this is the path that used to compute
        Decimal * float and would now raise TypeError if the fallback
        path hadn't been updated alongside the constant.
        """
        from django.core.cache import cache
        from orders.utils import get_current_rate

        cache.clear()
        rate = get_current_rate(base_currency_code="CNY", target_currency_code="HKD")
        assert isinstance(rate, float)
        assert rate > 0

    def test_cache_hit_and_miss_return_comparable_values(self, settings):
        """
        The two paths should produce roughly the same value when the
        cached rate matches the fallback rate. Not an exact-equality
        assertion (the quantization and the adjustment multiplier mean
        tiny drift is expected), but the same order of magnitude.
        """
        from django.core.cache import cache
        from orders.utils import get_current_rate
        from accounts.data import DEFAULT_EXCHANGE_RATE_VS_CNY

        # Cache HKD at a rate that, after the CNY/CNH ratio and the
        # adjustment, lands near the fallback. This is the exact rate
        # implied by the fallback value: fallback / adjustment = raw.
        fallback_hkd = DEFAULT_EXCHANGE_RATE_VS_CNY["HKD"]
        from accounts.data import INTERNAL_CURRENCY_ADJUSTMENT
        implied_raw = float(fallback_hkd / INTERNAL_CURRENCY_ADJUSTMENT)

        cache.set(
            "exchange_rates",
            {"CNH": 1.0, "HKD": implied_raw},
            timeout=60,
        )
        hit = get_current_rate("CNY", "HKD")

        cache.clear()
        miss = get_current_rate("CNY", "HKD")

        # Within 0.01 of each other.
        assert abs(hit - miss) < 0.01, f"hit={hit}, miss={miss}"

    def test_unknown_target_currency_falls_back_to_one(self, settings):
        """
        The defensive last-resort: a target currency with no fallback
        entry returns 1.0 rather than raising.
        """
        from django.core.cache import cache
        from orders.utils import get_current_rate

        cache.clear()
        rate = get_current_rate("CNY", "ZZZ")
        assert rate == 1.0