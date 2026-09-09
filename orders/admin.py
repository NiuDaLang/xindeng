from datetime import timedelta
from .models import Payment, OrderVoucherUsage, Order, OrderProduct, OrderInquiry
from store.models import DigitalDownloadToken
from carts.models import ProformaInvoice, CheckoutInfo, Cart, CartItem
from store.models import ProductVariation
from accounts.models import CustomerVoucher
from django.contrib import admin, messages
from django.db import transaction
from django.utils import timezone
from .tasks import send_order_confirmation_email_task, send_gift_voucher_email_task, send_e_product_email_task, send_inquiry_notification_email_task, send_cancellation_completion_email_task
from django.urls import reverse
import decimal


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_id", "user", "payment_method", "amount_paid", "status", "created_at"]
    search_fields = ["payment_id", "user", "payment_method", "status"]
    list_filter = ["status", "created_at"]


@admin.register(OrderInquiry)
class OrderInquiryAdmin(admin.ModelAdmin):
    # Control list headers inside your admin dashboard list grid
    list_display = ('order', 'is_from_staff', 'staff_user', 'created_at')
    list_filter = ('is_from_staff', 'created_at')
    search_fields = ('order__order_number', 'message_content')
    
    # Exclude staff metrics from manual selection so Django assigns them automatically
    exclude = ('staff_user', 'is_from_staff')

    def save_model(self, request, obj, form, change):
        """
        🚀 ADMIN INTERCEPT ENGINE
        Catches dashboard manual inserts, applies staff attributes,
        and triggers your background Celery tasks automatically.
        """
        # If it's being created inside the Django Admin panel, it's definitely from staff
        if not change: # Check ensures this runs strictly on creation pass, not on sub-edits
            obj.is_from_staff = True
            obj.staff_user = request.user
            
        # Commit row item securely to the database ledger layout
        super().save_model(request, obj, form, change)
        
        # 🎯 CELERY EMAIL DISPATCH
        # This will evaluate 'is_from_staff=True' inside tasks.py and email the customer instantly!
        send_inquiry_notification_email_task.delay(obj.id)


class OrderVoucherUsageInline(admin.TabularInline):
    """
    🎯 VISUAL ENHANCEMENT:
    Displays voucher deductions directly inside the related Order detail screen.
    """
    # 🌟 CRITICAL FIX: Make sure this is the model CLASS, not a string like 'OrderVoucherUsage'
    model = OrderVoucherUsage  
    extra = 0
    readonly_fields = ['voucher', 'amount_deducted', 'created_at']
    can_delete = False


@admin.register(OrderVoucherUsage)
class OrderVoucherUsageAdmin(admin.ModelAdmin):
    """
    Independent ledger manager for tracking split voucher deductions across transactions.
    """
    list_display = [
        'order_number_link', 
        'voucher_owner', 
        'voucher_identifier', 
        'amount_deducted_display', 
        'created_at'
    ]
    
    list_filter = ['created_at']
    
    # Enable robust searching across multiple relational fields
    search_fields = [
        'order__order_number', 
        'voucher__id', 
        'voucher__purchaser_email', 
        'voucher__owner__email'
    ]
    
    # Protect systemic accounting metrics from accidental manual drift
    readonly_fields = ['order', 'voucher', 'amount_deducted', 'created_at']

    def order_number_link(self, obj):
        """Displays the matching parent order number handle."""
        return obj.order.order_number
    order_number_link.short_description = "Order Number｜訂單號"

    def voucher_owner(self, obj):
        """Displays the current registered profile owner of the voucher."""
        return obj.voucher.owner if obj.voucher.owner else "Guest / Unclaimed"
    voucher_owner.short_description = "Voucher Owner｜禮品券所有人"

    def voucher_identifier(self, obj):
        """Displays the unique database UUID key block of the voucher asset."""
        return str(obj.voucher.id)[:8] + "..."  # Truncates long UUID for clean scannability
    voucher_identifier.short_description = "Voucher ID (Short)｜券號"

    def amount_deducted_display(self, obj):
        """Formats the transaction currency metrics cleanly."""
        return f"CNY {obj.amount_deducted:.2f}"
    amount_deducted_display.short_description = "Amount Spent｜扣減金額"

    def has_add_permission(self, request):
        """Prevents staff from creating manual entries outside the checkout engine."""
        return False


