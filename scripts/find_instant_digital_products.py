from store.models import Product, ProductVariation

qs = (
    ProductVariation.objects
    .select_related('product', 'product__category')
    .filter(
        is_available=True,
        stock__gt=0,
        product__is_active=True,
        product__is_deleted=False,
        product__status='Published',
        product__is_digital=True,
        product__digital_fulfillment_type='INSTANT',
    )
    .order_by('product__product_name')
)

print('Published INSTANT digital variations available to buy:')
print('=' * 100)
for v in qs:
    p = v.product
    print(
        f"  pk={v.pk:4d}  "
        f"{p.product_name!r:40s}  "
        f"category={p.category.slug:20s}  "
        f"price=CNY {v.price}  "
        f"digital_file_path={v.digital_file_path or '(none)'}"
    )
print('=' * 100)
print('count:', qs.count())