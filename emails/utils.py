# emails.utils.py

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from orders.models import Order, Payment, OrderProduct
from carts.models import ProformaInvoice
from accounts.data import CURRENCY_SYMBOL, INTEGER_CURRENCIES
from pathlib import Path
import logging
from accounts.models import CustomerVoucher
from django.contrib.sites.models import Site # 🌟 IMPORT THE DATABASE SITE CONFIG
from blog.models import Post
from django.utils import timezone


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
     
    mail_subject = f"🎁 A Gift Voucher For You!｜您收到了一份來自 {voucher.purchaser_email} 的禮品券！"
   
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
    mail_subject = f"🔒 Secure PIN: Claim Your Gift Voucher｜安全驗證碼：領取您的禮品券 [#{str(voucher.id)[:8].upper()}]"

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


def send_gift_voucher_revocation_email(order_id, recipient_email):
    """
    Compiles and dispatches professional bilingual cancellation alerts
    to 3rd-party gift receivers when a purchased gift card is deactivated.
    """
    # 1. Fetch matching transaction variables securely from database
    order = Order.objects.get(id=order_id)
    
    # 2. Gather deactivated vouchers linked to this recipient for tracking
    # Grabs short 8-character token signatures to display safely without exposing full strings
    revoked_vouchers = CustomerVoucher.objects.filter(
        purchaser_email=order.email, 
        registered_email=recipient_email.strip().lower()
    )
    
    short_ids = [str(v.id)[:8].upper() for v in revoked_vouchers]
    short_ids_str = ", ".join(short_ids) if short_ids else f"VAR-{order.order_number[:8].upper()}"

    # 3. Configure administrative email tracking headers
    mail_subject = f"🛑 Gift Card Notice｜您的電子禮品卡狀態變更與註銷通知 [#{order.order_number}]"
    
    current_site = Site.objects.get_current()
    site_domain = f"http://{current_site.domain}"
    
    # 4. Bind runtime template variables
    context = {
        "order": order,
        "site_domain": site_domain,
        "recipient_email": recipient_email.strip(),
        "short_ids_str": short_ids_str,
    }
    
    # 5. Render separate multi-part template files for strict client reliability
    html_message = render_to_string("emails/gift_voucher_revocation.html", context)
    plain_message = render_to_string("emails/gift_voucher_revocation.txt", context)
    
    # 6. Build and dispatch the multi-part email
    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email.strip()]
    )
    
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()
    
    return True


def send_inquiry_alert_email(order_number, message_content):
    """Alerts shop admins immediately when a customer logs a fresh query."""
    order = Order.objects.get(order_number=order_number)
    mail_subject = f"🚨 New Customer Inquiry｜新留言提醒 [#{order.order_number}]"
    
    from_email = settings.DEFAULT_FROM_EMAIL
    # As requested, matching your admin fallback logic loops
    to_email = ['gogocfa@yahoo.co.jp'] 

    context = {
        "order": order,
        "message_content": message_content,
    }

    html_message = render_to_string("emails/admin_inquiry_alert_email.html", context)
    plain_message = render_to_string("emails/admin_inquiry_alert_email.txt", context)

    mail = EmailMultiAlternatives(subject=mail_subject, body=plain_message, from_email=from_email, to=to_email)
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()


def send_staff_reply_email(order_number, message_content):
    """Streams formal message blocks down to the target customer's inbox tray."""
    order = Order.objects.get(order_number=order_number)
    mail_subject = f"✉️ Hṛdayadīpa｜心燈 - Customer Care Reply｜專員客服回覆 [#{order.order_number}]"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [order.email]

    # 🚀 DYNAMIC SITE LOOKUP (Safe for background Celery worker threads)
    current_site = Site.objects.get_current() 
    # This evaluates to '127.0.0.1:8000' or 'localhost:8000' in development, 
    # and automatically flips to 'xindeng.art' once configured in your production DB.
    site_domain = f"http://{current_site.domain}"

    context = {
        "user": order.user,
        "order": order,
        "message_content": message_content,
        "site_domain": site_domain, # 🌟 PASS THE ASYNC SAFE PROTOCOL PATH HERE
    }

    html_message = render_to_string("emails/staff_reply_email.html", context)
    plain_message = render_to_string("emails/staff_reply_email.txt", context)

    mail = EmailMultiAlternatives(subject=mail_subject, body=plain_message, from_email=from_email, to=to_email, bcc=[from_email])
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()


