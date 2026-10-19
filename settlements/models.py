# settlements/models.py

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from orders.models import Order
from creators.models import CreatorProfile

class ArtisanSettlementLine(models.Model):
    """
    Represents the financial settlement for a single artisan on a single order.
    One row per (order, artisan) pair.
    """
    class DeliveryMode(models.TextChoices):
        DIRECT = 'DIRECT', 'Direct Ship'
        TRANSIT = 'TRANSIT', 'Via Platform Transit'

    class Status(models.TextChoices):
        UNAID = 'UNAID', 'Unpaid'
        PAID = 'PAID', 'Paid'

    # --- Identity ---
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='artisan_settlement_lines')
    artisan = models.ForeignKey(CreatorProfile, on_delete=models.PROTECT, related_name='settlement_lines')

    # --- State & Metadata ---
    delivery_mode = models.CharField(max_length=10, choices=DeliveryMode.choices, blank=True, default="")
    is_finalised = models.BooleanField(
        default=False,
        help_text="Set to True by admin when the courier invoice has been reconciled. "
                  "The artisan can only see the net payable amount when this is True."
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNAID)
    paid_date = models.DateField(null=True, blank=True)
    payment_evidence = models.FileField(
        upload_to='settlement_payment_evidence/',
        null=True, blank=True,
        help_text="Upload transfer receipt or other proof of payment."
    )

    # --- Financial Fields ---
    product_revenue = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Auto-computed from OrderProduct.subtotal at line creation. Admin can override."
    )
    shipping_charged_to_customer = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Allocated share of Order.shipping_cost. Admin can override."
    )
    website_margin_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.0000"),
        help_text="Per-artisan, optionally per-product/variation margin rate (e.g., 0.15 for 15%)."
    )
    website_margin_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Computed as product_revenue x website_margin_rate. Stored for audit."
    )

    # --- Manual Cost Fields (Platform-Fronted) ---
    shipping_paid_by_website = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Manual entry from the 运营点's courier statement."
    )
    tax_paid_by_website = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Manual entry. Sum of DDP customs duty + GST/VAT/consumption tax paid by platform."
    )

    # --- Manual Cost Fields (Artisan-Fronted) ---
    shipping_paid_by_artisan = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Manual entry from the artisan's courier receipt."
    )
    tax_paid_by_artisan = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Manual edge case: artisan paid DDP duty themselves."
    )

    # --- Other Adjustments ---
    other_costs = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Free-form manual adjustment. Can be positive or negative."
    )
    other_costs_note = models.TextField(blank=True, default="")
    receipt_reference = models.CharField(
        max_length=255, blank=True, default="",
        help_text="Courier bill number for shipping_paid_by_artisan / shipping_paid_by_website."
    )

    # --- FX & Audit ---
    settlement_exchange_rate = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="Snapshot of Order.locked_exchange_rate at line creation. Used for audit."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['order', 'artisan'], name='unique_settlement_per_order_artisan')
        ]
        verbose_name = "Artisan Settlement Line"
        verbose_name_plural = "Artisan Settlement Lines"

    def __str__(self):
        return f"Settlement for {self.artisan.display_name} on Order #{self.order.order_number}"

    @property
    def gross_payable_to_artisan(self) -> Decimal:
        return self.product_revenue + self.shipping_charged_to_customer

    @property
    def net_payable_to_artisan(self) -> Decimal:
        """
        Computes the net amount owed to the artisan in CNY.
        Formula confirmed against the 2026-10-19 session memo.
        """
        # Ensure all values are treated as Decimals
        return (
            self.gross_payable_to_artisan
            - self.website_margin_amount
            - self.shipping_paid_by_website
            - self.tax_paid_by_website
            + self.shipping_paid_by_artisan
            + self.tax_paid_by_artisan
            + self.other_costs
        )


class LogisticsAdvance(models.Model):
    """
    One row per (order, individual, month) for a courier outlay by a
    team member, batched for reimbursement.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUBMITTED = 'SUBMITTED', 'Submitted for Reimbursement'
        REIMBURSED = 'REIMBURSED', 'Reimbursed'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logistics_advances')
    individual = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='logistics_advances_made'
    )
    month = models.DateField(help_text="Set to the first day of the month for aggregation.")
    amount_advanced = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_reference = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    reimbursed_at = models.DateTimeField(null=True, blank=True)
    reimbursed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_reference = models.CharField(max_length=255, blank=True, default="")
    notes = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month', 'individual']
        verbose_name = "Logistics Advance"
        verbose_name_plural = "Logistics Advances"

    def __str__(self):
        return f"Advance by {self.individual.username} for Order #{self.order.order_number} ({self.month.strftime('%Y-%m')})"