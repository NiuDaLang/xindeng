from django.db import models
from accounts.models import Account, Perk
from accounts.data import DESTINATIONS_INCL_DIGITAL, INTEGER_CURRENCIES
from django.core.validators import MinValueValidator
from store.models import ProductVariation
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.humanize.templatetags.humanize import intcomma


# Create your models here.
class Cart(models.Model):
    cart_id             = models.CharField(max_length=250, blank=True)
    user                = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='cart_user', blank=True, null=True)
    date_added          = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
    def get_items_count(self):
        cart_items = CartItem.objects.filter(cart=self)
        return sum(item.quantity for item in cart_items)
    
    def get_cart_total(self):
        cart_items = CartItem.objects.filter(cart=self)
        total = sum(item.subtotal for item in cart_items)
        return intcomma(f"{total:.2f}")
    
    def get_cart_total_foreign(self, currency_code, exchange_rate):
        """Sums up pre-quantized line items to ensure perfect horizontal stability."""
        cart_items = self.cartitem_set.filter(is_active=True)
        total = sum(item.get_subtotal_foreign(currency_code, exchange_rate) for item in cart_items) or Decimal('0')
        precision = 0 if currency_code in INTEGER_CURRENCIES else 2
        return intcomma(f"{total:.{precision}f}")
    
    def get_physical_products_subtotal(self):
        cart_items = CartItem.objects.filter(cart=self, product_variation__product__is_physical=True, product_variation__product__is_voucher=False)
        total = sum(item.subtotal for item in cart_items)
        return intcomma(f"{total:.2f}")
    
    def get_physical_products_subtotal_foreign(self, currency_code, exchange_rate):
        cart_items = self.cartitem_set.filter(
            is_active=True,
            product_variation__product__is_physical=True,
            product_variation__product__is_voucher=False
        )
        total = sum(item.get_subtotal_foreign(currency_code, exchange_rate) for item in cart_items) or Decimal('0')
        precision = 0 if currency_code in INTEGER_CURRENCIES else 2
        return intcomma(f"{total:.{precision}f}")
    
    def get_e_products_subtotal(self):
        cart_items = CartItem.objects.filter(cart=self, product_variation__product__is_physical=False, product_variation__product__is_voucher=False)
        total = sum(item.subtotal for item in cart_items)
        return intcomma(f"{total:.2f}")
    
    def get_e_products_subtotal_foreign(self, currency_code, exchange_rate):
        cart_items = self.cartitem_set.filter(
            is_active=True,
            product_variation__product__is_physical=False,
            product_variation__product__is_voucher=False
        )
        total = sum(item.get_subtotal_foreign(currency_code, exchange_rate) for item in cart_items) or Decimal('0')
        precision = 0 if currency_code in INTEGER_CURRENCIES else 2
        return intcomma(f"{total:.{precision}f}")
    
    def get_voucher_products_subtotal(self):
        cart_items = CartItem.objects.filter(cart=self, product_variation__product__is_voucher=True)
        total = sum(item.subtotal for item in cart_items)
        return intcomma(f"{total:.2f}")
    
    def get_voucher_products_subtotal_foreign(self, currency_code, exchange_rate):
        cart_items = self.cartitem_set.filter(is_active=True, product_variation__product__is_voucher=True)
        total = sum(item.get_subtotal_foreign(currency_code, exchange_rate) for item in cart_items) or Decimal('0')
        precision = 0 if currency_code in INTEGER_CURRENCIES else 2
        return intcomma(f"{total:.{precision}f}")
    
    def get_cart_total_ex_voucher(self):
        cart_items = CartItem.objects.filter(cart=self, product_variation__product__is_voucher=False)
        total = sum(item.subtotal for item in cart_items)
        return intcomma(f"{total:.2f}")
    
    def get_cart_total_ex_voucher_foreign(self, currency_code, exchange_rate):
        cart_items = CartItem.objects.filter(cart=self, product_variation__product__is_voucher=False)
        total = sum(Decimal(intcomma(f"{(item.subtotal * Decimal(exchange_rate)):.0f}").replace(",", "")
                            if currency_code in INTEGER_CURRENCIES else 
                            intcomma(f"{(item.subtotal * Decimal(exchange_rate)):.2f}").replace(",", "")
                            ) for item in cart_items)
        return intcomma(f"{total:.0f}" if currency_code in INTEGER_CURRENCIES else f"{total:.2f}")
    
    # Cart Model
    @property
    def needs_shipping(self):
        """Returns True if there is at least one physical product in the cart."""
        return self.cartitem_set.filter(product_variation__product__is_physical=True).exists()    


