from datetime import timedelta
import requests
import logging
from celery import shared_task
from celery.signals import worker_ready
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from emails.utils import send_order_confirmation_email, send_gift_voucher_email, send_secure_voucher_pin_email
from .utils import generate_order_confirmation_pdf
from orders.models import Order
from django.db import transaction
from carts.models import ProformaInvoice
from orders.models import Payment, OrderProduct
from store.models import ProductVariation
from django.core.mail import EmailMultiAlternatives
from accounts.models import CustomerVoucher
from django.utils import timezone
from .models import OrderVoucherUsage
from store.models import DigitalDownloadToken
from carts.models import CartItem
from email.mime.image import MIMEImage
import os
import traceback
from carts.models import Cart



logger = logging.getLogger(__name__)

@shared_task
def update_exchange_rates():
    url = f"https://openexchangerates.org/api/latest.json?app_id={settings.OPENEXCHANGERATES_APP_ID}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=30) # 30s is standard for fast APIs
        response.raise_for_status()
        data = response.json()
        
        rates = data.get('rates')
        if not rates:
            raise ValueError("API response data was missing the 'rates' payload container mapping.")
        
        # 🌟 FIX: Persist data for 3 full days (259200 seconds) instead of 24 hours.
        # This gives your site a 3-day survival buffer if the external API faces downtime.
        cache.set('exchange_rates', rates, timeout=3600 * 24 * 3)
        return "Rates updated successfully"
    
    except Exception as e:
        return f"Failed to update rates: {str(e)}"
    

@worker_ready.connect
def at_start(sender, **kwargs):
    # This runs as soon as the worker is ready to process tasks
    update_exchange_rates.delay()


@shared_task(name="tasks.send_order_confirmation_email_task")
def send_order_confirmation_email_task(order_id):
    """Asynchronously generates tax PDFs and dispatches client receipt notices."""
    try:
        order = Order.objects.get(order_number=order_id, is_ordered=True)
        
        if getattr(order, 'payment_email_sent', False):
            return f"Payment email already processed for Order {order.order_number}"

        # Build custom ReportLab binary layout buffer
        pdf_buffer = generate_order_confirmation_pdf(order_id)

        # Dispatch the payload
        send_order_confirmation_email(order_id, pdf_buffer)
        
        order.payment_email_sent = True
        order.save(update_fields=['payment_email_sent'])
        
        return f"Email sent successfully to {order.email}"
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found or unpaid state."
    

@shared_task(name="tasks.send_gift_voucher_email_task")
def send_gift_voucher_email_task(v_id, link):
    """Dispatches gift card claim links directly to the recipient's inbox."""
    try:
        voucher = CustomerVoucher.objects.get(id=v_id)
        send_gift_voucher_email(v_id, link)
        return f"Gift voucher tracking notification completed for ID: {v_id}"
        
    except CustomerVoucher.DoesNotExist:
        return f"Voucher target tracking row ID {v_id} missing. Task aborted."
    

@shared_task(name="tasks.send_secure_voucher_pin_email_task")
def send_secure_voucher_pin_email_task(voucher_id, pin_code):
    print("voucher_id, pin_code: ", voucher_id, pin_code)
    """Asynchronously executes the secure PIN transmission via background worker threads."""
    try:
        send_secure_voucher_pin_email(voucher_id, pin_code)
        return f"Secure PIN delivery completed for Voucher ID {voucher_id}."
    except Exception as e:
        return f"Failed to execute secure PIN transmission task for ID {voucher_id}. Error: {str(e)}"


