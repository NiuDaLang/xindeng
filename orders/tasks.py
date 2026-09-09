from datetime import timedelta
import requests
import logging
from celery import shared_task
from celery.signals import worker_ready
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from emails.utils import send_order_confirmation_email, send_gift_voucher_email, send_secure_voucher_pin_email, send_cancellation_initiation_email, send_gift_voucher_revocation_email, send_cancellation_completion_email
from .utils import generate_order_confirmation_pdf, reverse_perk_usage_at_cancellation
from orders.models import Order, OrderInquiry
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
from django.core.exceptions import ObjectDoesNotExist


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


@shared_task(bind=True, name="tasks.send_gift_receiver_revocation_email_task")
def send_gift_receiver_revocation_email_task(self, order_id, recipient_email, revoked_tokens_log_str, **kwargs):
    """
    Asynchronous Celery Task Core for Voucher Revocations (Case g-iv).
    Queries the master order and triggers the email layout engine to notify
    3rd-party gift receivers that their credit voucher has been cancelled.
    """    
    
    logger.info(f"🚀 Initialising gift voucher cancellation email loop for Order ID: {order_id}")
    
    try:
        # Execute the main transactional email compilation sequence safely
        result = send_gift_voucher_revocation_email(order_id, recipient_email)
        return f"✅ Voucher revocation email successfully dispatched to: {recipient_email}"
        
    except ObjectDoesNotExist as odne:
        error_msg = f"❌ Revocation task aborted: Order matching ID {order_id} could not be found. Error: {str(odne)}"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"💥 Critical exception during voucher revocation email routing: {str(e)}"
        logger.error(error_msg)
        raise self.retry(exc=e, countdown=60, max_retries=3) # Safe retry engine on SMTP delivery drops


