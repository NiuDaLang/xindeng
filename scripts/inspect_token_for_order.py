# scripts/inspect_token_for_order.py
"""
Template — edit `order_number` below before running.

Run with:
    python manage.py shell < scripts/inspect_token_for_order.py
    python manage.py shell < scripts/inspect_token_for_order.py HK-A5G7LC

Order numbers are `<country_prefix>-<sqids>`: XX- for digital-only orders,
the ISO country code for orders with a physical line (HK-, AU-, CN-, ...).
Any prefix is accepted here.
"""
import sys
from store.models import DigitalDownloadToken

# Accept an argument if one is passed; otherwise, prompt the reader to edit.
ARG = sys.argv[-1] if len(sys.argv) > 1 else None
order_number = ARG if ARG and "-" in ARG else "REPLACE_ME"

if order_number == "REPLACE_ME":
    print("Edit order_number in this script, or pass it as an argument:")
    print("    python manage.py shell < scripts/inspect_token_for_order.py <ORDER_NUMBER>")
    sys.exit(0)

t = (
    DigitalDownloadToken.objects
    .select_related('order_product__order')
    .filter(order_product__order__order_number=order_number)
    .first()
)

if not t:
    print(f"No token for order {order_number}")
else:
    op = t.order_product
    o = op.order
    print(f"order   : {o.order_number}")
    print(f"status  : {o.order_status}")
    print(f"is_ordered: {o.is_ordered}")
    print(f"token id: {t.id}")
    print(f"is_active: {t.is_active}")
    print(f"expires : {t.expires_at}")
    print(f"is_claimed: {op.is_claimed}")
    print(f"claimed_at: {op.claim_timestamp}")
    print(f"variation: {op.product_variation}")
    print(f"product : {op.product_variation.product.product_name}")