@shared_task(name="tasks.check_and_expire_hold")
def check_and_expire_hold(order_id):
    """
    🔒 HIGH-SECURITY CLEAN-UP ENGINE LOOP
    Evaluates an unpaid manual bank-transfer hold exactly at its expiration time.
    Restores inventory pools, purges orphaned cart items, and refunds voucher points on failure.
    """
    print("check_and_expire_hold()!!!!!")
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id)
            print(f"order: {order}")
            if order.is_ordered or order.order_status in ['Cancelled', 'Completed', 'Shipped', 'Processing']:
                return f"Verification skipped. Order {order.order_number} is actively settled."

            payment_confirmed = Payment.objects.filter(invoice__proforma_order_number=order.order_number, status='Completed').exists()
            print("payment_confirmed: ", payment_confirmed)
            if not payment_confirmed:
                print("payment not confirmed")
                # ── STEP A: RESTORE HELDF INVENTORY POOLS ─────────────────────────
                order_items = OrderProduct.objects.filter(order=order)
                for item in order_items:
                    if item.product_variation:
                        variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                        variation.stock += item.quantity
                        variation.save(update_fields=['stock'])

                # ── STEP B: SURGICAL GHOST CART PURGE ─────────────────────────────
                try:
                    # 1. Fetch your baseline proforma log record row matching this order string text
                    proforma = ProformaInvoice.objects.filter(proforma_order_number=order.order_number).first()
                    print('proforma lookup result: ', proforma)
                    
                    # 🌟 THE FINAL FIX: Drop the crashing 'target_hold_cart_id' line entirely!
                    # We execute the native string lookup directly against our Cart database table index:
                    historical_cart = Cart.objects.filter(cart_id__contains=f"_hold_{order.order_number}").first()
                    print("Historical Cart lookup by string match token: ", historical_cart)

                    if historical_cart:
                        print("🌟 Identity validation pass: Commencing historical cart purge sequence.")
                        
                        # Clear out all individual CartItem lines bound to this historical hold basket
                        CartItem.objects.filter(cart=historical_cart).delete()
                        print(f"🗑️ AUTOMATED CLEANUP: Wiped ghost items from expired Cart ID {historical_cart.id}")
                        
                        # Safely delete the historical Cart row container itself to optimize database footprint
                        historical_cart.delete()
                        print("🎯 Target Cart row deleted from database cleanly.")
                    else:
                        print("⚠️ No matching hold cart row was found for this order signature.")

                except Exception as cleanup_err:
                    # This catches any syntax or reference faults inside the block
                    print(f"❌ CRITICAL TASK BLINK EXCEPTION: {str(cleanup_err)}")
                    traceback.print_exc() # Prints the exact line-by-line python crash log to your console!

                # ── STEP C: PINPOINT VOUCHER BALANCE REVERSALS ───────────────────
                if order.voucher_applied > 0:
                    usages = OrderVoucherUsage.objects.filter(order=order)
                    for usage in usages:
                        voucher = CustomerVoucher.objects.select_for_update().get(id=usage.voucher.id)
                        voucher.balance += usage.amount_deducted
                        if voucher.is_used:
                            voucher.is_used = False
                            voucher.used_date = None
                        voucher.save(update_fields=['balance', 'is_used', 'used_date'])

                # ── STEP D: TRANSACTION DATA STATE CLOSEOUT ──────────────────────
                order.order_status = 'Cancelled'
                order.save(update_fields=['order_status'])

                # 🌟 THE SECURITY LOCK: Keep is_ordered=True locked down inside your proforma database row!
                # This explicitly invalidates this token, blocking checkout bypass loops from loading.
                ProformaInvoice.objects.filter(proforma_order_number=order.order_number).update(is_ordered=True)
            
                # Queue your background cancellation notification mailer safely outside the core lock loop
                transaction.on_commit(lambda: send_bank_hold_cancelled_email_task.delay(order.id))
                return f"Hold window closed. Cancelled expired Order Hold #{order.order_number} successfully."
            
            else:
                # Late-clearing payment found inside the validation window: Settle order cleanly
                order.is_ordered = True
                order.ordered_at = timezone.now()
                order.order_status = 'Processing'
                order.save(update_fields=['is_ordered', 'ordered_at', 'order_status'])
                OrderProduct.objects.filter(order=order).update
                return f"Payment verification cleared in flight window for order {order.order_number}."

    except Order.DoesNotExist:
        return f"Identity tracking vector parameter {order_id} missing."


@shared_task(name="tasks.send_bank_hold_confirmation_email_task")
def send_bank_hold_confirmation_email_task(order_id):
    """
    Constructs and executes transmission lines conveying your bank account numbers 
    and payment guidelines along with a PDF copy of the transaction statement.
    """
    try:
        order = Order.objects.get(id=order_id)
        if getattr(order, 'email_sent', False):
            return f"Bank hold summary alert distribution sequence already logged for Order {order.order_number}"

        mail_subject = f"Hṛdayadīpa (हृदयदीप) ｜ 心燈 - Bank Transfer Instructions ｜ 銀行轉帳指引 [#{order.order_number}]"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.email.strip()]

        # 🌟 THE SYNCED CONTEXT DICTIONARY MATRIX
        # Captures identical expiration time constraints and matches the dynamic year property
        context = {
            "user": order.user,
            "order": order,
            "expiry_date": order.created_at + timedelta(minutes=60), # Standardized match for your 15-minute hold validation
            "year": timezone.now().year,
        }

        html_message = render_to_string("emails/bank_hold_confirmation_email.html", context)
        plain_message = render_to_string("emails/bank_hold_confirmation_email.txt", context)

        mail = EmailMultiAlternatives(
            subject=mail_subject,
            body=plain_message,
            from_email=from_email,
            to=to_email,
            bcc=[from_email],
        )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'

        # ── ATTACHMENT A: GENERATED WATERMARK STATEMENT PDF OVERLAY ──────
        pdf_buffer = generate_order_confirmation_pdf(order.order_number)
        if pdf_buffer:
            mail.attach(f"轉帳明細｜Hold_Details_{order.order_number}.pdf", pdf_buffer.getvalue(), "application/pdf")

        # Stream the full envelope payload out to your mail configuration server pipelines
        mail.send()

        order.email_sent = True
        order.save(update_fields=['email_sent'])
        return f"Remittance roadmap notification dispatched successfully to {order.email}"

    except Order.DoesNotExist:
        return f"Order database snapshot with target key ID {order_id} could not be uncovered."