class CartItem(models.Model):
    product_variation   = models.ForeignKey(ProductVariation, related_name='product_sku', on_delete=models.CASCADE, null=True)
    cart                = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity            = models.PositiveIntegerField()
    is_active           = models.BooleanField(default=True)
    user                = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='user', blank=True, null=True)

    def __str__(self):
        return f"{self.product_variation.product} - [{self.product_variation}]"
    
    @property
    def subtotal(self):
        """Absolute unquantized baseline subtotal truth layer in core CNY currency."""
        return self.product_variation.price * self.quantity

    def get_subtotal_foreign(self, currency_code, exchange_rate):
        """
        Locks down line-item foreign currency precision at the atomic source.
        Truncates/Rounds early to treat foreign totals exactly like native CNY.
        """
        is_integer = currency_code.upper() in INTEGER_CURRENCIES
        rate_decimal = Decimal(str(exchange_rate))
        
        # Calculate raw aggregate conversion for this specific line item block
        raw_foreign_subtotal = self.subtotal * rate_decimal
        
        # Enforce your standardized truncation/rounding rule safely
        if is_integer:
            # For integer-only currencies like JPY, truncate fractions immediately
            return raw_foreign_subtotal.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        else:
            # For standard currencies, cut off everything past the 2nd decimal place
            return raw_foreign_subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    

class ShippingCharge(models.Model):
    shipped_from        = models.CharField(max_length=100)
    zone                = models.CharField(max_length=100)
    country_code        = models.CharField(max_length=2, default="00")
    service_name        = models.CharField(max_length=100)
    min_charge          = models.DecimalField(max_digits=10, decimal_places=5, default=0.00)
    min_charge_weight   = models.PositiveIntegerField(default=1) # gram
    add_cost_unit_price = models.DecimalField(max_digits=10, decimal_places=5, default=0.00)
    add_cost_weight     = models.PositiveIntegerField(default=1) # gram
    other_fee           = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    for_small_package   = models.BooleanField(default=False)
    is_express          = models.BooleanField(default=False)
    is_standard         = models.BooleanField(default=False)
    is_economical       = models.BooleanField(default=False)
    is_active           = models.BooleanField(default=True)
    notes               = models.CharField(max_length=500, blank=True, null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Charge service for {self.zone}: {self.service_name}"

    class Meta:
        verbose_name = "Shipping Charge"
        verbose_name_plural = "Shipping Charges"


class CheckoutInfo(models.Model):
    DESTINATION_SOURCE = [
        ('DEFAULT',     'Default'),
        ('ADDRESS_BOOK','Address Book'),
    ]

    user                            = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='checkout_user', blank=True, null=True)
    cart                            = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='checkout_cart', blank=True, null=True)
    cart_total                      = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    destination_source              = models.CharField(max_length=20, choices=DESTINATION_SOURCE, default="DEFAULT")
    default_zone                    = models.CharField(max_length=20, blank=True, null=True)
    default_destination             = models.CharField(max_length=100, blank=True, null=True)
    address_id                      = models.CharField(max_length=5, blank=True, null=True)
    shipping_cost                   = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    offer_code                      = models.CharField(max_length=100, blank=True, null=True)
    discount_amount                 = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    voucher_applied                 = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax_amount                      = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount                     = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_due                       = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    # Field to track if specific destination requirements (like Taiwan ID) are validated
    requirements_validated          = models.BooleanField(default=False)
    display_mode                    = models.CharField(max_length=25, blank=True, null=True) 

    cart_total_foreign              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost_amount_foreign    = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount_amount_foreign         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax_amount_foreign              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    duty_amount_foreign             = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    applied_voucher_amount_foreign  = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due_foreign               = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    locked_exchange_rate            = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    currency_code                   = models.CharField(max_length=10, default="USD", blank=True, null=True)

    tax_calculated                  = models.BooleanField(default=False)

    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        user = self.user.username if self.user else "Guest"
        return f"Checkout info for {user}'s cart {self.cart.id}, created on {self.created_at}"
    
    @property
    def is_calculation_complete(self):
        """Returns True only if both shipping and tax have been processed."""
        # Ensure values are greater than zero (or check if a 'calculated' flag is True)
        # Note: tax_amount can be 0 for HK/Macao, so check a flag or destination
        return self.shipping_cost > 0 and self.default_destination is not None


