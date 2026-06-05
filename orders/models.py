from django.db import models
from accounts.models import Account
from accounts.data import DESTINATIONS_FOR_INPUT
from django.core.validators import MinValueValidator
from store.models import ProductVariation, Product
from carts.models import ProformaInvoice

# Create your models here.
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('PaypPal', 'PayPal'),
        ('Stripe', 'Stripe'),
        ('AliPay', 'AliPay'),
        ('WeChat', 'WeChat'),
        ('Cash On Delivery', 'Cash On Delivery'),
        ('Credit Card', 'Credit Card'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Mobile Payment', 'Mobile Payment'),
        ('Other', 'Other'),
    )
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
        ('Refunded', 'Refunded'),
    )
    
    user            = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    invoice         = models.ForeignKey(ProformaInvoice, on_delete=models.CASCADE, blank=True, null=True)
    order_id        = models.CharField(max_length=100, blank=True, null=True)
    payment_id      = models.CharField(max_length=100)
    payer_id        = models.CharField(max_length=100, blank=True, null=True)
    payment_method  = models.CharField(max_length=100, choices=PAYMENT_METHODS, default="", blank=False)
    amount_paid     = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0.00)
    currency        = models.CharField(max_length=3, default="CNY")
    exchange_rate   = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    cny_equivalent  = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status          = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="", blank=False)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.payment_id
    
    def get_payment_method(self):
        if self.payment_method == "paypal":
            return "PayPal"
        elif self.payment_method == "stripe":
            return "Stripe"
        elif self.payment_method == "alipay":
            return "AliPay"
        elif self.payment_method == "wechat":
            return "WeChat"
        elif self.payment_method == "cash on delivery":
            return "Cash on Delivery"
        elif self.payment_method == "credit card":
            return "Credit Card"
        elif self.payment_method == "bank transfer":
            return "Bank Transfer"
        elif self.payment_method == "mobile payment":
            return "Mobile Payment"
        elif self.payment_method == "other":
            return "Other"
        else:
            return "Unknown"


class Order(models.Model):
    STATUS = (
        ('New', 'New'), # On Payment Approval -> send payment received email
        ('Processing', 'Processing'), # after confirmation email
        ('Shipped', 'Shipped'), # after shipped email
        ('Completed', 'Completed'), # after parcel received
        ('Cancelled', 'Cancelled'), # manual input, after cancellation
    )
    user                    = models.ForeignKey(Account, on_delete=models.SET_NULL, blank=True, null=True)
    payment                 = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number            = models.CharField(max_length=20)

    # Buyer Context line (Used directly for your auto-generated email loops!)
    email                   = models.EmailField(max_length=100, blank=True, null=True)

    # RECIPIENT'S Physical Package Delivery Details (Renamed)
    recipient_first_name    = models.CharField(max_length=50, blank=True, null=True)
    recipient_last_name     = models.CharField(max_length=50, blank=True, null=True)
    recipient_mobile_area   = models.CharField(blank=True, null=True, max_length=15)
    recipient_mobile_number = models.CharField(blank=True, null=True, max_length=40)

    # Physical delivery destination metrics
    address_line_1          = models.CharField(max_length=255, blank=True, null=True) # St, Apt, Suite, Landmark
    address_line_2          = models.CharField(max_length=255, blank=True, null=True)
    city                    = models.CharField(max_length=100, blank=True, null=True)
    state_province_region   = models.CharField(max_length=100, blank=True, null=True)
    country                 = models.CharField(max_length=2, choices=DESTINATIONS_FOR_INPUT, default="", blank=False) # ISO 3166-1 alpha-2 (e.g., 'US', 'FR')
    postal_code             = models.CharField(max_length=20, blank=True, null=True) # Optional for global
    delivery_note           = models.TextField(max_length=250, blank=True, null=True)
    do_not_send_invoice     = models.BooleanField(default=False)

    # Generic field to hold Taiwan ID, Korea PCCC, etc.
    destination_tax_id      = models.CharField(max_length=50, blank=True, null=True)

    product_total           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount                = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax                     = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount             = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    voucher_applied         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due               = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)

    product_total_foreign   = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost_foreign   = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount_foreign        = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax_foreign             = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount_foreign     = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    voucher_applied_foreign = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due_foreign       = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)

    locked_exchange_rate    = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)

    ip                      = models.CharField(blank=True, max_length=20)
    is_ordered              = models.BooleanField(default=False)
    email_sent              = models.BooleanField(default=False)
    order_status            = models.CharField(max_length=100, choices=STATUS, default="", blank=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_number
    

class OrderProduct(models.Model):
    order                   = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment                 = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user                    = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    product                 = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variation       = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, blank=True, null=True)
    quantity                = models.IntegerField()
    product_price           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    ordered                 = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product_variation)
    
    def get_subtotal(self):
        return self.product_price * self.quantity