def send_cancellation_initiation_email(order_id, user_type, is_online_gateway, currency_code, net_cash_payout_str):
    """
    Compiles and dispatches professional bilingual cash refund intake requests.
    Adapts text layouts based on user membership and original payment gateway routes.
    """
    order = Order.objects.get(id=order_id)
    mail_subject = f"⏳ Refund Processing｜您的訂單取消與退款申請已受理 [#{order.order_number}]"
    
    current_site = Site.objects.get_current()
    site_domain = f"http://{current_site.domain}"
    
    # Calculate original voucher applied amount part to display in context safely
    original_voucher_spent = order.voucher_applied

    # Assemble contextual template parameter dictionaries
    context = {
        "order": order,
        "user_type": user_type,                  # 'member' or 'guest'
        "is_online_gateway": is_online_gateway,  # True (PayPal/Stripe) or False (Bank Transfer)
        "currency_code": currency_code.upper(),
        "net_cash_payout_str": net_cash_payout_str,
        "original_voucher_spent": original_voucher_spent,
        "site_domain": site_domain
    }
    
    html_message = render_to_string("emails/cancellation_initiation_email.html", context)
    plain_message = render_to_string("emails/cancellation_initiation_email.txt", context)
    
    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email.strip()]
    )
    
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()
    
    return True


def send_cancellation_completion_email(order_id, user_type, voucher_id_str, net_amount_str):
    """
    Compiles and dispatches professional bilingual refund confirmation statements.
    Appends automated ledger vouchers or secure registration activation funnels dynamically.
    """
    order = Order.objects.get(id=order_id)
    mail_subject = f"✨ Refund Completed｜您的訂單取消與購物金簽發已完成 [#{order.order_number}]"
    
    current_site = Site.objects.get_current()
    site_domain = f"http://{current_site.domain}"
    
    claim_link = ""
    short_voucher_id = ""
    
    # 🌟 Secure extraction of token metadata vectors if a voucher database row exists
    if voucher_id_str:
        try:
            voucher = CustomerVoucher.objects.get(id=voucher_id_str)
            short_voucher_id = str(voucher.id)[:8].upper()
            # Programmatically construct an absolute endpoint URL path for guests
            claim_link = f"{site_domain}/vouchers/claim/{str(voucher.id)}/"
        except CustomerVoucher.DoesNotExist:
            short_voucher_id = "VCH-ERR"

    # Assemble template mapping dictionary parameters
    context = {
        "order": order,
        "user_type": user_type,  # 'member' or 'guest'
        "net_amount_str": net_amount_str,
        "short_voucher_id": short_voucher_id,
        "claim_link": claim_link,
        "site_domain": site_domain
    }
    
    html_message = render_to_string("emails/cancellation_completion_email.html", context)
    plain_message = render_to_string("emails/cancellation_completion_email.txt", context)
    
    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email.strip()]
    )
    
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = 'utf-8'
    mail.send()
    
    return True


