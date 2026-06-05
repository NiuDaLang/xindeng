# from .models import Category
# from carts.models import Cart, CartItem
# from carts.views import _cart_id
# from django.contrib.humanize.templatetags.humanize import intcomma


# def menu_links(request):
#     links = Category.objects.all()
#     return dict(links=links)


# def cart_item_count(request):
#     user = request.user if request.user.is_authenticated else None
#     try:
#         if user:
#             cart = Cart.objects.get(user=user) if Cart.objects.filter(user=user) else Cart.objects.create(cart_id=_cart_id(request), user=user)
#         else:
#             cart = Cart.objects.get(cart_id=_cart_id(request)) if Cart.objects.filter(cart_id=_cart_id(request)) else Cart.objects.create(cart_id=_cart_id(request))
#         cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
#             '-product_variation__product__is_physical', # True (1) before False (0)
#             'product_variation__product__is_voucher',  # False (0) before True (1)
#             'product_variation__product__product_name' # Alphabetical within groups
#         )
        
#         quantity = cart.get_items_count()
#         cart_total = cart.get_cart_total()
#         cart_total = intcomma(f"{cart_total:.2f}")

#     except CartItem.DoesNotExist:
#         quantity = 0
#         cart_total = intcomma(f"{0:.2f}")

#     return dict(cart_total=cart_total, item_count=quantity, current_cart_items=cart_items)


# context_processors.py
from .models import Category
from carts.models import Cart, CartItem
from carts.views import _cart_id


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


def cart_item_count(request):
    user = request.user if request.user.is_authenticated else None
    quantity = 0
    cart_total_value = 0.00  # Internal temp variable
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

    # 💡 CHANGE THE KEY NAME HERE TO AVOID CHEKOUT VIEW CLASHES
    return dict(header_cart_total=cart_total_value, item_count=quantity, current_cart_items=cart_items)