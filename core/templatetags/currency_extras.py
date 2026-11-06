# core/templatetags/currency_extras.py
"""
Template filters for foreign-currency display.

The filter takes a "rate|code" string because Django template filters
accept exactly one argument. The alternative (a tag) is more verbose in
templates for what is a single-value display.

Usage:
    {% load currency_extras %}
    {{ variation.price|to_foreign:"0.1098|HKD" }}

Renders "96.53" (no symbol — the template supplies the symbol via
foreign_currency_symbol, matching the existing pattern in the cart).

Decimal end-to-end. The source value in every template call site is
ProductVariation.price or Product.lowest_price — both Decimal. The rate
is locked_rate, which is session-stored as a string but was written by
get_or_lock_checkout_rate as a 4-dp Decimal. Converting both to Decimal
via str() and quantizing via core.currency.foreign_format is the only
path that preserves the caller's last bit; float() would introduce
1-ulp drift on some prices and round the .xx5 boundary inconsistently
from the line-item path.
"""

from decimal import Decimal, InvalidOperation

from django import template

from core.currency import foreign_format


register = template.Library()


@register.simple_tag
def to_foreign(value, rate, code):
    """
    Convert a CNY value to a foreign figure.

    {% to_foreign displayed_price locked_rate foreign_currency_code %}
    """
    return _convert(value, rate, code)


@register.filter
def to_foreign_filter(value, rate_and_code):
    """
    Same conversion, filter shape (one argument). Usage:
    {{ value|to_foreign_filter:"0.1234|HKD" }}
    """
    if rate_and_code is None or "|" not in str(rate_and_code):
        return ""
    rate_str, code = str(rate_and_code).split("|", 1)
    return _convert(value, rate_str.strip(), code.strip())


def _convert(value, rate_str, code):
    if value is None or value == "":
        return ""
    try:
        rate = Decimal(str(rate_str).strip())
        code = (code or "").strip().upper()
        if not rate or not code:
            return ""
        cny = Decimal(str(value))
        return foreign_format(cny * rate, code)
    except (ValueError, TypeError, InvalidOperation):
        return ""