import requests
import logging
from celery import shared_task
from celery.signals import worker_ready
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from emails.utils import send_order_confirmation_email
from .utils import generate_order_confirmation_pdf
from orders.models import Order
from django.db import transaction
from carts.models import ProformaInvoice
from orders.models import Payment, OrderProduct
from store.models import ProductVariation
from django.core.mail import EmailMultiAlternatives
from datetime import timedelta
from accounts.models import CustomerVoucher
from django.utils import timezone


logger = logging.getLogger(__name__)

@shared_task
def update_exchange_rates():
    url = f"https://openexchangerates.org/api/latest.json?app_id={settings.OPENEXCHANGERATES_APP_ID}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Extract rates (e.g., HKD)
        rates = data.get('rates')
        print("rates: ", rates)
        # Store in Redis cache for 3660 seconds (1 hour + buffer)
        cache.set('exchange_rates', rates, timeout=3660)
        return "Rates updated successfully"
    except Exception as e:
        return f"Failed to update rates: {str(e)}"
    

@worker_ready.connect
def at_start(sender, **kwargs):
    # This runs as soon as the worker is ready to process tasks
    update_exchange_rates.delay()


@shared_task
def send_order_confirmation_email_task(order_id):
    try:
        order = Order.objects.get(order_number=order_id, is_ordered=True)
        
        # Guard clause: stop if email was already sent
        if getattr(order, 'email_sent', False):
            return f"Email already sent for Order {order_id}"

        # 1. Generate the PDF
        pdf_buffer = generate_order_confirmation_pdf(order_id)

        # 2. Call the email function
        send_order_confirmation_email(order_id, pdf_buffer)
        
        # 3. Mark as sent to prevent duplicates on future triggers
        order.email_sent = True
        order.save(update_fields=['email_sent'])
        
        return f"Email sent successfully to {order.email}"
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found or not paid."


@shared_task
def check_and_expire_hold(order_id):
    """
    Evaluates unpaid manual bank-transfer holds exactly 72 hours down the line.
    Reverts product inventory pools atomically and dispatches cancellation alerts if unpaid.
    """
    try:
        with transaction.atomic():
            # Apply strict row-level lock on the target Order
            order = Order.objects.select_for_update().get(id=order_id)
            
            # If manually moved forward by admin or cancelled prior, terminate immediately
            if order.order_status in ['Cancelled', 'Completed', 'Shipped', 'Processing']:
                return f"Verification skipped. Order {order.order_number} status is active at: {order.order_status}"

            # Check ground-truth table for a verified manual payment matching this transaction
            payment_confirmed = Payment.objects.filter(
                invoice__proforma_order_number=order.order_number,
                status='Completed'
            ).exists()

            if not payment_confirmed:
                # 1. Replenish database stock values back onto ProductVariation warehouse definitions
                order_items = OrderProduct.objects.filter(order=order)
                for item in order_items:
                    if item.product_variation:
                        variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                        variation.stock += item.quantity
                        variation.save()

                # 🎯 2. AUTOMATED VOUCHER BALANCE RECOVERY MANAGEMENT
                # Check if this specific order had a voucher deduction applied
                if order.voucher_applied > 0:
                    CustomerVoucher.objects.create(
                        value=order.voucher_applied,
                        balance=order.voucher_applied,
                        owner=order.user,
                        purchaser_email=order.email if order.email else "system-reversal@yourdomain.com",
                        registered_email=order.user.email if order.user else order.email,
                        is_claimed=True,
                        claimed_date=timezone.now(),
                        is_used=False
                    )

                # 3. Assign cancelled status markers across your profiles
                order.order_status = 'Cancelled'
                order.save(update_fields=['order_status'])
                
                # Rollback tracking visibility flags on the source Proforma invoice
                ProformaInvoice.objects.filter(proforma_order_number=order.order_number).update(is_ordered=False)
                
                # 3. Queue immediate account deletion/cancellation alerts down to background handlers
                send_bank_hold_cancelled_email_task.delay(order.id)
                return f"72-hour threshold reached. Reverted inventory units and cancelled order {order.order_number}."
            else:
                # Safe-state resolution transition mapping
                order.order_status = 'Processing'
                order.save(update_fields=['order_status'])
                return f"Valid payment cleared in flight window for order {order.order_number}. Retained."

    except Order.DoesNotExist:
        return f"Target hold confirmation identity vector {order_id} missing."


@shared_task
def send_bank_hold_confirmation_email_task(order_id):
    """
    Constructs and executes transmission lines conveying your bank account numbers 
    and payment guidelines along with a PDF copy of the transaction statement.
    """
    try:
        order = Order.objects.get(id=order_id, is_ordered=True)
        if getattr(order, 'email_sent', False):
            return f"Bank hold summary alert distribution sequence already logged for Order {order.order_number}"

        mail_subject = f"Hṛdayadīpa (हृदयदीप)｜心燈 - Bank Transfer Instructions｜銀行轉帳指引 [#{order.order_number}]"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [order.email]

        context = {
            "user": order.user,
            "order": order,
            # "expiry_date": order.created_at + timedelta(hours=72),
            "expiry_date": order.created_at + timedelta(minutes=5),
            # "expiry_date": order.created_at + timedelta(seconds=20),
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
        
        # Pull your application context settings directly to pass order strings onto standard templates
        pdf_buffer = generate_order_confirmation_pdf(order.order_number)
        mail.attach(f"轉帳明細｜Hold_Details_{order.order_number}.pdf", pdf_buffer.getvalue(), "application/pdf")
        
        mail.encoding = 'utf-8'
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