@shared_task(name="tasks.check_and_expire_hold")
def check_and_expire_hold(order_id):
    """
    🔒 HIGH-SECURITY CLEAN-UP ENGINE LOOP
    Evaluates an unpaid manual bank-transfer hold exactly at its expiration time.
    Restores inventory pools, purges orphaned cart items, and refunds voucher points on failure.
    """
    logger.info(f"⏳ Executing automated 72-hour bank transfer expiry check for Order ID: {order_id}")

    try:
        with transaction.atomic():
            # Apply pessimistic row locking to prevent racing payment conditions
            order = Order.objects.select_for_update().get(id=order_id)

            # If the order is already settled or managed, exit the clean-up engine early
            if order.is_ordered or order.order_status in ['Cancelled', 'Delivered', 'Partly_Dispatched', 'All_Dispatched', 'Processing']:
                return f"Verification skipped. Order #{order.order_number} is actively settled."

            # Query if a valid payment instance was verified inside your invoicing models
            payment_confirmed = Payment.objects.filter(
                invoice__proforma_order_number=order.order_number, 
                status='Completed'
            ).exists()

            if not payment_confirmed:
                logger.warning(f"🛑 Payment not confirmed for Order #{order.order_number}. Commencing rollback sequence.")

                # ── STEP A: RESTORE HELD INVENTORY POOLS ─────────────────────────
                order_items = OrderProduct.objects.filter(order=order)
                for item in order_items:
                    if item.product_variation:
                        # Row-lock the specific variation to prevent race conditions during restocking
                        variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                        
                        is_instant_eproduct = (
                            variation.product.is_digital and 
                            variation.product.digital_fulfillment_type == 'INSTANT' and 
                            not variation.product.is_voucher
                        )
                        
                        # Only restock items that consumed physical warehouse footprint slots
                        if not is_instant_eproduct:
                            variation.stock += item.quantity
                            variation.save(update_fields=['stock'])

                # ── STEP B: SURGICAL GHOST CART PURGE ─────────────────────────────
                try:
                    # Clear out the un-purchased hold cart from the checkout session
                    historical_cart = Cart.objects.filter(cart_id__contains=f"_hold_{order.order_number}").first()
                    if historical_cart:
                        CartItem.objects.filter(cart=historical_cart).delete()
                        historical_cart.delete()
                        logger.info(f"🗑 Automated Cleanup: Purged ghost hold items for Order #{order.order_number}")
                except Exception as cleanup_err:
                    logger.error(f"❌ Minor exception during ghost cart purge: {str(cleanup_err)}")

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
                    logger.info(f"✨ Restored store credit voucher fields for Order #{order.order_number}")

                # ── STEP D: CONNECTED PROMOTIONAL COUPON PERK REVERSAL ───────────
                try:
                    perk_rollback_message = reverse_perk_usage_at_cancellation(order)
                    logger.info(f"🎁 Promo Perk Engine: {perk_rollback_message}")
                except Exception as perk_err:
                    logger.error(f"❌ Failed to execute coupon perk rollback: {str(perk_err)}")

                # ── STEP E: TRANSACTION DATA STATE CLOSEOUT ──────────────────────
                order.order_status = 'Cancelled'
                order.save(update_fields=['order_status'])
                
                # Invalidate the checkout token inside the proforma invoice to block bypass loops
                ProformaInvoice.objects.filter(proforma_order_number=order.order_number).update(is_ordered=True)
                
                # Queue the background bank transfer cancellation notification email safely
                from .tasks import send_bank_hold_cancelled_email_task 
                transaction.on_commit(lambda: send_bank_hold_cancelled_email_task.delay(order.id))
                
                return f"Hold window closed. Cancelled expired Order Hold #{order.order_number} successfully."

            else:
                # =========================================================================
                # 🌟 核心修復：靈活適應人工核銷狀態機 (CONTEXT-AWARE STATUS PRESERVATION)
                # =========================================================================
                # The payment WAS confirmed! We must solidify record states safely.
                update_fields_list = []

                if not order.is_ordered:
                    order.is_ordered = True
                    update_fields_list.append('is_ordered')
                    
                    # Only assign the ordered_at timestamp if it was never stamped by a view or staff member
                    if not order.ordered_at:
                        order.ordered_at = timezone.now()
                        update_fields_list.append('ordered_at')

                # ⚠️ FIX: If staff already advanced the fulfillment status (e.g. Partly_Dispatched),
                # NEVER force it backward to 'Processing'. Preserve their active fulfillment tracking state!
                if order.order_status not in ['Processing', 'Partly_Dispatched', 'All_Dispatched', 'Delivered']:
                    order.order_status = 'Processing'
                    update_fields_list.append('order_status')

                if update_fields_list:
                    order.save(update_fields=update_fields_list)
                    logger.info(f"✅ In-Flight Save: Secured payment flags for Order #{order.order_number} on fields: {update_fields_list}")
                
                return f"Payment verification cleared in flight window for order {order.order_number}. Active tracking state preserved."

    except Order.DoesNotExist:
        return f"Identity tracking vector parameter {order_id} missing on system logs."
    except Exception as fatal_err:
        logger.error(f"❌ CRITICAL TASK BLINK EXCEPTION: {str(fatal_err)}")
        traceback.print_exc()
        raise fatal_err


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

        mail_subject = f"Hṛdayadīpa (हृदयदीप)｜心燈 - Bank Transfer Instructions｜銀行轉帳指引 [#{order.order_number}]"
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
        
        mail_subject = f"✨ Ready for Download: Your Digital Content｜電子商品下載連結 [#{order.order_number}]"
        
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


@shared_task(name="tasks.send_inquiry_notification_email_task")
def send_inquiry_notification_email_task(inquiry_id):
    """
    Asynchronously parses message contexts, shifts parameters, 
    and handles two-way dispatch runs between buyers and admins.
    """
    from .models import OrderInquiry
    from emails.utils import send_inquiry_alert_email, send_staff_reply_email
    try:
        inquiry = OrderInquiry.objects.get(id=inquiry_id)
        order = inquiry.order
        
        if inquiry.is_from_staff:
            # 📬 Dispatch notice down to the buyer's checkout email
            send_staff_reply_email(order.order_number, inquiry.message_content)
            return f"Staff response email successfully queued to user: {order.email}"
        else:
            # 🚨 Dispatch alert note to shop administrator channels
            send_inquiry_alert_email(order.order_number, inquiry.message_content)
            return f"Admin alert email successfully logged for Order {order.order_number}"
            
    except OrderInquiry.DoesNotExist:
        return f"Inquiry record tracker ID {inquiry_id} not found."