@shared_task
def send_bank_hold_cancelled_email_task(order_id):
    """Dispatches automatic system notifications warning users that their 72-hour checkout lock window has run out."""
    try:
        order = Order.objects.get(id=order_id)
        mail_subject = f"Hṛdayadīpa (हृदयदीप)｜心燈 - Order Hold Expired｜庫存保留已逾期取消 [#{order.order_number}]"
        
        context = {"user": order.user, "order": order}
        html_message = render_to_string("emails/bank_hold_cancelled_email.html", context)
        plain_message = render_to_string("emails/bank_hold_cancelled_email.txt", context)

        mail = EmailMultiAlternatives(
            subject=mail_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email],
            bcc=[settings.DEFAULT_FROM_EMAIL]
        )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'
        mail.send()
        return f"Expiration warning message sent onto user {order.email}."
    except Order.DoesNotExist:
        return f"Order contextual layout instance {order_id} missing."


@shared_task
def send_e_product_email_task(token_id):
    """Asynchronously executes the time-locked download token transmission via background workers."""
    try:
        token = DigitalDownloadToken.objects.select_related('user', 'order_product__order', 'order_product__product_variation__product').get(id=token_id)
        order = token.order_product.order
        product = token.order_product.product_variation.product
        
        mail_subject = f"✨ Ready for Download: Your Digital Content ｜ 電子商品下載連結 [#{order.order_number}]"
        
        # Base site URL routing pass (Adjust variable based on your local vs live deployment keys)
        site_domain = getattr(settings, "SITE_DOMAIN", "http://localhost:8000")
        download_url = f"{site_domain}/store/digital/download/{str(token.id)}/"
        
        context = {
            "token": token,
            "order": order,
            "product": product,
            "download_url": download_url,
            "user": token.user
        }
        
        # Render clean email template variations
        html_message = render_to_string("emails/eproduct_download_notification.html", context)
        plain_message = render_to_string("emails/eproduct_download_notification.txt", context)
        
        mail = EmailMultiAlternatives(
            subject=mail_subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.email.strip()],
            bcc=[settings.DEFAULT_FROM_EMAIL]
        )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'
        mail.send()
        
        return f"Digital item delivery completed securely for Token ID {token_id}."
    except Exception as e:
        return f"Failed to execute digital link dispatch for Token ID {token_id}. Error: {str(e)}"



# For scheduled tasks to work, you must run two separate processes simultaneously: 
# 1. The Worker: Executes the tasks.
# [BASH]
# celery -A your_project_name worker --loglevel=info


# 2. The Beat Service: The "scheduler" that tells the worker when it's time to run the task.
# [BASH]
# celery -A your_project_name beat --loglevel=info

# * For development only, you can run both in one command: celery -A xindeng worker --beat --loglevel=info


# Production (Separate Processes)
# In a production environment (on a real server), you should run them as separate processes. You don't necessarily "open windows," but you run them as background services (daemons) using tools like systemd, Supervisor, or Docker. 
# Why separate them in production?
# Scaling: You can have 10 worker servers but you must only have one beat instance. If you run -B on all 10 workers, your "hourly" task will trigger 10 times.
# Stability: If a heavy task crashes a worker, a separate beat process will continue to schedule future tasks reliably. 
# Production Service Pattern:
# Service 1 (Worker): celery -A proj worker -l info
# Service 2 (Beat): celery -A proj beat -l info

# 6/7:
# confirm_bank_payment_admin_action()
# send_bank_hold_confirmation_email_task()
# check_and_expire_hold()
# send_gift_voucher_email_task()
# send_order_confirmation_email_task()
# send_gift_voucher_email()
# send_order_confirmation_email()
# execute_atomic_voucher_deduction()
# generate_order_confirmation_pdf()
# paypal_order_success()
# order_complete()
# place_order()
# clear_expired_bank_holds --- stil need? 



# [Buyer Completes Payment]
#          │
#          ▼
# [Execute Order Finalization (Atomic Transaction)]
#          │
#          ├─► Generate Order & OrderProducts
#          └─► Loop item.quantity: Create unclaimed CustomerVoucher records
#                  │
#                  ▼
# [Dispatch Celery Notification Pipeline]
#          │
#          ├─► Send PDF Tax Invoice to Buyer (A-i)
#          └─► Send Notification + Unique Claim Link to Recipient (A-ii)
#                  │
#                  ▼
# [Recipient Clicks Link] ──► Not Logged In? ──► Redirect to Custom Registration Page
#                  │
#                  ▼ (Authenticated)
# [Execute voucher.claim(user.email)] ──► Lock owner field ──► Done!

