from django.contrib import admin
from .models import Cart, CartItem, ShippingCharge, CheckoutInfo, ProformaInvoice


class CartAdmin(admin.ModelAdmin):
    list_display = ("cart_id", "user", "date_added")
    search_fields = ("cart_id", "user", "date_added")

class ShippingChargeAdmin(admin.ModelAdmin):
    list_display = ("shipped_from", "zone", "country_code", "service_name", "min_charge", "min_charge_weight", "add_cost_unit_price", "add_cost_weight", "other_fee", "for_small_package", "is_express", "is_standard", "is_economical", "is_active", "notes", "created_at", "updated_at")
    search_fields = ("id", "shipped_from", "zone", "service_name", "is_active", "notes")
    list_filter = ("is_active", "is_express", "is_standard", "is_economical", "for_small_package", "created_at", "updated_at")
    list_per_page = 15

# Register your models here.
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem)
admin.site.register(ShippingCharge, ShippingChargeAdmin)
admin.site.register(CheckoutInfo)
admin.site.register(ProformaInvoice)