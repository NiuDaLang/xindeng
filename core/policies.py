# core/policies.py
"""
Named policy constants.

Each of these was previously a literal at its call site. Extracting them
here means a policy change is one edit, not a grep. The values are
unchanged from the literals they replace; the extraction is pure.

See the 2026-11-06 handoff section "policy constants" for the
reasoning on each window.

Voucher and perk locks are named separately on purpose. They happen to
share a 15-minute value today, but they govern different resources
(CustomerVoucher rows vs UserPerk rows), are written by different views,
and a future policy change to one should not silently change the other.
Naming them the same constant would invite exactly that drift.
"""

# Session-pinned display-rate validity. Every page that shows a foreign
# equivalent pins a rate once on load (via carts.utils.get_or_lock_checkout_rate)
# and treats it as authoritative for this many hours. Beyond that, the
# next page load re-pins.
RATE_LOCK_HOURS = 24

# Offline bank-transfer hold window. Set in orders.views.place_order as
# inventory_hold_expiry; the check_and_expire_hold task fires at this
# offset.
BANK_HOLD_HOURS = 72

# Instant e-product download token lifetime. Issued by
# orders.utils.issue_download_token with the default ttl_hours.
DOWNLOAD_TOKEN_INSTANT_HOURS = 168  # 7 days

# CUSTOM (made-to-order) digital delivery token lifetime. Longer than
# the instant window because the customer has waited weeks for the work;
# see store.views.review_vault_upload_approve.
DOWNLOAD_TOKEN_CUSTOM_HOURS = 8760  # 365 days

# Customer self-service cancellation window for instant e-products.
# After this many days from order creation, the online cancellation gate
# (Order.evaluate_cancellation_details) refuses.
EPRODUCT_CANCEL_WINDOW_DAYS = 7

# Row-lock window for CustomerVoucher rows held by an active checkout
# session. Set in carts.views.checkout (lock acquisition) and
# carts.views.cart (stale-lock self-healing release). Stale locks past
# this window are reclaimable by another session.
VOUCHER_LOCK_MINUTES = 15

# Row-lock window for UserPerk rows held by an active checkout session.
# Same shape as VOUCHER_LOCK_MINUTES, different resource. Both are
# written and released together in the same checkout transaction, but
# they govern independent tables and must stay independently tunable.
PERK_LOCK_MINUTES = 15