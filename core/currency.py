# core/currency.py
"""
Currency formatting primitives.

The single source of truth for how foreign-currency figures are
quantized and rendered across the project. Used by:
  - carts.models.CartItem.get_subtotal_foreign (line-item subtotals)
  - carts.utils.calculate_foreign_amount (shipping, offer, voucher, total)
  - store.templatetags.currency_extras.to_foreign (product and product-card display)

Before this module existed, the two paths used different rounding rules
at the .xx5 boundary — get_subtotal_foreign used ROUND_HALF_UP, while
calculate_foreign_amount used Python's format() (banker's rounding).
This meant a cart could show HK$ 98.53 for a line item and HK$ 98.52
for the same figure in the summary. Foreign_format unifies both on
ROUND_HALF_UP, matching the line-item path (which is what
get_paypal_items uses when constructing PayPal line items).

The DEFAULT symbol fallback is the bare currency code, not "$". A "$"
for an unknown code would be actively misleading; "XYZ 123.45" is at
least readable. See the 2026-11-06 design discussion.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib.humanize.templatetags.humanize import intcomma

from accounts.data import INTEGER_CURRENCIES, CURRENCY_SYMBOL


def get_currency_precision(currency_code: str) -> int:
    """0 for integer-only currencies (JPY, KRW, TWD, ...), 2 otherwise."""
    return 0 if currency_code.upper() in INTEGER_CURRENCIES else 2


def quantize_amount(value, currency_code: str) -> Decimal:
    """
    Round `value` to `currency_code`'s precision, half-up.

    Accepts Decimal, int, float, or comma-containing string; returns a
    Decimal. Half-up (not banker's) so .xx5 always rounds away from zero,
    matching get_subtotal_foreign and get_paypal_items.
    """
    precision = get_currency_precision(currency_code)
    decimal_val = Decimal(str(value).replace(",", ""))
    if precision == 0:
        return decimal_val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return decimal_val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def format_fx_value(value, currency_code: str) -> str:
    """
    Format an already-quantized Decimal value with thousands separators.
    Does NOT quantize — pass through quantize_amount first if needed.
    """
    precision = get_currency_precision(currency_code)
    return intcomma(f"{value:.{precision}f}")


def foreign_symbol(currency_code: str) -> str:
    """
    The display symbol for a currency code, or the bare code if unknown.

    Falling back to the bare code (e.g. "XYZ 123.45") rather than "$" or
    "?" so an unrecognised cookie value renders readably. The cookie is
    normally written by carts.views.set_currency, which only accepts the
    codes in accounts.data.CURRENCIES, but a hand-crafted cookie would
    reach this path.
    """
    code = (currency_code or "").upper().strip()
    return CURRENCY_SYMBOL.get(code, code or "—")


def foreign_format(value, currency_code: str) -> str:
    """
    Quantize then format in one call. The string counterpart of
    `quantize_amount` for cases that only need the display form.

    Half-up rounding via quantize_amount; intcomma grouping via
    format_fx_value. Both steps reuse the same underlying Decimal, so
    the string returned here always represents the exact Decimal
    quantize_amount would return.
    """
    quantized = quantize_amount(value, currency_code)
    return format_fx_value(quantized, currency_code)