class ProformaInvoice(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('PAYPAL', 'PayPal Express Checkout'),
        ('BANK_TRANSFER', 'Bank Transfer / WeChat Pay Manual Hold'),
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    inventory_hold_expiry = models.DateTimeField(blank=True, null=True)
    
    # Track the active display mode to easily check product rules during presentation layers
    display_mode = models.CharField(max_length=25, blank=True, null=True) 

    # User / Buyer tracking (Null if guest checkout)
    cart                    = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True)
    user                    = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    proforma_order_number   = models.CharField(max_length=100, blank=True, null=True)

    # Buyer Contact line (Always present for order communications/receipts)
    email                   = models.EmailField(max_length=100, blank=True, null=True)

    # RECIPIENT'S Delivery details (Physical shipping destination only)
    recipient_first_name    = models.CharField(max_length=50, blank=True, null=True)
    recipient_last_name     = models.CharField(max_length=50, blank=True, null=True)
    recipient_mobile_area   = models.CharField(blank=True, null=True, max_length=15)
    recipient_mobile_number = models.CharField(blank=True, null=True, max_length=40)

    # Useful for shipping APIs (e.g., combined full phone if needed)
    recipient_phone         = models.CharField(max_length=20, blank=True, null=True)

    # shipping address
    is_default_address      = models.BooleanField(default=False)
    address_line_1          = models.CharField(max_length=255, blank=True, null=True) # St, Apt, Suite, Landmark
    address_line_2          = models.CharField(max_length=255, blank=True, null=True)
    city                    = models.CharField(max_length=100, blank=True, null=True)
    state_province_region   = models.CharField(max_length=100, blank=True, null=True)
    country                 = models.CharField(max_length=2, choices=DESTINATIONS_INCL_DIGITAL, default="", blank=False) # ISO 3166-1 alpha-2 (e.g., 'US', 'FR')
    postal_code             = models.CharField(max_length=20, blank=True, null=True) # Optional for global

    # vocher purchase
    recipient_email         = models.EmailField(max_length=100, blank=True, null=True)
    gift_message            = models.TextField(max_length=500, blank=True, null=True)

    # delivery instruction
    delivery_note           = models.TextField(max_length=250, blank=True, null=True)
    do_not_send_invoice     = models.BooleanField(default=False)

    # Generic field to hold Taiwan ID, Korea PCCC, etc.
    destination_tax_id      = models.CharField(max_length=50, blank=True, null=True)

    # summary
    cart_total              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost           = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount                = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax                     = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    voucher_applied         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due               = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)

    cart_total_foreign              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    shipping_cost_amount_foreign    = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    discount_amount_foreign         = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    tax_amount_foreign              = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    applied_voucher_amount_foreign  = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    total_due_foreign               = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], default=0.0)
    locked_exchange_rate            = models.DecimalField(max_digits=10, decimal_places=4, default=1.0)
    currency_code                   = models.CharField(max_length=10, default="USD", blank=True, null=True)

    google_place_id         = models.CharField(max_length=255, blank=True, null=True) # Google recommends unconstrained lengths as Place IDs can grow
    latitude                = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True) # standard accuracy cap
    longitude               = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_verified_by_google   = models.BooleanField(default=False)

    # status
    is_ordered              = models.BooleanField(default=False)
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.proforma_order_number
    
    class Meta:
        verbose_name = "Proforma Invoice"
        verbose_name_plural = "Proforma Invoices"
