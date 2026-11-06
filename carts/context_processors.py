# carts/context_processors.py
"""
Read-only accessors for currency state, available to every template.

The currency_state processor exposes the *currently pinned* exchange
rate, if one exists. It does NOT pin a rate — that is each price-bearing
view's job (get_or_lock_checkout_rate). Pages that never call that helper
(blog, about, homepage, etc.) see `rate_state = None` here, and the
header's ⓘ icon renders hidden.

Registered in xindeng.settings TEMPLATES["OPTIONS"]["context_processors"]
alphabetically between blog.context_processors.blog_review_count and
category.context_processors.menu_links.
"""

from accounts.data import CURRENCIES
from django.utils import timezone


def currency_state(request):
    """
    Read the session-pinned rate, if any. No writes, no rate fetch.

    Returns {"rate_state": None} when no rate is pinned, or
    {"rate_state": {...}} with the display-ready fields the header
    ⓘ Swal consumes.
    """
    locked_at_iso = request.session.get("locked_at")
    rate = request.session.get("locked_rate")
    code = request.session.get("locked_currency_code")
    expires_ms = request.session.get("rate_expiry_timestamp")

    base = {"currency_selection": CURRENCIES}

    if not (rate and code and locked_at_iso and expires_ms):
        return {**base, "rate_state": None}

    try:
        locked_at = timezone.datetime.fromisoformat(locked_at_iso)
        expires_at = timezone.datetime.fromtimestamp(expires_ms / 1000)
    except (ValueError, TypeError, OverflowError):
        return {**base, "rate_state": None}

    now_ms = int(timezone.now().timestamp() * 1000)
    is_expired = now_ms > int(expires_ms)

    return {
        **base,
        "rate_state": {
            "rate": rate,
            "code": code,
            "locked_at_display": locked_at.strftime("%Y-%m-%d %H:%M"),
            "expires_at_display": expires_at.strftime("%Y-%m-%d %H:%M"),
            "is_expired": is_expired,
        },
    }