@admin.action(description="Confirm Selected Bank Payments｜確認所選銀行匯款")
def confirm_bank_payment_admin_action(modeladmin, request, queryset):
    """
    Admin action to manually verify that a customer bank transfer has cleared.
    Transitions orders to a completed, active state with dynamic status recalculation.
    """
    pending_orders = queryset.filter(is_ordered=False)
    
    if not pending_orders.exists():
        messages.warning(request, "所選訂單中沒有處於「待付款」狀態的項目。 No pending orders were selected.")
        return

    processed_count = 0
    
    for order in pending_orders:
        try:
            with transaction.atomic():
                order_locked = Order.objects.select_for_update().get(id=order.id)
                if order_locked.order_status == 'Cancelled':
                    continue

                # 1. Create permanent Payment entry
                payment = Payment.objects.create(
                    user=order_locked.user,
                    payment_id=f"ADMIN_VERIFIED_{order_locked.order_number}_{int(timezone.now().timestamp())}",
                    payment_method='Bank Transfer',
                    amount_paid=order_locked.total_due,
                    status='Completed'
                )

                # 2. Update order level flags upfront
                order_locked.payment = payment
                order_locked.is_ordered = True
                order_locked.ordered_at = timezone.now()
                order_locked.save(update_fields=['payment', 'is_ordered', 'ordered_at'])                        

                # 3. Process individual lines data arrays
                order_products = OrderProduct.objects.filter(order=order_locked)

                for prod in order_products:
                    variation = ProductVariation.objects.select_for_update().get(id=prod.product_variation.id)
                    
                    if variation.product.is_voucher:
                        is_gift = order_locked.recipient_email and order_locked.recipient_email.strip().lower() != order_locked.email.strip().lower()

                        for _ in range(prod.quantity):
                            voucher = CustomerVoucher.objects.create(
                                value=prod.product_price,
                                balance=prod.product_price,
                                purchaser_email=order_locked.email,
                                owner=None if is_gift else order_locked.user,
                                registered_email=order_locked.recipient_email if is_gift else order_locked.email,
                                is_claimed=False if is_gift else True,
                                claimed_date=None if is_gift else timezone.now(),
                                is_used=False
                            )
                            if is_gift:
                                reg_link = request.build_absolute_uri(reverse('claim_voucher_url', args=[str(voucher.id)]))
                                transaction.on_commit(
                                    lambda v_id=voucher.id, link=reg_link: send_gift_voucher_email_task.delay(v_id, link)
                                )
                        
                        # Mark instant voucher lines as fully dispatched
                        prod.is_dispatched = True
                        prod.save(update_fields=['is_dispatched'])

                    elif getattr(variation.product, 'is_digital', False) and getattr(variation.product, 'digital_fulfillment_type', 'INSTANT') == 'INSTANT':
                        expiration_time = timezone.now() + timedelta(hours=168)
                        download_token = DigitalDownloadToken.objects.create(
                            user=order_locked.user,
                            order_product=prod,
                            expires_at=expiration_time
                        )
                        transaction.on_commit(
                            lambda token_id=download_token.id: send_e_product_email_task.delay(str(token_id))
                        )
                        
                        # Mark instant digital lines as fully dispatched
                        prod.is_dispatched = True
                        prod.save(update_fields=['is_dispatched'])

                # 🌟 STEP 4: ELEVATE SNAPSHOT LINE RECORDS BEFORE FINAL CALCULATION
                # This locks 'ordered=True' into the database, allowing your status engine to read them correctly!
                order_products.update(ordered=True, payment=payment)

                # 🌟 STEP 5: RUN THE ADVANCED STATUS TRACKING ENGINE FINAL PASS
                # Now that lines are 'ordered=True' and 'is_dispatched=True', your Chrono Engine 
                # will calculate your self-vouchers as 'Completed' or 'Processing' flawlessly!
                order_locked.update_fulfillment_status()
                order_locked.save(update_fields=['order_status'])

                # ── STEP 6: SURGICAL GHOST CART PURGE PASS ────────────────────────
                try:
                    historical_cart = Cart.objects.filter(cart_id__contains=f"_hold_{order_locked.order_number}").first()
                    if historical_cart:
                        CartItem.objects.filter(cart=historical_cart).delete()
                        historical_cart.delete()
                        print(f"🗑️ ADMIN PURGE COMPLETE: Deleted hold cart for Order {order_locked.order_number}")
                except Exception as cart_err:
                    print(f"⚠️ Non-breaking cart cleanup alert: {str(cart_err)}")

                # Invalidate the matching proforma record completely
                ProformaInvoice.objects.filter(proforma_order_number=order_locked.order_number).update(is_ordered=True)

                if order_locked.user:
                    CheckoutInfo.objects.filter(user=order_locked.user).delete()

                # 7. Queue your final payment confirmation email task post-commit
                transaction.on_commit(
                    lambda ord_num=order_locked.order_number: send_order_confirmation_email_task.delay(ord_num)
                )
                processed_count += 1

        except Exception as e:
            messages.error(request, f"處理訂單 {order.order_number} 時出錯 Error: {str(e)}")

    if processed_count > 0:
        messages.success(request, f"成功確認 {processed_count} 筆訂單的付款！ Successfully processed {processed_count} orders.")

    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["user", "payment", "order_number", "order_status", "recipient_first_name", "recipient_last_name", "email", "total_due", "is_ordered", "created_at"]
    search_fields = ["user__email", "user__username", "payment__payment_id", "order_number", "email", "order_status"]
    list_filter = ["is_ordered", "order_status", "created_at"]

    actions = [confirm_bank_payment_admin_action] 
    inlines = [OrderVoucherUsageInline]

    def get_actions(self, request):
        """
        🎯 SUPERUSER SECURITY GUARD:
        Ensures that only superusers can execute this specific payment clearance action.
        """
        actions = super().get_actions(request)
        
        # Adjust this flag check to perfectly match your custom Account model property (e.g. is_superadmin)
        if not request.user.is_superadmin:
            if 'confirm_bank_payment_admin_action' in actions:
                del actions['confirm_bank_payment_admin_action']
                
        return actions

    def save_model(self, request, obj, form, change):
        """
        🚀 ZERO-CALCULATION STAFF COMPLETION HOOK INTERCEPT
        Reads frozen snapshot database columns from the order instance to guarantee 
        absolute ledger data alignment across automated and manual paths.
        """
        if change and 'order_status' in form.changed_data:
            # Check if the staff member is moving an order into an absolute dead/complete state
            if obj.order_status in ['Refunded', 'Cancelled']:
                timestamp_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Append audit logs seamlessly without touching old delivery note arrays
                obj.delivery_note = f"{obj.delivery_note or ''}\n\n[Staff Settlement - {timestamp_str}]: Manual refund reconciliation completed. Cancellation mail sent from saved snapshot markers."
                
                if obj.payment:
                    obj.payment.status = 'Refunded'
                    obj.payment.save(update_fields=['status', 'updated_at'])

                # 🌟 Read from the snapshot data directly to enforce single source of truth rules
                # Safe conversion fallbacks provide additional runtime insurance blocks
                refund_type_str = str(obj.refund_type or 'CASH').lower()
                user_type_str = str(obj.user_classification or 'MEMBER').lower()
                net_payout_total = obj.total_due - (obj.total_cancellation_fee_applied or 0)

                # Execute the Celery completion task safely using the committed parameters
                # This guarantees that the final email contains the exact data processed on checkout
                connection = transaction.get_connection()
                if connection.in_atomic_block:
                    transaction.on_commit(lambda: send_cancellation_completion_email_task.delay(
                        order_id=obj.id,
                        refund_type=refund_type_str,
                        user_type=user_type_str,
                        voucher_id_str=obj.refund_voucher_id_str,
                        net_amount_str=f"{net_payout_total:.2f}"
                    ))
                else:
                    send_cancellation_completion_email_task.delay(
                        order_id=obj.id,
                        refund_type=refund_type_str,
                        user_type=user_type_str,
                        voucher_id_str=obj.refund_voucher_id_str,
                        net_amount_str=f"{net_payout_total:.2f}"
                    )

        # Execute parent class database save routing cleanly
        super().save_model(request, obj, form, change)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ["order", "user", "product_variation", "quantity", "is_dispatched", "created_at",]
    search_fields = ["order", "user", "created_at",]
