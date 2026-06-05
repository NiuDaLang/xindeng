from django.contrib import admin
from .models import Payment, Order, OrderProduct


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("payment_id", "user", "payment_method", "amount_paid", "status", "created_at")
    search_fields = ("payment_id", "user", "payment_method", "status")
    list_filter = ("status", "created_at")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "payment", "order_number", "recipient_first_name", "recipient_last_name", "email", "total_due", "is_ordered", "order_status", "created_at")
    search_fields = ("user",  "payment", "order_number", "email", "order_status")
    list_filter = ("user",  "payment", "order_number", "email", "order_status")

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "created_at",)
    search_fields = ("order", "user", "created_at",)


admin.site.register(Payment, PaymentAdmin)   
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)