from django.db import models
from accounts.models import Account
from accounts.data import DESTINATIONS_FOR_INPUT
from django.core.validators import MinValueValidator
from store.models import ProductVariation, Product
from carts.models import ProformaInvoice
from accounts.models import CustomerVoucher
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('PayPal', 'PayPal'),
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
    ORDER_STATUS_CHOICES = [
        ('Hold_Pending', 'Wait Pending ｜ 待付款'),
        ('Processing', 'Processing ｜ 處理中'),
        ('Partly_Dispatched', 'Partly Dispatched ｜ 部分發貨'),
        ('All_Dispatched', 'All Dispatched ｜ 已全部發貨'),
        ('Delivered', 'Delivered ｜ 已妥投完成'),
        ('Cancelled', 'Cancelled ｜ 已取消'),
    ]
    
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

    # E-VOUCHER RECIPIENT's Details
    recipient_email         = models.EmailField(max_length=100, blank=True, null=True)
    gift_message            = models.TextField(max_length=500, blank=True, null=True)

    # Physical delivery destination metrics
    address_line_1          = models.CharField(max_length=255, blank=True, null=True)
    address_line_2          = models.CharField(max_length=255, blank=True, null=True)
    city                    = models.CharField(max_length=100, blank=True, null=True)
    state_province_region   = models.CharField(max_length=100, blank=True, null=True)
    country                 = models.CharField(max_length=2, choices=DESTINATIONS_FOR_INPUT, default="", blank=False)
    postal_code             = models.CharField(max_length=20, blank=True, null=True)
    delivery_note           = models.TextField(max_length=250, blank=True, null=True)
    do_not_send_invoice     = models.BooleanField(default=False)

    # Generic field to hold Taiwan ID, Korea PCCC, etc.
    destination_tax_id      = models.CharField(max_length=50, blank=True, null=True)

    # Financial Totals (Base CNY)
    product_total           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount                = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax                     = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount             = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    voucher_applied         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due               = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)

    # Financial Totals (Foreign Currency)
    product_total_foreign   = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost_foreign   = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount_foreign        = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax_foreign             = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount_foreign     = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    voucher_applied_foreign = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due_foreign       = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)

    locked_exchange_rate    = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    currency_code           = models.CharField(max_length=10, default="USD", blank=True, null=True)

    # Control Metadata Flags
    ip                      = models.CharField(blank=True, max_length=20)
    is_ordered              = models.BooleanField(default=False)
    is_dispatched           = models.BooleanField(default=False)
    ordered_at              = models.DateTimeField(blank=True, null=True)
    inventory_hold_expiry   = models.DateTimeField(blank=True, null=True)
    order_status            = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default="Hold_Pending", blank=False)
    email_sent              = models.BooleanField(default=False) # 🏦 Tracks bank hold instruction dispatches
    payment_email_sent      = models.BooleanField(default=False) # Tracks absolute paid confirmation receipts separately

    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    # Set only upon true payment clearance
    def __str__(self):
        return self.order_number
    
    def update_fulfillment_status(self):
        """
        🌟 CHRONO LOGIC ORDER STATUS ENGINE
        Analyzes item categories and fulfillment lines to automatically 
        apply granular order statuses across split shipments matching ORDER_STATUS_CHOICES.
        """
        lines = self.orderproduct_set.all()
        if not lines.exists():
            return

        # 1. Check status groupings across your product catalogue variations
        total_items = lines.count()
        physical_lines = lines.filter(product_variation__product__is_physical=True)
        voucher_lines = lines.filter(product_variation__product__is_voucher=True)
        instant_digital_lines = lines.filter(
            product_variation__product__is_digital=True, 
            product_variation__product__digital_fulfillment_type='INSTANT'
        )
        custom_digital_lines = lines.filter(
            product_variation__product__is_digital=True, 
            product_variation__product__digital_fulfillment_type='CUSTOM'
        )

        # 2. Count lines actively cleared by shipment passes or admin actions
        dispatched_physical_count = physical_lines.filter(is_dispatched=True).count()
        dispatched_custom_digital_count = custom_digital_lines.filter(is_dispatched=True).count()

        # 3. Vouchers and Instant Digitals are auto-fulfilled instantly upon successful checkout payment
        auto_fulfilled_count = voucher_lines.count() + instant_digital_lines.count()
        total_fulfilled_lines = dispatched_physical_count + dispatched_custom_digital_count + auto_fulfilled_count

        # 4. State Router Logic Gate Mapping Matrix
        if total_fulfilled_lines == 0:
            self.order_status = 'Processing'
        elif total_fulfilled_lines < total_items:
            self.order_status = 'Partly_Dispatched'
        elif total_fulfilled_lines == total_items:
            # If there are physical lines, it shifts to All_Dispatched (waiting for delivery).
            # If it contains digital goods or self-vouchers only, it moves instantly to Delivered!
            if physical_lines.exists():
                self.order_status = 'All_Dispatched'
            else:
                self.order_status = 'Delivered'

        # Note: We do not call self.save() here since your views and signals 
        # handle committing the fields via update_fields=['order_status'] atomically!


class OrderProduct(models.Model):
    order                   = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment                 = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user                    = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    product                 = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variation       = models.ForeignKey(ProductVariation, on_delete=models.CASCADE, blank=True, null=True)
    quantity                = models.IntegerField()
    product_price           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    ordered                 = models.BooleanField(default=False)
    is_dispatched           = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.product_variation)
    
    def get_subtotal(self):
        return self.product_price * self.quantity
    

class OrderVoucherUsage(models.Model):
    order               = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="voucher_usages")
    voucher             = models.ForeignKey(CustomerVoucher, on_delete=models.CASCADE)
    amount_deducted     = models.DecimalField(max_digits=10, decimal_places=2)
    created_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 🌟 THE SNAP FIX: Cast the UUID object explicitly into a text string using str() 
        # so that your [:8] bracket slicing operator can run securely without crashing!
        voucher_uuid_str = str(self.voucher.id)
        short_voucher_id = voucher_uuid_str[:8].upper()
        
        return f"Order {self.order.order_number} - Voucher #{short_voucher_id} (-CNY {self.amount_deducted})"
    

@receiver(post_save, sender=OrderProduct)
def auto_recalculate_order_fulfillment_state(sender, instance, created, **kwargs):
    """
    🌟 CHRONO STATUS SYNC TRIGGER
    Fires automatically whenever an individual OrderProduct line item is modified.
    Forces the parent Order to re-evaluate and upgrade its global status choice natively.
    """
    # Verify that this row is actually bound to a valid parent transaction record
    if instance.order:
        parent_order = instance.order
        
        # Trigger your model's status engine to re-run its checks
        parent_order.update_fulfillment_status()
        
        # Save the updated status string value firmly to the disk drive
        parent_order.save(update_fields=['order_status'])
        print(f"⚡ SIGNAL SYNC: Recalculated status for Order #{parent_order.order_number} to: {parent_order.order_status}")