# ARTISAN related
def send_artisan_new_order_email(order_id, creator_id):
    """
    Dispatches a 'new order to fulfill' notification to a single artisan.
    Called by the Celery task `send_artisan_new_order_email_task` for each
    artisan with pending (un-dispatched) lines in a given order.
    """
    from orders.models import Order, OrderProduct
    from creators.models import CreatorProfile

    order = Order.objects.get(id=order_id)
    creator = CreatorProfile.objects.get(id=creator_id)

    # Only pull lines this artisan is responsible for and that still need action
    pending_lines = OrderProduct.objects.filter(
        order=order,
        fulfilled_by=creator,
        is_dispatched=False,
    ).select_related('product', 'product_variation')

    if not pending_lines.exists():
        # Nothing to notify about — silently exit
        return False

    mail_subject = (
        f"🧑‍🎨 New Order to Fulfill｜待發貨訂單 "
        f"[#{order.order_number}]"
    )

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [creator.user.email]

    # Async-safe site domain lookup (matches your existing pattern)
    current_site = Site.objects.get_current()
    site_domain = f"http://{current_site.domain}"
    dashboard_url = f"{site_domain}/artisans/dashboard/orders/"

    context = {
        "order": order,
        "creator": creator,
        "pending_lines": pending_lines,
        "line_count": pending_lines.count(),
        "dashboard_url": dashboard_url,
        "site_domain": site_domain,
    }

    html_message = render_to_string("emails/artisan_new_order_email.html", context)
    plain_message = render_to_string("emails/artisan_new_order_email.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()

    return True


def send_blog_submission_notification(post_id):
    """Notify the platform admin that a new blog post was submitted for review."""
    post = Post.objects.get(id=post_id)

    author_label = (
        post.creator.display_name if post.creator
        else post.author.username
    )

    mail_subject = f"📝 [Blog Review] New submission｜新筆記待審 — {post.title}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.ADMIN_EMAIL]

    context = {
        "post": post,
        "author_label": author_label,
        "review_url": f"{settings.SITE_DOMAIN}/accounts/dashboard/blog_review/",
        "year": timezone.now().year,
    }
    html_message = render_to_string("emails/blog_submission_notification.html", context)
    plain_message = render_to_string("emails/blog_submission_notification.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()


def send_blog_review_result_notification(post_id, approved, note=""):
    """Notify the artisan that their blog post was approved or rejected."""
    post = Post.objects.get(id=post_id)

    # Editorial posts (creator is None) should never reach the artisan
    if not post.creator:
        return

    author_label = post.creator.display_name

    if approved:
        mail_subject = f"✅ [Blog] Approved｜筆記已通過 — {post.title}"
    else:
        mail_subject = f"📝 [Blog] Revision Needed｜筆記需要修改 — {post.title}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [post.creator.user.email]

    context = {
        "post": post,
        "author_label": author_label,
        "approved": approved,
        "note": note,
        "public_url": f"{settings.SITE_DOMAIN}{post.get_url()}" if approved else None,
        "dashboard_url": f"{settings.SITE_DOMAIN}/creators/dashboard/blog/",
        "year": timezone.now().year,
    }
    html_message = render_to_string("emails/blog_review_result.html", context)
    plain_message = render_to_string("emails/blog_review_result.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()    


def send_product_submission_notification(product_id):
    """Notify the platform admin that a new product was submitted for review."""
    from store.models import Product

    product = Product.objects.get(id=product_id)

    artisan_label = (
        product.creator.display_name if product.creator
        else "Platform｜平台"
    )

    mail_subject = f"🛍️ [Product Review] New submission｜新作品待審 — {product.product_name}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.ADMIN_EMAIL]

    context = {
        "product": product,
        "artisan_label": artisan_label,
        "review_url": f"{settings.SITE_DOMAIN}/accounts/dashboard/product_review/",
        "year": timezone.now().year,
    }
    html_message = render_to_string("emails/product_submission_notification.html", context)
    plain_message = render_to_string("emails/product_submission_notification.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()


def send_product_review_result_notification(product_id, approved, note=""):
    """Notify the artisan that their product was approved or rejected."""
    from store.models import Product

    product = Product.objects.get(id=product_id)

    # Platform-owned products have no artisan to notify
    if not product.creator:
        return

    artisan_label = product.creator.display_name

    if approved:
        mail_subject = f"✅ [Product] Approved｜作品已通過 — {product.product_name}"
    else:
        mail_subject = f"📝 [Product] Revision Needed｜作品需要修改 — {product.product_name}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [product.creator.user.email]

    context = {
        "product": product,
        "artisan_label": artisan_label,
        "approved": approved,
        "note": note,
        "public_url": f"{settings.SITE_DOMAIN}{product.get_url()}" if approved else None,
        "dashboard_url": f"{settings.SITE_DOMAIN}/artisans/dashboard/products/",
        "year": timezone.now().year,
    }
    html_message = render_to_string("emails/product_review_result.html", context)
    plain_message = render_to_string("emails/product_review_result.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()


def send_product_deactivation_request_notification(product_id):
    """Notify the platform admin that an artisan requested a product deactivation."""
    from store.models import Product

    product = Product.objects.get(id=product_id)
    latest_log = product.review_logs.order_by('-created_at').first()
    reason = latest_log.note if latest_log else ""

    artisan_label = (
        product.creator.display_name if product.creator
        else "Platform｜平台"
    )

    mail_subject = f"⚠️ [Product] Deactivation Requested｜申請下架 — {product.product_name}"

    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [settings.ADMIN_EMAIL]

    context = {
        "product": product,
        "artisan_label": artisan_label,
        "reason": reason,
        "review_url": f"{settings.SITE_DOMAIN}/accounts/dashboard/product_review/",
        "year": timezone.now().year,
    }
    html_message = render_to_string("emails/product_deactivation_request.html", context)
    plain_message = render_to_string("emails/product_deactivation_request.txt", context)

    mail = EmailMultiAlternatives(
        subject=mail_subject,
        body=plain_message,
        from_email=from_email,
        to=to_email,
        bcc=[from_email],
    )
    mail.attach_alternative(html_message, "text/html")
    mail.encoding = "utf-8"
    mail.send()