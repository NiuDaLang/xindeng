from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from orders.models import Order, Payment, OrderProduct
from carts.models import ProformaInvoice
from accounts.data import CURRENCY_SYMBOL, INTEGER_CURRENCIES
from weasyprint import HTML
import weasyprint
# find url for weasyprint
from django.contrib.staticfiles import finders
import os
from urllib.parse import unquote
import mimetypes
from pathlib import Path
import logging
from accounts.models import CustomerVoucher


logger = logging.getLogger(__name__)


def send_account_verification(mail_subject, user, to_email, current_site, uid, token):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL

        context = {
            "user": user,
            "domain": current_site,
            "uid": uid,
            "token": token
        }

        html_message = render_to_string("emails/registration_activation_email.html", context)
        plain_message = render_to_string("emails/registration_activation_email.txt", context)

        mail = EmailMultiAlternatives(
                subject = mail_subject, 
                body = plain_message, 
                from_email = from_email, 
                to = to_email,
                bcc = [from_email],
                )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'
        mail.send()

    except Exception as e:
        raise e
    

def send_password_reset(mail_subject, user, to_email, current_site, uid, token):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL

        context = {
            "user": user,
            "domain": current_site,
            "uid": uid,
            "token": token
        }

        html_message = render_to_string("emails/reset_password_email.html", context)
        plain_message = render_to_string("emails/reset_password_email.txt", context)

        mail = EmailMultiAlternatives(
                subject = mail_subject,
                body = plain_message,
                from_email = from_email,
                to = to_email,
                bcc = [from_email],
                )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'
        mail.send()

    except Exception as e:
        raise e
    

def send_password_reset_completion(mail_subject, user, to_email, current_site):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL

        context = {
            "user": user,
            "domain": current_site,
        }

        html_message = render_to_string("emails/reset_password_completion_email.html", context)
        plain_message = render_to_string("emails/reset_password_completion_email.txt", context)

        mail = EmailMultiAlternatives(
                subject = mail_subject,
                body = plain_message,
                from_email = from_email,
                to = to_email,
                bcc = [from_email],
                )
        mail.attach_alternative(html_message, "text/html")
        mail.encoding = 'utf-8'
        mail.send()

    except Exception as e:
        raise e


def django_url_fetcher(url, timeout=10, ssl_context=None):
    # 1. Decode %20 (spaces) and Chinese characters
    # This turns 'projects%20django' into 'projects django'
    decoded_url = unquote(url)
    
    # 2. Convert to a Path object and remove the 'file:' protocol if present
    if decoded_url.startswith('file://'):
        # On macOS/Linux, file:///path/to/file becomes /path/to/file
        clean_path = decoded_url.replace('file://', '')
    else:
        clean_path = decoded_url

    # 3. Resolve Static Files
    if 'static/' in clean_path:
        relative_path = clean_path.split('static/')[-1]
        # Use / operator with Path objects for space-safe joining
        full_path = Path(settings.STATIC_ROOT) / relative_path
        
        # This will show up in your Celery logs
        logger.error(f"PDF FETCH ATTEMPT (static): {full_path}") 
        
        if full_path.exists():
            return {'file_obj': open(full_path, 'rb'), 'mime_type': 'image/png'}
        

        # if full_path.exists():
        #     with open(full_path, 'rb') as f:
        #         return {
        #             'string': f.read(),
        #             'mime_type': 'image/png' # or use mimetypes.guess_type(str(full_path))[0]
        #         }        
        
        # Fallback to App static directories
        found_path = finders.find(relative_path)
        if found_path:
            return {'file_obj': open(found_path, 'rb'), 'mime_type': 'image/png'}

    # 4. Resolve Media Files
    if 'media/' in clean_path:
        relative_path = clean_path.split('media/')[-1]
        full_path = Path(settings.MEDIA_ROOT) / relative_path

        # This will show up in your Celery logs
        logger.error(f"PDF FETCH ATTEMPT (media): {full_path}") 
        
        if full_path.exists():
            return {'file_obj': open(full_path, 'rb'), 'mime_type': 'image/png'}
        
        # if full_path.exists():
        #     with open(full_path, 'rb') as f:
        #         return {
        #             'string': f.read(),
        #             'mime_type': 'image/png' # or use mimetypes.guess_type(str(full_path))[0]
        #         }

    return weasyprint.default_url_fetcher(url, timeout, ssl_context)


