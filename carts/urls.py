from django.urls import path
from . import views


urlpatterns = [
    # currency
    path("set_currency/", views.set_currency, name="set_currency"),
    path("update_exchange_rate_api/", views.update_exchange_rate_api, name="update_exchange_rate_api"),

    # cart
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("get_cart_item_info/", views.get_cart_item_info, name="get_cart_item_info"),
    path("cart/", views.cart, name="cart"),

    path("calculate_shipping/", views.calculate_shipping, name="calculate_shipping"),
    path("clear_shipping_session/", views.clear_shipping_session, name="clear_shipping_session"), 
    path("reset_shipping_fragment/", views.reset_shipping_fragment, name="reset_shipping_fragment"),

    path("apply_offer/", views.apply_offer, name="apply_offer"), 
    path("reset_offer/", views.reset_offer, name="reset_offer"), 

    path("apply_voucher/", views.apply_voucher, name="apply_voucher"), 
    path("reset_voucher/", views.reset_voucher, name="reset_voucher"), 

    path("update_cart_item_qty/<int:item_id>", views.update_cart_item_qty, name="update_cart_item_qty"), 
    path("add_wish_to_cart/<int:wish_id>", views.add_wish_to_cart, name="add_wish_to_cart"),
    path("delete_cart_item/<int:item_id>", views.delete_cart_item, name="delete_cart_item"),

    path("add_to_wishlist/<int:item_id>", views.add_to_wishlist, name="add_to_wishlist"),
    path("delete_wishlist_item/<int:wish_id>", views.delete_wishlist_item, name="delete_wishlist_item"),

    path("add_to_favorite/<int:variation_id>", views.add_to_favorite, name="add_to_favorite"),

    # checkout
    path("checkout/", views.checkout, name="checkout"),

    # path("calculate_tax_duty_api/", views.calculate_tax_duty_api, name="calculate_tax_duty_api"),
    # path("get_compliance_fields/", views.get_compliance_fields, name="get_compliance_fields"),
]
