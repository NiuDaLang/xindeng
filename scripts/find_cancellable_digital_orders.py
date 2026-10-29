from store.models import DigitalDownloadToken

CANCELLABLE = ('Processing', 'Hold_Pending', 'Pending', 'Paid')

qs = (
    DigitalDownloadToken.objects
    .select_related(
        'order_product__order',
        'order_product__product_variation__product',
    )
    .filter(
        is_active=True,
        order_product__is_claimed=False,
        order_product__order__order_status__in=CANCELLABLE,
    )
    .order_by('-order_product__order__ordered_at', '-created_at')
)

print('Candidate orders:')
print('=' * 100)
seen = set()
for t in qs:
    op = t.order_product
    o = op.order
    if o.order_number in seen:
        continue
    seen.add(o.order_number)
    p = op.product_variation.product
    kind = p.digital_fulfillment_type if p.is_digital else 'PHYSICAL'
    buyer = 'MEMBER' if o.user_id else 'GUEST'
    print(
        f"{o.order_number:20s}"
        f" status={o.order_status:14s}"
        f" buyer={buyer:7s}"
        f" kind={kind:8s}"
        f" ordered_at={o.ordered_at}"
        f" product={p.product_name!r}"
        f" token={str(t.id)[:8]}"
        f" expires={t.expires_at.date()}"
    )
print('=' * 100)
print('count:', len(seen))