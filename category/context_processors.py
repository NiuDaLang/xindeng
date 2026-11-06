# category/context_processors.py
from .models import Category
from carts.models import Cart, CartItem
from carts.views import _cart_id
from carts.utils import get_currency_format, get_or_lock_checkout_rate
from core.currency import foreign_format, foreign_symbol
from decimal import Decimal


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def cart_item_count(request):
    user = request.user if request.user.is_authenticated else None
    quantity = 0
    cart_total_value = '0.00'  # Internal temp variable
    cart_items = []

    try:
        if user:
            cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': _cart_id(request)})
        else:
            cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        
        if cart:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
                '-product_variation__product__is_physical',
                'product_variation__product__is_voucher',
                'product_variation__product__product_name'
            )
            quantity = cart.get_items_count()
            cart_total_value = cart.get_cart_total()

    except Exception as e:
        print(f"[Context Processor Exception] Global Cart Sync Failed: {str(e)}")
        quantity = 0
        cart_total_value = 0.00
        cart_items = []

    try:
        is_integer, code = get_currency_format(request)
        rate = request.session.get("locked_rate")
        if rate and code and code != "CNY":
            cny_total = Decimal(str(cart_total_value).replace(",", ""))
            header_cart_total_foreign = foreign_format(cny_total * Decimal(str(rate)), code)
            foreign_currency_symbol = foreign_symbol(code)
        else:
            header_cart_total_foreign = None
            foreign_currency_symbol = None
    except Exception:
        header_cart_total_foreign = None
        foreign_currency_symbol = None

    # 💡 CHANGE THE KEY NAME HERE TO AVOID CHEKOUT VIEW CLASHES
    return dict(
        item_count=quantity, 
        header_cart_total=cart_total_value, 
        current_cart_items=cart_items,
        header_cart_total_foreign=header_cart_total_foreign,
        foreign_currency_symbol=foreign_currency_symbol,
    )