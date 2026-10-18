# core/settings_helpers.py
"""
Read helpers for core.SiteConfig.

The SiteConfig row is read on the checkout hot path (once per
calculate_shipping call, potentially once per tax-estimate call in a
future session). A DB hit per call is wasteful and would couple
checkout latency to a settings lookup. These helpers cache the value
for 60 seconds and the SiteConfig.save() method invalidates the cache
on admin change, so the effective latency of an admin flip is at most
one cache-miss round trip.
"""

from django.core.cache import cache


_DDP_KEY = "site_config:ddp_enabled"
_DDP_TTL_SECONDS = 60


def is_ddp_enabled() -> bool:
    """
    True when the SiteConfig singleton has ddp_enabled=True.

    Missing row → False (default). This is the fail-closed choice:
    if SiteConfig was never created (fresh DB, missing migration data,
    or a test that did not seed it), the site behaves as DAP — which
    is the current live behaviour. A missing row never silently turns
    on DDP.
    """
    cached = cache.get(_DDP_KEY)
    if cached is not None:
        return cached

    from core.models import SiteConfig

    obj = SiteConfig.objects.filter(pk=1).first()
    value = bool(obj.ddp_enabled) if obj is not None else False
    cache.set(_DDP_KEY, value, timeout=_DDP_TTL_SECONDS)
    return value