def send_order_confirmation_email(order_id, pdf_buffer):
    """Generates multi-part confirmation summaries attaching transactional receipts."""
    order = Order.objects.get(order_number=order_id, is_ordered=True)
    mail_subject = f"Hṛdayadīpa (हृदयदीप)｜心燈 - Order Confirmation｜訂單確認 [#{order.order_number}]"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    context = {
        "user": order.user,
        "order": order,        
    }

    html_message = render_to_string("emails/order_confirmation_email.html", context)
    plain_message = render_to_string("emails/order_confirmation_email.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc = [from_email],
    )
    mail.attach_alternative(html_message, "text/html")

    # Extract structural binaries directly via read methods if wrapper requires string arrays
    pdf_data = pdf_buffer.getvalue() if hasattr(pdf_buffer, 'getvalue') else pdf_buffer
    mail.attach(f"訂單｜Order_{order.order_number}.pdf", pdf_data, "application/pdf")
    mail.encoding = 'utf-8'
    mail.send()


def send_gift_voucher_email(v_id, link):
    """
    🌟 FIXED: Cleared initialization parameter clash bugs.
    Routes unique claim tracking configurations safely to the gift recipient's inbox.
    """
    voucher = CustomerVoucher.objects.get(id=v_id)

    # 🎯 FIX: Traverse database structures to locate the original recipient email parameter
    # dynamically or use the purchaser email address as a secure fallback
    associated_order = Order.objects.filter(email=voucher.purchaser_email, recipient_email__isnull=False).order_by('-created_at').first()
    
    if associated_order and associated_order.recipient_email:
        target_recipient = associated_order.recipient_email.strip()
        gift_message_text = associated_order.gift_message
    else:
        target_recipient = voucher.purchaser_email.strip()
        gift_message_text = ""
     
    mail_subject = f"🎁 您收到了一份來自 {voucher.purchaser_email} 的禮品券！ | A Gift Voucher For You!"
   
    context = {
        "voucher": voucher,
        "registration_link": link,
        "gift_message": gift_message_text,
    }

    html_message = render_to_string("emails/gift_voucher_delivery.html", context)
    plain_message = render_to_string("emails/gift_voucher_delivery.txt", context)
    
    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[target_recipient],
        bcc=[settings.DEFAULT_FROM_EMAIL]
    )

    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()


def send_secure_voucher_pin_email(v_id, pin_code):
    """
    Constructs and dispatches the single-use security 6-digit PIN code
    directly to the voucher's registered recipient email address.
    """
    voucher = CustomerVoucher.objects.get(id=v_id)
    
    associated_order = Order.objects.filter(
        email=voucher.purchaser_email, 
        recipient_email=voucher.registered_email
    ).order_by('-created_at').first()
    
    target_recipient = voucher.registered_email if voucher.registered_email else voucher.purchaser_email
    mail_subject = f"🔒 Secure PIN: Claim Your Gift Voucher ｜ 安全驗證碼：領取您的禮品券 [#{str(voucher.id)[:8].upper()}]"

    # 🌟 THE SNAP FIX: Append the voucher instance directly into the dictionary context maps!
    # This satisfies line 7's voucher.value demand, allowing your template engine to print the 6-digit PIN code perfectly.
    print("pin: ", pin_code)
    print("pin_code: ", pin_code)
    print("voucher value: ", voucher.value)
    
    context_data = {
        "pin": pin_code,
        "pin_code": pin_code,  # Backup key mapping for safety
        "voucher": voucher
    }

    # Render your template files using the complete context mapping framework
    html_message = render_to_string("emails/claim_pin_notification.html", context_data)
    plain_message = render_to_string("emails/claim_pin_notification.txt", context_data)
    
    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[target_recipient.strip()],
        bcc=[settings.DEFAULT_FROM_EMAIL]
    )

    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()


# __str__ returned non-string (type ProductVariation)
# Request Method:	POST
# Request URL:	http://localhost:8000/admin/orders/order/
# Django Version:	6.0.1
# Exception Type:	TypeError
# Exception Value:	
# __str__ returned non-string (type ProductVariation)
# Exception Location:	/Users/mycomputer/Documents/path/project/env/lib/python3.13/site-packages/django/contrib/admin/utils.py, line 148, in format_callback
# Raised during:	django.contrib.admin.options.changelist_view
# Python Executable:	/Users/mycomputer/Documents/path/project/env/bin/python
# Python Version:	3.13.5
# Python Path:	
# ['/Users/mycomputer/Documents/path/project',
#  '/Users/mycomputer/Documents/path/project',
#  '/opt/anaconda3/lib/python313.zip',
#  '/opt/anaconda3/lib/python3.13',
#  '/opt/anaconda3/lib/python3.13/lib-dynload',
#  '/Users/mycomputer/Documents/path/project/env/lib/python3.13/site-packages']