# @shared_task(name="tasks.send_cancellation_initiation_email_task")
# def send_cancellation_initiation_email_task(order_id, *args, **kwargs):
#     """Safely handles single or multiple variables without breaking execution chains."""
#     try:
#         order = Order.objects.get(id=order_id)
#         send_cancellation_initiation_email(order.order_number, **kwargs)
#         return f"🔒 Safety warning sent down to customer: {order.email}"
#     except Order.DoesNotExist:
#         return f"Order record tracker ID {order_id} missing on system."


# @shared_task(name="tasks.send_cancellation_completion_email_task")
# def send_cancellation_completion_email_task(order_id, *args, **kwargs):
#     """Processes final closure statements notifying clients that funds have been processed."""
#     try:
#         order = Order.objects.get(id=order_id)
#         send_cancellation_finalized_email(order.order_number, **kwargs)
#         return f"✉️ Final statement notice sent to user: {order.email}"
#     except Order.DoesNotExist:
#         return f"Order record tracker ID {order_id} missing on system."


@shared_task(bind=True, name="tasks.send_cancellation_initiation_email_task")
def send_cancellation_initiation_email_task(self, order_id, refund_type, user_type, is_online_gateway, currency_code, net_cash_payout_str, **kwargs):
    """
    Asynchronous Celery Task Core for Cash/Gateway Refund Initiation.
    Separates heavy mail construction layers from HTTP runtime execution threads.
    """
    
    logger.info(f"🚀 Initializing cash refund initiation task for Order ID: {order_id} ({user_type})")
    
    try:
        # Feed the captured payload metrics cleanly into the email compiler
        result = send_cancellation_initiation_email(
            order_id=order_id,
            user_type=user_type,
            is_online_gateway=is_online_gateway,
            currency_code=currency_code,
            net_cash_payout_str=net_cash_payout_str
        )
        return f"✅ Cancellation initiation alert successfully dispatched for Order ID: {order_id}"
        
    except ObjectDoesNotExist as odne:
        error_msg = f"❌ Task Aborted: Order registry node matching ID {order_id} missing on database records. Error: {str(odne)}"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"💥 Transient exception caught during initiation email assembly: {str(e)}"
        logger.error(error_msg)
        # Automated incremental retry buffer block to defend against gateway lag spikes
        raise self.retry(exc=e, countdown=60, max_retries=3)


@shared_task(bind=True, name="tasks.send_cancellation_completion_email_task")
def send_cancellation_completion_email_task(self, order_id, refund_type, user_type, voucher_id_str, net_amount_str, **kwargs):
    """
    Asynchronous Celery Task Core for Voucher Refund Finalization.
    Fires smoothly outside the main web worker thread to deliver the final balance certificates.
    """
    
    logger.info(f"🚀 Initializing cancellation completion email worker for Order ID: {order_id} ({user_type})")
    
    try:
        # Pass variables cleanly into our email rendering compilation loop
        result = send_cancellation_completion_email(order_id, user_type, voucher_id_str, net_amount_str)
        return f"✅ Cancellation completion certificate successfully sent for Order ID: {order_id}"
        
    except ObjectDoesNotExist as odne:
        error_msg = f"❌ Task Aborted: Order registry node matching ID {order_id} cannot be found. Error: {str(odne)}"
        logger.error(error_msg)
        return error_msg
        
    except Exception as e:
        error_msg = f"💥 Transient error during completion email generation loop: {str(e)}"
        logger.error(error_msg)
        # Safe incremental retry block to defend against gateway server lag spikes
        raise self.retry(exc=e, countdown=60, max_retries=3)



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

