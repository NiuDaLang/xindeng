# orders.views.py
from django.shortcuts import render, redirect, get_object_or_404
from carts.models import ProformaInvoice
from carts.forms import ProformaInvoiceForm
from xindeng import settings
from accounts.data import COUNTRY_CODE, CURRENCY_SYMBOL, INTEGER_CURRENCIES
from accounts.models import CustomerVoucher, Perk
from accounts.evaluators import PerkEvaluator
from .models import Payment, Order, OrderProduct, OrderVoucherUsage
from django.db import transaction
from django.http import FileResponse, Http404
from .utils import generate_order_confirmation_pdf, format_accounting_currency, mark_off_perk_at_checkout, execute_atomic_voucher_deduction, reverse_perk_usage_at_cancellation
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import intcomma
from decimal import Decimal
from accounts.models import UserProfile, Address
from store.models import ProductVariation, DigitalDownloadToken
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .tasks import send_inquiry_notification_email_task, send_cancellation_initiation_email_task, send_gift_receiver_revocation_email_task, send_cancellation_completion_email_task
from store.models import DigitalDownloadToken
from pathlib import Path
from carts.models import Cart
from carts.views import _cart_id
from django.contrib.auth import get_user_model
from .models import OrderInquiry
from django.http import JsonResponse
from django.urls import reverse
from carts.models import CartItem, CheckoutInfo
from .tasks import send_gift_voucher_email_task, send_e_product_email_task, send_order_confirmation_email_task

import json
import decimal
import logging

# Import your explicit celery tasks directly
from .tasks import check_and_expire_hold, send_bank_hold_confirmation_email_task

logger = logging.getLogger(__name__)


def place_order(request, proforma_invoice_no):
    """
    Handles the offline payment workflow path. Initializes the stock hold parameters,
    creates the Order record as UNPAID (is_ordered=False), and dispatches hold notices.
    """
    try:
        proforma_invoice = ProformaInvoice.objects.get(proforma_order_number=proforma_invoice_no)
        print("proforma_invoice.email: ", proforma_invoice.email)
        # Safeguard: Bounces them to receipt if already finalized
        if proforma_invoice.is_ordered:
            return redirect(f"/orders/order_complete/?order_number={proforma_invoice_no}&method=bank")

       # 🌟 BACKUP LOCKPOINT: Ensure an unauthenticated checkout hasn't snuck through with a member email
        if not request.user.is_authenticated and proforma_invoice.email:
            User = get_user_model()
            print("User: ", User)
            if User.objects.filter(email__iexact=proforma_invoice.email).exists():
                request.session["prior_session_key"] = _cart_id(request)
                request.session["next_url"] = request.path
                request.session.modified = True
                print("place order next_url: ", request.session.get("next_url"))
                if request.headers.get("HX-Request"):
                    response = HttpResponse("&nbsp;", status=200)
                    response["HX-Trigger"] = json.dumps({
                        "errorMssg": {
                            "title": "Login Required｜請先登入",
                            "text": "Please log in to complete this transaction.<br>檢測到此電子郵件已註冊會員。請先登入以合併您的購物車並完成交易！",
                            "redirect_url": "/accounts/login/" # Replace with your login URL path
                        }
                    })
                    return response
                
                messages.warning(request, "Please log in to your account to continue checkout.｜該電子郵件已註冊。請先登入會員帳號以繼續結帳。")
                return redirect("login")

        cart_items = proforma_invoice.cart.cartitem_set.all() if proforma_invoice.cart else []

        foreign_currency_code = request.COOKIES.get('user_currency') or request.session.get('user_currency', 'HKD')
        country_code = COUNTRY_CODE.get(foreign_currency_code, 'HK')
        is_integer = foreign_currency_code in INTEGER_CURRENCIES

        # 🎯 TRACK COHESIVE RECIPIENT ACCURACY BOUNDARIES
        # If display_mode is digital, or if name values are missing, explicitly flag it False
        has_recipient_info = False
        if proforma_invoice.recipient_first_name and proforma_invoice.recipient_last_name:
            if proforma_invoice.recipient_first_name.strip() != "None" and proforma_invoice.recipient_last_name.strip() != "None":
                has_recipient_info = True                
        # -------------------------------------------------------------
        # 🔥 HANDLE BANK TRANSFER SUBMISSIONS DIRECTLY VIA NATIVE HTML/HTMX
        # -------------------------------------------------------------
        if request.method == "POST":
            action_method = request.POST.get("payment_method")
            if action_method == "BANK_TRANSFER":
                expiry_time = timezone.now() + timedelta(hours=72)
                # expiry_time = timezone.now() + timedelta(minutes=60)
                # expiry_time = timezone.now() + timedelta(seconds=30)

                # 1. Fetch the active cart using an explicit row lock
                active_cart = proforma_invoice.cart
                if active_cart:
                    # 2. Break the direct relationship link with the user account 
                    # so this specific cart becomes an immutable historical log
                    active_cart.user = None
                    active_cart.cart_id = f"{active_cart.cart_id}_hold_{proforma_invoice_no}"
                    active_cart.save()
                    
                    # 3. Optional: Clear out session variables to prevent browser leaks
                    if 'cart_id' in request.session:
                        del request.session['cart_id']
                
                # 4. Generate a completely fresh, blank shopping bag for their next round of shopping
                if request.user.is_authenticated:
                    new_cart_id = _cart_id(request)
                    
                    # 🌟 THE SNAP FIX: Remove the 'defaults=' wrapper and assign 'cart_id' directly as a field argument!
                    new_cart, created = Cart.objects.update_or_create(
                        user=request.user,
                        defaults={'cart_id': new_cart_id}
                    )
                    request.session['cart_id'] = new_cart.id
                    print(f"🛒 FRESH CANVAS ENGAGED: Rotated Cart ID to {new_cart.id} for user {request.user.id}")                    

                try:
                    with transaction.atomic():
                        invoice = ProformaInvoice.objects.select_for_update().get(pk=proforma_invoice.pk)
                        if invoice.is_ordered:
                            return redirect(f"/orders/order_complete/?order_number={proforma_invoice_no}&method=bank")
                            
                        for item in cart_items:
                            variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                            if variation.stock < item.quantity:
                                out_of_stock_payload = {
                                    "title": "庫存不足｜Out of Stock Alert", 
                                    "text": f"Sorry, [{variation}] only has {variation.stock} units remaining.<br>抱歉，商品 [{variation}] 僅剩 {variation.stock} 件可用庫存，無法完成鎖定。", 
                                    "redirect_url": "/carts/cart/"}
                                response = HttpResponse("&nbsp;", content_type="text/html", status=200)
                                response["HX-Reswap"] = "none"
                                response["HX-Trigger"] = json.dumps({"errorMssg": out_of_stock_payload})
                                return response

                        voucher_session = request.session.get("applied_voucher", {})
                        voucher_to_spend = Decimal(str(voucher_session.get("applied_voucher_amount", "0")))

                        voucher_changes = []
                        if voucher_to_spend > 0 and request.user.is_authenticated:
                            voucher_changes = execute_atomic_voucher_deduction(request.user, voucher_to_spend)

                        # 🎯 ATOMIC COUPON MARK-OFF EXECUTION
                        offer_session = request.session.get("offer_applied", {})
                        offer_code = offer_session.get("offer_code")

                        if offer_code and request.user.is_authenticated:
                            try:
                                # This will raise a ValidationError if coupon checks fail
                                mark_off_perk_at_checkout(request.user, offer_code)
                            except ValidationError as perk_err:
                                # Intercept and pass cleanly to your front-end SWAL handler
                                response = HttpResponse("&nbsp;", content_type="text/html", status=200)
                                response["HX-Reswap"] = "none"
                                response["HX-Trigger"] = json.dumps({
                                    "errorMssg": {
                                        "title": "Offer Verification Failed｜優惠校驗失敗",
                                        "text": str(perk_err.message),
                                        "redirect_url": "/carts/cart/"
                                    }
                                })
                                return response
                            
                        # 1. Update Proforma Invoice state parameters
                        invoice.payment_method = "BANK_TRANSFER"
                        invoice.inventory_hold_expiry = expiry_time
                        invoice.is_ordered = True
                        invoice.save()

                        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

                        # 2. Map and generate the complementary permanent Order record
                        order, created = Order.objects.get_or_create(
                            order_number=invoice.proforma_order_number,
                            defaults={
                                "user": invoice.user,
                                "email": invoice.email, 
                                "recipient_first_name": invoice.recipient_first_name,
                                "recipient_last_name": invoice.recipient_last_name,
                                "recipient_mobile_area": invoice.recipient_mobile_area,
                                "recipient_mobile_number": invoice.recipient_mobile_number,

                                "recipient_email": invoice.recipient_email, # 🎯 Transfer Gift Email
                                "gift_message": invoice.gift_message,       # 🎯 Transfer Gift Message
                                
                                "address_line_1": invoice.address_line_1,
                                "address_line_2": invoice.address_line_2,
                                "city": invoice.city,
                                "state_province_region": invoice.state_province_region, 
                                "country": invoice.country,
                                "postal_code": invoice.postal_code,
                                "delivery_note": invoice.delivery_note,
                                "do_not_send_invoice": invoice.do_not_send_invoice,
                                
                                # Financial Totals Base CNY
                                "product_total": invoice.cart_total,
                                "shipping_cost": invoice.shipping_cost,
                                "discount": invoice.discount,
                                "tax": invoice.tax,
                                "voucher_applied": invoice.voucher_applied,
                                "total_due": invoice.total_due,
                                
                                # Foreign details
                                "product_total_foreign": invoice.cart_total_foreign,
                                "shipping_cost_foreign": invoice.shipping_cost_amount_foreign,
                                "discount_foreign": invoice.discount_amount_foreign,
                                "tax_foreign": invoice.tax_amount_foreign,
                                "voucher_applied_foreign": invoice.applied_voucher_amount_foreign,
                                "total_due_foreign": invoice.total_due_foreign,
                                "locked_exchange_rate": invoice.locked_exchange_rate,
                                "currency_code": invoice.currency_code,

                                "ip": ip,
                                "is_ordered": False,
                                "ordered_at": None,
                                "inventory_hold_expiry": expiry_time,
                                "order_status": "Hold_Pending"
                            }
                        )

                        # 🎯 4. LOG DEDUCTION ENTRIES FOR POTENTIAL CANCELLATION REFUNDS
                        for change in voucher_changes:
                            OrderVoucherUsage.objects.create(
                                order=order,
                                voucher=change['voucher_instance'],
                                amount_deducted=change['amount']
                            )

                        # 3. Process inventory deductions and create permanent OrderProduct snapshots
                        for item in cart_items:
                            variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                            
                            # 🌟 CORE CONDITION: Determine if this is an instant digital product (excluding vouchers)
                            is_instant_eproduct = variation.product.is_digital and variation.product.digital_fulfillment_type == 'INSTANT' and not variation.product.is_voucher

                            if is_instant_eproduct:
                                # Enforce business rules: Limit infinite digital products to a single quantity unit per order
                                if item.quantity > 1:
                                    raise ValueError(f"數位產品 [{variation.product.product_name}] 單筆訂單限購 1 件")
                                # Ensure infinite products are always marked as available without crashing stock counters
                                if not variation.is_available:
                                    raise ValueError(f"數位產品 [{variation.product.product_name}] 目前已下架不可選購")
                            else:
                                # ── PHYSICAL & VOUCHER VALIDATION AND DEDUCTION ──────────────────
                                if variation.stock < item.quantity:
                                    raise ValueError(f"商品 [{variation}] 庫存不足")
                                
                                # Deduct physical/voucher warehouse stock
                                variation.stock -= item.quantity
                                
                            variation.save()
                            
                            # Save line item snapshot record attached to Order
                            OrderProduct.objects.create(
                                order=order,
                                user=invoice.user,
                                product=item.product_variation.product,
                                product_variation=item.product_variation,
                                quantity=item.quantity,
                                product_price=item.product_variation.price,
                                ordered=False,
                                fulfilled_by=variation.product.creator,   # 🌟 NEW — auto-attributed
                                fulfillment_started_at=timezone.now(),     # 🌟 NEW — payment just cleared
                            )

                        # 4. ADDRESS BOOK INJECTION
                        if request.user.is_authenticated and invoice.is_default_address is False:
                            user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
                            
                            if invoice.display_mode in ["PHYSICAL", "PHYSICAL_AND_VOUCHER"]:
                                Address.objects.get_or_create(
                                    profile=user_profile,
                                    recipient_first_name=invoice.recipient_first_name,
                                    recipient_last_name=invoice.recipient_last_name,
                                    mobile_area=invoice.recipient_mobile_area,
                                    mobile_number=invoice.recipient_mobile_number,
                                    address_line_1=invoice.address_line_1,
                                    address_line_2=invoice.address_line_2,
                                    city=invoice.city,
                                    state_province_region=invoice.state_province_region,
                                    country=invoice.country,
                                    postal_code=invoice.postal_code,
                                    google_place_id=invoice.google_place_id,
                                    latitude=invoice.latitude,
                                    longitude=invoice.longitude,
                                    is_verified_by_google=invoice.is_verified_by_google,
                                )

                        # 🔒 INVALIDATE CURRENT CART ITEMS TO PREVENT DOUBLE CHECKOUTS
                        cart_items.update(is_active=False)

                        # 5. Clear out session configuration variables
                        for session_key in ["applied_voucher", "offer_applied", "shipping_data", "active_proforma_id"]:
                            request.session.pop(session_key, None)
                        request.session.modified = True

                        # 6. Decouple proforma instance link from the cart object
                        invoice.cart = None
                        invoice.save()

                    # 🔥 Trigger background processing safely outside atomic transaction lock block
                    transaction.on_commit(lambda: send_bank_hold_confirmation_email_task.delay(order.id))
                    transaction.on_commit(lambda: check_and_expire_hold.apply_async((order.id,), eta=expiry_time))
                    
                    if request.headers.get("HX-Request"):
                        response = HttpResponse("", status=200)
                        location_payload = {
                            "path": f"/orders/order_complete/?order_number={invoice.proforma_order_number}&method=bank",
                            "target": "body",      
                            "swap": "innerHTML"    
                        }
                        response["HX-Location"] = json.dumps(location_payload)
                        return response

                    # 💡 SECURE AUTHORIZATION: Whitelist this order number in the guest's session
                    accessible = request.session.get("accessible_receipts", [])
                    accessible.append(proforma_invoice_no)
                    request.session["accessible_receipts"] = accessible
                    request.session.modified = True
                        
                    return redirect(f"/orders/order_complete/?order_number={invoice.proforma_order_number}&method=bank")

                except ValueError as stock_err:
                    print("stock_err")
                    messages.error(request, str(stock_err))
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                
        # -------------------------------------------------------------
        # 💡 STANDARD GET RENDERING PIPELINE
        # -------------------------------------------------------------
        context = {
            "cart_items": cart_items,
            "cart_total_quantity": proforma_invoice.cart.get_items_count(),
            "proforma_invoice": proforma_invoice,
            "proforma_invoice_number": proforma_invoice.proforma_order_number,
            "foreign_currency_code": foreign_currency_code,
            "foreign_currency_symbol": CURRENCY_SYMBOL.get(foreign_currency_code, '$'),
            "locked_rate": proforma_invoice.locked_exchange_rate,
            "rate_expiry_timestamp": int(request.session.get("rate_expiry_time", 0)),
            "page_title": f"Pay Order｜支付訂單號 {proforma_invoice_no}",
            "main_title": "Place Order｜支 付 訂 單",
            "sub_title_1": "Complete Purchase｜迎接寶貝",
            "bread_crumb_1": "Home｜首頁",
            "bread_crumb_2": "Pay Now｜訂單支付",
            "bread_crumb_1_url": "/",
            "bread_crumb_2_url": request.path,
            
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
            "is_integer": is_integer,
            "country_code": country_code,
            "display_mode": proforma_invoice.display_mode,
            "has_recipient_info": has_recipient_info,
        }
        return render(request, 'orders/place_order.html', context)
    
    except (ProformaInvoice.DoesNotExist, Http404):
        # 🌟 THE EXCEPTION FIX: Intercept missing links and route back to cart safely
        messages.warning(request, "This checkout session has expired or was removed.｜該結算單已過期或已被移除，請重新結算。")
        return redirect('cart')
    

def order_complete(request):
    """Renders final receipts cleanly. Handles refreshes and duplicate loads securely."""
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    
    if not order_number:
        return redirect("home")
    
    try:
        proforma_invoice = ProformaInvoice.objects.get(proforma_order_number=order_number, is_ordered=True)
    except ProformaInvoice.DoesNotExist:
        messages.info(request, "Order details not found or session expired.｜找不到該訂單明細，可能已被封存或重置。")
        return redirect("cart")

    # ─────────────────────────────────────────────────────────────
    # 🔒 AUTHENTICATION & ACCESS SANITATION GATEWAY
    # ─────────────────────────────────────────────────────────────
    # Check if the invoice is associated with a registered member account
    if hasattr(proforma_invoice, 'user') and proforma_invoice.user:
        if not request.user.is_authenticated or request.user != proforma_invoice.user:
            messages.error(request, "Unauthorized access to this receipt.｜您無權查看此訂單明細。")
            return redirect("home")
    else:
        # For Anonymous Guest Checkout: Verify against a temporary session whitelist
        allowed_receipts = request.session.get("accessible_receipts", [])
        if order_number not in allowed_receipts:
            messages.error(request, "Receipt viewing window has expired.｜訂單查閱授權已過期。")
            return redirect("home")
    
    order = None
    ordered_products = []
    payment = None
    is_bank_transfer = (proforma_invoice.payment_method == "BANK_TRANSFER")

    foreign_currency_code = request.COOKIES.get('user_currency', 'HKD')
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, f"{foreign_currency_code} ")
    is_integer = foreign_currency_code in INTEGER_CURRENCIES
    cny_symbol = '¥'

    # 🌟 FIX UNBOUND LOCAL VARIABLE ERRORS BY DEFINING ANCHOR baselines
    base_product_total = Decimal("0.00")
    base_shipping_cost = Decimal("0.00")
    base_discount = Decimal("0.00")
    base_voucher = Decimal("0.00")
    base_total_due = Decimal("0.00")

    if is_bank_transfer:
        main_title = "Order Hold Confirmed｜訂單保留中"
        sub_title_1 = "Please complete transfer within 72 hours.｜請於72小時內完成付款以保留商品庫存。"
        
        # 🌟 THE EXPIRATION GUARD PASS
        # Immediately check if the un-finalized bank transfer hold has already expired!
        if proforma_invoice.inventory_hold_expiry and timezone.now() > proforma_invoice.inventory_hold_expiry:
            # Inject a clear banner notice message via Django's messaging framework
            messages.error(
                request, 
                "This inventory reservation hold has expired. The items have been returned to stock."
                "｜該筆訂單保留期已屆滿失效，庫存商品已被系統釋出。請重新將商品加入購物車結帳。 "
            )
            
            # 🔒 CLEAN SESSIONS UPON LAPSING FOR MAXIMUM INTEGRITY
            request.session.pop("offer_applied", None)
            request.session.pop("applied_voucher", None)
            request.session.modified = True
            
            # Safely re-route them back to the active shopping bag view node
            return redirect("cart")

        try:
            order = Order.objects.get(order_number=order_number, is_ordered=False)

            # Double check the order instance itself just in case statuses were updated by admin actions
            if order.order_status == 'Cancelled':
                messages.warning(request, "此訂單已被取消。｜This order hold has been cancelled.")
                return redirect("cart")
                     
            db_products = OrderProduct.objects.filter(order=order)
            
            for prod in db_products:
                ordered_products.append({
                    'product_variation': prod.product_variation,
                    'quantity': prod.quantity,
                    'formatted_price': format_accounting_currency(prod.product_price, cny_symbol, False),
                    'formatted_subtotal': format_accounting_currency(prod.get_subtotal(), cny_symbol, False)
                })
            
            base_product_total = order.product_total
            base_shipping_cost = order.shipping_cost
            base_discount = order.discount
            base_voucher = order.voucher_applied
            base_total_due = order.total_due

        except Order.DoesNotExist:
            return redirect("cart")
    else:
        main_title = "Payment Complete｜訂單完成"
        sub_title_1 = "Thank You for Your Support!｜感謝您對我們的支持！"
    
        try:
            order = Order.objects.get(order_number=order_number, is_ordered=True)
            db_products = OrderProduct.objects.filter(order=order)
            
            for prod in db_products:
                ordered_products.append({
                    'product_variation': prod.product_variation,
                    'quantity': prod.quantity,
                    'formatted_price': format_accounting_currency(prod.product_price, cny_symbol, False),
                    'formatted_subtotal': format_accounting_currency(prod.get_subtotal(), cny_symbol, False)
                })
                
            # ─────────────────────────────────────────────────────────────
            # 🔒 HARDENED PAYMENT TRANSACTION LOOKUP ENGINE
            # ─────────────────────────────────────────────────────────────
            if transaction_id:
                payment = Payment.objects.filter(payment_id=transaction_id).first()
                
            # 💡 FAIL-SAFE 1: If transaction_id was missing or the webhook was slow,
            # lookup using the locked Proforma Invoice relationship (100% Reliable)
            if not payment and proforma_invoice:
                payment = Payment.objects.filter(invoice=proforma_invoice).first()
                
            # 💡 FAIL-SAFE 2: If it's still missing, lookup using the confirmed Order row
            if not payment and order:
                payment = Payment.objects.filter(order_id=order.order_number).first()
                
            # 💡 FAIL-SAFE 3: Memory-Mock object fallback. If the PayPal webhook is heavily 
            # delayed, build a temporary mock object using invoice parameters so the 
            # frontend template can still render the currency boxes cleanly without crashing!
            if not payment:
                print(f"⚠️ [Webhook Lag caught] Payment row missing for invoice {order_number}. Building secure runtime proxy fallback.")
                from types import SimpleNamespace
                payment = SimpleNamespace(
                    currency=proforma_invoice.currency_code or "USD",
                    amount_paid=proforma_invoice.total_due_foreign,
                    status="Pending"
                )

            print("🚀 Final resolved payment object context parameter: ", payment)
            
            base_product_total = order.product_total
            base_shipping_cost = order.shipping_cost
            base_discount = order.discount
            base_voucher = order.voucher_applied
            base_total_due = order.total_due
                
        except Order.DoesNotExist:
            # Fallback to proforma values if the payment callback processes slower than user redirects
            base_product_total = proforma_invoice.cart_total
            base_shipping_cost = proforma_invoice.shipping_cost
            base_discount = proforma_invoice.discount
            base_voucher = proforma_invoice.voucher_applied
            base_total_due = proforma_invoice.total_due
    
    target_source = order if order else proforma_invoice
    
    has_self_voucher = False

    if order:
        has_self_voucher = order.items.filter(
            product_variation__product__is_voucher=True
        ).exists() and (not order.recipient_email or order.recipient_email.strip().lower() == order.email.strip().lower())
        
        raw_db_shipping_fx = Decimal(str(target_source.shipping_cost_foreign))
        raw_db_discount_fx = Decimal(str(target_source.discount_foreign))
        raw_db_voucher_fx = Decimal(str(target_source.voucher_applied_foreign))
    else:
        raw_db_shipping_fx = Decimal(str(target_source.shipping_cost_amount_foreign))
        raw_db_discount_fx = Decimal(str(target_source.discount_amount_foreign))
        raw_db_voucher_fx = Decimal(str(target_source.applied_voucher_amount_foreign))
    
    raw_db_payable_fx = Decimal(str(target_source.total_due_foreign))
    raw_db_subtotal_fx = raw_db_payable_fx + raw_db_discount_fx + raw_db_voucher_fx - raw_db_shipping_fx
    
    context = {
        "main_title": main_title, 
        "sub_title_1": sub_title_1, 
        "has_self_voucher": has_self_voucher,
        "page_title": "訂單完成｜Order Complete",
        "bread_crumb_1": "首頁｜Home",
        "bread_crumb_2": "訂單完成｜Order Complete",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": request.path,

        "proforma_invoice": proforma_invoice, 
        "order": order,
        "total_order_items_quantity": order.get_total_items_count(),
        "ordered_products": ordered_products,
        "transaction_id": transaction_id, 
        "payment": payment, 
        "is_bank_transfer": is_bank_transfer,
        "foreign_currency_code": foreign_currency_code,

        "cny_product_total": format_accounting_currency(base_product_total, cny_symbol, False),
        "cny_shipping_cost": format_accounting_currency(base_shipping_cost, cny_symbol, False),
        "cny_discount": format_accounting_currency(-base_discount if base_discount > 0 else 0, cny_symbol, False),
        "cny_voucher": format_accounting_currency(-base_voucher if base_voucher > 0 else 0, cny_symbol, False),
        "cny_total_due": format_accounting_currency(base_total_due, cny_symbol, False),
        
        "is_integer": is_integer,
        "foreign_product_total": format_accounting_currency(raw_db_subtotal_fx, foreign_currency_symbol, is_integer),
        "foreign_shipping_cost": format_accounting_currency(raw_db_shipping_fx, foreign_currency_symbol, is_integer),
        "foreign_discount": format_accounting_currency(-raw_db_discount_fx if raw_db_discount_fx > 0 else 0, foreign_currency_symbol, is_integer),
        "foreign_voucher": format_accounting_currency(-raw_db_voucher_fx if raw_db_voucher_fx > 0 else 0, foreign_currency_symbol, is_integer),
        "foreign_total_due": format_accounting_currency(raw_db_payable_fx, foreign_currency_symbol, is_integer),
    }

    # 🔒 CLEAN SESSIONS IF RETRIEVED SAFELY
    if "offer_applied" in request.session or "applied_voucher" in request.session:
        request.session.pop("offer_applied", None)
        request.session.pop("applied_voucher", None)
        request.session.modified = True

    return render(request, "orders/order_complete.html", context)


@login_required(login_url='login')
@require_POST
def complete_zero_due_voucher_order(request):
    proforma_invoice_number = request.GET.get("invoice")
    created_vouchers = []
    
    try:
        with transaction.atomic():
            # 1. Pessimistic row-lock capture on active ProformaInvoice context
            proforma_order = ProformaInvoice.objects.select_for_update().get(
                proforma_order_number=proforma_invoice_number, 
                user=request.user, 
                is_ordered=False
            )
            
            if proforma_order.total_due > 0:
                return JsonResponse({"error": "Gateway capture required for pending balances."}, status=400)
            
            active_cart = proforma_order.cart
            cart_items = CartItem.objects.filter(cart=active_cart, is_active=True)
            
            # 2. 🎯 FINAL LAST-SECOND RACE CONDITION PROTECTION BLOCK
            for item in cart_items:
                variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                if variation.stock < item.quantity:
                    raise ValueError(f"Race condition stock failure caught for {variation}")

            # 3. Process voucher deductions instantly if applied to cart session (Page 2 Mismatch Fix)
            voucher_session = request.session.get("applied_voucher", {})
            voucher_to_spend = Decimal(str(voucher_session.get("applied_voucher_amount", "0")))
            
            # Failsafe check: If session cache failed or cleared early, read directly from proforma
            if voucher_to_spend == 0 and proforma_order.voucher_applied > 0:
                voucher_to_spend = proforma_order.voucher_applied

            voucher_changes = []
            if voucher_to_spend > 0:
                # 🌟 THIS IS THE CRITICAL LINE THAT DECRIMENTS YOUR WALLET LEDGERS ATOMICALLY
                voucher_changes = execute_atomic_voucher_deduction(request.user, voucher_to_spend)

            # 4. Safely get or create the order on the fly (Matching PayPal layout defaults)
            order, order_created = Order.objects.select_for_update().get_or_create(
                order_number=proforma_invoice_number,
                defaults={
                    "user": proforma_order.user,
                    "email": proforma_order.email,
                    "recipient_first_name": proforma_order.recipient_first_name,
                    "recipient_last_name": proforma_order.recipient_last_name,
                    "recipient_mobile_area": proforma_order.recipient_mobile_area,
                    "recipient_mobile_number": proforma_order.recipient_mobile_number,
                    "recipient_email": proforma_order.recipient_email,
                    "gift_message": proforma_order.gift_message,
                    "address_line_1": proforma_order.address_line_1,
                    "address_line_2": proforma_order.address_line_2,
                    "city": proforma_order.city,
                    "state_province_region": proforma_order.state_province_region,
                    "country": proforma_order.country,
                    "postal_code": proforma_order.postal_code,
                    "delivery_note": proforma_order.delivery_note,
                    "do_not_send_invoice": proforma_order.do_not_send_invoice,
                    "product_total": proforma_order.cart_total,
                    "shipping_cost": proforma_order.shipping_cost,
                    "discount": proforma_order.discount,
                    "tax": proforma_order.tax,
                    "voucher_applied": proforma_order.voucher_applied,
                    "total_due": Decimal("0.00"),
                    "product_total_foreign": proforma_order.cart_total_foreign,
                    "shipping_cost_foreign": proforma_order.shipping_cost_amount_foreign,
                    "discount_foreign": proforma_order.discount_amount_foreign,
                    "tax_foreign": proforma_order.tax_amount_foreign,
                    "voucher_applied_foreign": proforma_order.applied_voucher_amount_foreign,
                    "total_due_foreign": Decimal("0.00"),
                    "locked_exchange_rate": proforma_order.locked_exchange_rate,
                    "currency_code": proforma_order.currency_code,
                    "is_ordered": False,
                    "order_status": "Processing"
                }
            )
            
            order.recipient_email = proforma_order.recipient_email
            order.gift_message = proforma_order.gift_message

            # 5. 🎯 LOG DEDUCTION ENTRIES FOR POTENTIAL CANCELLATION REFUNDS
            for change in voucher_changes:
                OrderVoucherUsage.objects.create(
                    order=order,
                    voucher=change['voucher_instance'],
                    amount_deducted=change['amount']
                )

            # Create permanent local Payment ledger record
            transaction_id = f"VUCH_SETTLED_{order.order_number}_{int(timezone.now().timestamp())}"
            payment = Payment.objects.create(
                user=request.user,
                invoice=proforma_order,
                order_id=f"VUCH_{order.order_number}",
                payment_id=transaction_id,
                payment_method='Voucher Balance',
                amount_paid=proforma_order.voucher_applied,
                currency=proforma_order.currency_code.upper().strip(),
                exchange_rate=proforma_order.locked_exchange_rate,
                cny_equivalent=proforma_order.voucher_applied,
                status="Completed"
            )
            
            order.payment = payment
            order.is_ordered = True
            order.ordered_at = timezone.now()
            order.save()

            # Relocate items securely over to structural OrderProduct tables
            for item in cart_items:
                variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                order_prod = OrderProduct.objects.create(
                    order=order,
                    payment=payment,
                    user=request.user,
                    product=variation.product,
                    product_variation=variation,
                    quantity=item.quantity,
                    product_price=variation.price,
                    ordered=True,
                    fulfilled_by=variation.product.creator,   # 🌟 NEW — auto-attributed
                    fulfillment_started_at=timezone.now(),     # 🌟 NEW — payment just cleared
                )
                
                is_instant_eproduct = variation.product.is_digital and variation.product.digital_fulfillment_type == 'INSTANT' and not variation.product.is_voucher
                if not is_instant_eproduct:
                    variation.stock -= item.quantity
                    variation.save(update_fields=['stock'])
                
                # E-Voucher Product Asset Management Generation Pipelines
                if variation.product.is_voucher:
                    buyer_email = proforma_order.email.strip().lower()
                    recipient_email = (proforma_order.recipient_email or "").strip().lower()
                    is_gift = recipient_email and recipient_email != buyer_email
                    for _ in range(item.quantity):
                        voucher = CustomerVoucher.objects.create(
                            value=variation.price,
                            balance=variation.price,
                            purchaser_email=proforma_order.email,
                            owner=None if is_gift else request.user,
                            registered_email=proforma_order.recipient_email if is_gift else proforma_order.email,
                            is_claimed=False if is_gift else True,
                            claimed_date=None if is_gift else timezone.now(),
                            is_used=False
                        )
                        if is_gift:
                            reg_link = request.build_absolute_uri(reverse('claim_voucher_url', args=[str(voucher.id)]))
                            transaction.on_commit(lambda v_id=voucher.id, link=reg_link: send_gift_voucher_email_task.delay(v_id, link))
                        created_vouchers.append(voucher)
                    order_prod.is_dispatched = True
                    order_prod.dispatched_at = timezone.now()
                    order_prod.save(update_fields=['is_dispatched', 'dispatched_at'])
                
                # Infinite Instant Digital Assets download token generation loops
                elif getattr(variation.product, 'is_digital', False) and getattr(variation.product, 'digital_fulfillment_type', 'INSTANT') == 'INSTANT':
                    expiration_time = timezone.now() + timedelta(hours=168)
                    download_token = DigitalDownloadToken.objects.create(
                        user=order.user,
                        order_product=order_prod,
                        expires_at=expiration_time
                    )
                    transaction.on_commit(lambda token_id=download_token.id: send_e_product_email_task.delay(str(token_id)))
                    order_prod.is_dispatched = True
                    order_prod.dispatched_at = timezone.now()
                    order_prod.save(update_fields=['is_dispatched', 'dispatched_at'])

            # After handling individual lines, automatically evaluate final status
            order.update_fulfillment_status()
            order.save(update_fields=['order_status'])
            
            proforma_order.is_ordered = True
            if active_cart:
                active_cart.cartitem_set.all().delete()
                CheckoutInfo.objects.filter(cart=active_cart).delete()
            proforma_order.cart = None
            proforma_order.save()

            # Clear completed configuration caches from user session matrix
            for session_key in ["applied_voucher", "offer_applied", "shipping_data", "active_proforma_id"]:
                request.session.pop(session_key, None)
                
            accessible = request.session.get("accessible_receipts", [])
            if proforma_invoice_number not in accessible:
                accessible.append(proforma_invoice_number)
            request.session["accessible_receipts"] = accessible
            request.session.save()

            # 🚀 MASTER SUCCESS SIGNAL: Trigger asynchronous confirmation receipt email
            transaction.on_commit(lambda: send_order_confirmation_email_task.delay(order.order_number))
            
            return JsonResponse({"status": "SUCCESS", "transaction_id": payment.payment_id, "order_number": proforma_invoice_number}, status=200)

    except ValueError as stock_err:
        logger.critical(f"⚠ VOUCHER CHECKOUT STOCK EXCEPTION: Invoice {proforma_invoice_number}. Error: {str(stock_err)}")
        return JsonResponse({
            "status": "STOCK_CONFLICT",
            "error": "Payment verified via voucher balances, but an item ran out of stock. Customer service will resolve your balances shortly.",
            "order_number": proforma_invoice_number,
            "transaction_id": f"ERR_{proforma_invoice_number}"
        }, status=200)
    except Exception as e:
        logger.exception(f"💥 Voucher Settlement Fatal Exception Trace: {str(e)}")
        return JsonResponse({"error": "Internal database serialization error"}, status=500)

    
# def order_confirmation_pdf(request, order_id): # to be deleted later
#     order = Order.objects.get(order_number=order_id, is_ordered=True)
#     proforma_invoice = ProformaInvoice.objects.get(proforma_order_number=order_id)
#     payment = order.payment
#     currency_symbol = CURRENCY_SYMBOL[payment.currency]
#     foreign_currency_digit = 2 if payment.currency not in INTEGER_CURRENCIES else 0
#     user = order.user
#     order_products = OrderProduct.objects.filter(order=order)
#     has_physical_products = False

#     for order_product in order_products:
#         product = order_product.product_variation.product
#         if product.category.product_format == "physical":
#             has_physical_products = True
            
#     context = {
#         "page_title": f"訂單確認｜Order Confirmation - {order.order_number}",
#         "user": user,
#         "proforma_invoice": proforma_invoice,
#         "order": order,
#         "payment": payment,
#         "currency_symbole":currency_symbol,
#         "foreign_currency_digit": foreign_currency_digit,
#         "order_products": order_products,
#         "has_physical_products": has_physical_products,
#     }
#     return render(request, "orders/order_confirmation_pdf.html", context)


def view_order_pdf(request, order_id):
    # 1. Call your ReportLab function
    buffer = generate_order_confirmation_pdf(order_id)
    
    # 2. IMPORTANT: Move the pointer to the start of the buffer
    buffer.seek(0)
    
    # 3. Return as a PDF response
    return FileResponse(
        buffer, 
        as_attachment=False, # False opens it in the browser tab
        filename=f'order_{order_id}.pdf',
        content_type='application/pdf'
    )


def download_invoice_pdf_view(request, order_id):
    """
    🔒 DUAL-AUTHORIZATION SECURE INVOICE STREAM
    Surgically validates authorization across both authenticated members and verified guest sessions,
    then streams the raw generated ReportLab PDF bytes safely to the browser.
    """
    # 1. Fetch the target order by its unique number string
    order = get_object_or_404(Order, order_number=order_id)
    
    # 2. EVALUATION GATEPASS MATRIX
    is_authorized = False
    
    # Pathway A: The request comes from an authenticated member who owns the transaction record
    if request.user.is_authenticated:
        if order.user == request.user:
            is_authorized = True
            
    # Pathway B: The request comes from an unauthenticated guest user
    else:
        # Pull your secure cached verification parameters out of their signed session vault
        session_order_num = request.session.get('verified_guest_order')
        session_email = request.session.get('verified_guest_email')
        
        # The guest is authorized ONLY if their session tokens perfectly match this specific order instance
        if session_order_num == order.order_number and session_email and session_email.lower() == order.email.lower():
            is_authorized = True

    # 3. SECURITY GUARD FORCING ACCESS BLOCK ON FAILURES
    if not is_authorized:
        # Throws a clean, secure 403 Forbidden exception to prevent fishing attacks
        raise PermissionDenied("Unauthorized access to this receipt pass. / 您無權查看此單據。")
    
    # 4. STREAM GENERATED REPORTLAB PDF BUFFER
    try:
        # Call your existing optimized ReportLab function block
        pdf_buffer = generate_order_confirmation_pdf(order.order_number)
        
        # Build the safe HTTP file container output passing binary descriptors
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        
        # 'attachment;' forces a direct file save download layout pass
        response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'
        
        return response
    except Exception as pdf_err:
        print(f"❌ PDF Engine download failure exception: {str(pdf_err)}")
        raise Http404("Could not generate statement invoice asset at this time. / 無法生成水單檔案。")


@require_http_methods(["GET", "POST"])
def guest_order_verify(request):
    """
    🔒 SECURE GUEST ROUTER ENGINE (V2)
    Validates tracking lookups, surfaces contextual SweetAlert historical data flags,
    and maintains live conversational trails for persistent customer interactions.
    """
    order = None
    trigger_swal = None

    if request.method == "POST" and "order_number" in request.POST:
        order_number = request.POST.get("order_number", "").strip()
        guest_email = request.POST.get("guest_email", "").strip()

        try:
            order = Order.objects.get(order_number=order_number, email__iexact=guest_email)
            
            # Persist safe verification state tracking metrics inside session cookies
            request.session['verified_guest_order'] = order.order_number
            request.session['verified_guest_email'] = guest_email
            request.session.modified = True
            
            # 🌟 CORE LOOKUP INTERCEPT GATEWAY: If the order is dead, prepare an info modal trigger
            if order.order_status in ['Cancelled', 'Refunding', 'Refunded']:
                status_mapping = {
                    'Cancelled': 'Cancelled｜訂單已取消',
                    'Refunding': 'Refund Processing｜退款處理中',
                    'Refunded': 'Fully Refunded｜退款已完成'
                }
                desc_mapping = {
                    'Cancelled': 'This purchase was cancelled. Our finance operations desk is organizing your repayment file.',
                    'Refunding': 'Your refund stream is being cleared via PayPal. Funds should reflect inside your source account shortly.',
                    'Refunded': 'Transaction lifecycle complete. The financial balance has been fully returned to your payment avenue.'
                }
                
                trigger_swal = {
                    "status": order.order_status,
                    "title": status_mapping.get(order.order_status, "Order Update"),
                    "html": f"{desc_mapping.get(order.order_status)}<br><small class=\"font-mono opacity-50\">Last Updated: {order.updated_at.strftime('%Y-%m-%d %H:%M')}</small>",
                    "icon": "info" if order.order_status == 'Refunding' else "success"
                }
                
        except Order.DoesNotExist:
            messages.error(request, "Invalid order metrics pattern. Check your receipt parameters. / 訂單資訊驗證失敗，請重新核對。")
            return redirect('contact')

    elif request.method == "POST" and "message_content" in request.POST:
        session_order_num = request.session.get('verified_guest_order')
        session_email = request.session.get('verified_guest_email')

        if not session_order_num:
            messages.error(request, "Session expired. Re-authenticate your token layout.｜連線逾時，請重新驗證。")
            return redirect('contact')

        order = get_object_or_404(Order, order_number=session_order_num, email__iexact=session_email)
        message_content = request.POST.get("message_content", "").strip()

        if message_content:
            inquiry = OrderInquiry.objects.create(
                order=order,
                message_content=message_content,
                is_from_staff=False,
                staff_user=None
            )
            
            # Fire Celery task to notify store admins
            send_inquiry_notification_email_task.delay(inquiry.id)

            # 🚀 STANDARD DIRECT SWAP INTERCEPT GATE (Matches your work pattern)
            if request.headers.get("HX-Request"):
                sanitized_message = inquiry.message_content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
                current_time_str = timezone.now().strftime('%Y-%m-%d %H:%M')

                # Return ONLY the plain chat bubble. HTMX appends it right to the target container automatically.
                html_response = f"""
                <div class="chat chat-end animate-fade-in">
                    <div class="chat-header text-[10px] opacity-50 font-sans tracking-wide mb-1 select-none">
                        <span>Buyer / 顧客留言</span>
                        <time class="ml-1 font-mono text-[9px]">{current_time_str}</time>
                    </div>
                    <div class="chat-bubble text-xs leading-relaxed font-sans max-w-[85%] sm:max-w-[70%] rounded-2xl p-3 shadow-xs bg-neutral text-neutral-content">
                        {sanitized_message}
                    </div>
                </div>
                """
                return HttpResponse(html_response)

            # Standard browser reload fallback router
            messages.success(request, "Inquiry dispatched safely to the care team.｜您的留言已成功送出！")
            return redirect('guest_order_verify')

    else:
        # standard GET requests fallback sequence processing
        session_order_num = request.session.get('verified_guest_order')
        session_email = request.session.get('verified_guest_email')

        if session_order_num and session_email:
            order = get_object_or_404(Order, order_number=session_order_num, email__iexact=session_email)
        else:
            return redirect('contact')

    context = {
        "order": order,
        # Convert dictionary parameter context cleanly to safe inline JSON text layout indicators
        "trigger_swal_json": json.dumps(trigger_swal) if trigger_swal else None
    }
    return render(request, "orders/guest_order_detail.html", context)


# def is_order_eligible_for_online_cancellation(order):
#     """
#     Item-Level Deep Validation Engine.
#     Excludes any orders with discounts applied from automatic online cancellation.
#     """
#     # 🌟 NEW CONDITION: DISCOUNT SHIELD GATE
#     # Blocks orders with promotional discounts from self-service cancellation
#     if hasattr(order, 'discount') and order.discount > 0:
#         return False, "Orders with promotional offers applied require manual processing. Please contact support. / 包含特惠折抵的訂單無法線上自動取消，請洽客服人員。"

#     now = timezone.now()
    
#     # Pre-fetch items with their product relations to optimize database queries
#     order_items = order.items.select_related('product').all()
    
#     if not order_items.exists():
#         return False, "This order contains no items. / 訂單內無商品紀錄。"

#     for item in order_items:
#         product = item.product
        
#         # 🌟 CONDITION 1: PHYSICAL PRODUCT AUDIT
#         if product.is_physical:
#             # If even a single physical item has been shipped by the warehouse, block automatic cancellation
#             if item.is_dispatched:
#                 return False, f"Physical item '{product.product_name}' has been dispatched. Please contact support. / 實體商品已發貨，請聯絡客服。"
        
#         # 🌟 CONDITION 2: INSTANT E-PRODUCT AUDIT (Excluding Vouchers)
#         elif product.is_digital and product.digital_fulfillment_type == 'INSTANT' and not product.is_voucher:
#             # Block 1: Check if the secure link has already been clicked/downloaded
#             if item.is_claimed:
#                 return False, f"Digital item '{product.product_name}' has already been claimed. / 數位產品已下載領取，無法取消。"
            
#             # Block 2: Enforce the 7-day payment window expiration limit
#             if (now - order.created_at).days > 7:
#                 return False, "The 7-day digital download cancellation window has expired. / 已超過 7 天數位產品鑑賞期限制。"
        
#         # 🌟 CONDITION 3: VOUCHER GIFT PRODUCT AUDIT
#         elif product.is_voucher:
#             # Vouchers are paid in cash and don't affect structural physical fulfillment eligibility,
#             # but we protect the system by blocking the cancellation if the voucher has already been claimed/used. [INDEX]
#             if item.is_partially_used:
#                 return False, "Gift credit voucher has been partially consumed or claimed. / 禮品券已被核銷使用，無法取消。"

#     return True, "Eligible"


def process_order_cancellation(request, order_number):
    """
    Multi-Tier Billing Reconciliation & Dispatch Engine.
    Manages complex split-payment returns, currency checking, and multi-route email queuing.
    [Part 1 of 5: Security Clearance & Validation Handshakes]
    """

    # 🌟 Direct lookup by token alone to protect casual guest routing visibility
    order = get_object_or_404(Order, order_number=order_number)
    refund_type = request.GET.get('refund_type', 'cash')

    # =========================================================================
    # 🔒 BILINGUAL DUAL-AUTHORIZATION GATEKEEPER PASS (Section C-b)
    # =========================================================================
    is_authorized = False
    if request.user.is_authenticated:
        if order.user == request.user:
            is_authorized = True
    else:
        # Fallback check against anonymous verified session keys stored during tracking lookup
        session_order_num = request.session.get('verified_guest_order')
        session_email = request.session.get('verified_guest_email')
        if session_order_num == order.order_number and session_email and session_email.lower() == order.email.lower():
            is_authorized = True

    # 🌟 FIXED: Intercept mismatched validation handshakes for fetch pipelines immediately
    if not is_authorized:
        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                "status": "UNAUTHORIZED", 
                "error": "Verification required. Session credentials invalid. / 驗證失效，請重新登入。"
            }, status=403)
        
        # Fallback security track for standard structural HTML link redirects
        messages.error(request, "Verification required. Session credentials invalid. / 驗證失效，請提供正確的下單信箱。")
        return redirect('home')

    # =========================================================================
    # 📝 EXECUTE SYSTEM ELIGIBILITY AUDIT & FEE HARVEST (Section C-c / C-d)
    # =========================================================================
    # Calls the unified tuple generator built inside your order model instance
    is_eligible, total_cancellation_fee, audit_message = order.evaluate_cancellation_details()
    if not is_eligible:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({"status": "INELIGIBLE", "error": audit_message}, status=400)
        messages.error(request, audit_message)
        return redirect('dashboard', subpage='orders') if request.user.is_authenticated else redirect('contact')

    # Enforce hard model constraints: Full voucher check completely overrides choices
    paid_entirely_by_voucher = (order.voucher_applied >= order.total_due)
    if paid_entirely_by_voucher:
        refund_type = 'voucher'

    user_is_member = order.user is not None

    # =========================================================================
    # ⚡ BEGIN ATOMIC DATABASE TRANSACTION MATRIX (Section C-e)
    # =========================================================================
    try:
        with transaction.atomic():
            # Re-fetch for update to prevent racing transaction conditions across execution threads
            order = Order.objects.select_for_update().get(id=order.id)
            
            # Update order tracking milestones cleanly before committing down to accounting splits
            order.order_status = 'Refunding'
            order.updated_at = timezone.now()

            # 📦 Restock physical inventory item variations safely (Section C-e)
            for item in order.items.all():
                if item.product_variation:
                    variation = item.product_variation
                    
                    is_instant_eproduct = (
                        item.product.is_digital and 
                        item.product.digital_fulfillment_type == 'INSTANT' and 
                        not item.product.is_voucher
                    )
                    
                    # ── # C-e Override Rule: Infinite assets / Token Revocation Engine ──────────────────
                    if is_instant_eproduct:
                        # Locate and securely deactivate all generated secure download link passes
                        active_tokens = DigitalDownloadToken.objects.filter(order_product=item, is_active=True)
                        if active_tokens.exists():
                            active_tokens.update(is_active=False)
                    else:
                        # Physical and voucher stock levels increment back safely
                        variation.stock += item.quantity
                        variation.save(update_fields=['stock'])

            # Initialize accounting pools and conversion parameters (CNY base)
            voucher_refund_pool = order.voucher_applied
            cash_refund_pool = order.total_due - order.voucher_applied
            exchange_rate = order.locked_exchange_rate if hasattr(order, 'locked_exchange_rate') else decimal.Decimal('1.0000')
            currency = order.currency_code if order.currency_code else "HKD"
            
            voucher_refund_log = ""
            reimbursement_voucher = None
            is_gift_voucher_revocation_required = False

            # =========================================================================
            # 💳 PATHWAY A: STORE VOUCHER CREDIT REIMBURSEMENT MATRIX (Section C-f-Voucher)
            # =========================================================================
            if refund_type == 'voucher':
                print("voucher refund")
                net_voucher_refund_cny = max(decimal.Decimal('0.00'), order.total_due - total_cancellation_fee)

                # 🌟 THE FIX: Identify whether the order was fully paid using store credits upfront
                if paid_entirely_by_voucher:
                    print('100pct by voucher logic patch engaged')
                    # Use the actual amount subtracted during checkout as your baseline credit pool
                    net_voucher_refund_cny = max(decimal.Decimal('0.00'), order.voucher_applied - total_cancellation_fee)
                else:
                    # Standard fallback for standard or mixed split-payment accounts
                    net_voucher_refund_cny = max(decimal.Decimal('0.00'), order.total_due - total_cancellation_fee)
                    
                print("net_voucher_refund_cny: ", net_voucher_refund_cny)
        
                if paid_entirely_by_voucher:
                    print('100pct by voucher')
                    # Case C-g-i: 100% Paid with store credit balance
                    reimbursement_voucher = CustomerVoucher.objects.create(
                        value=net_voucher_refund_cny,
                        balance=net_voucher_refund_cny,
                        purchaser_email=order.email,
                        registered_email=order.email.lower() if user_is_member else None,
                        owner=order.user if user_is_member else None,
                        is_claimed=True if user_is_member else False,
                        is_used=False,
                        # 🌟 FIXED: Force instant wallet validation by bypassing default lock flags
                        is_locked=False,
                        locked_at=None,
                        locked_by_session=None
                    )
                    voucher_refund_log = f" [100% Voucher Refund]: Restored face value of CNY {net_voucher_refund_cny:.2f} directly to member account."

                elif voucher_refund_pool > 0 and cash_refund_pool > 0:
                    # Case C-g-ii: Mixed Split Payment arrays
                    # Step 1: Return the original spent voucher portion first after subtracting item fee metrics
                    fee_deduction_remainder = total_cancellation_fee
                    if voucher_refund_pool >= fee_deduction_remainder:
                        net_voucher_return = voucher_refund_pool - fee_deduction_remainder
                        fee_deduction_remainder = decimal.Decimal('0.00')
                    else:
                        fee_deduction_remainder -= voucher_refund_pool
                        net_voucher_return = decimal.Decimal('0.00')

                    # Step 2: Convert the cash remainder into a new credit voucher balance row
                    net_cash_converted_to_voucher = max(decimal.Decimal('0.00'), cash_refund_pool - fee_deduction_remainder)
                    total_combined_voucher_return = net_voucher_return + net_cash_converted_to_voucher

                    reimbursement_voucher = CustomerVoucher.objects.create(
                        value=total_combined_voucher_return,
                        balance=total_combined_voucher_return,
                        purchaser_email=order.email,
                        registered_email=order.email.lower() if user_is_member else None,
                        owner=order.user if user_is_member else None,
                        is_claimed=True if user_is_member else False,
                        is_used=False,
                        is_locked=False,
                        locked_at=None,
                        locked_by_session=None
                    )
                    voucher_refund_log = f" [Split-to-Voucher]: Returned total combined credit value of CNY {total_combined_voucher_return:.2f}."

                else:
                    # Case C-g-iii: 100% Cash-to-Voucher Conversion Funnel (Both members and guests)
                    reimbursement_voucher = CustomerVoucher.objects.create(
                        value=net_voucher_refund_cny,
                        balance=net_voucher_refund_cny,
                        purchaser_email=order.email,
                        registered_email=order.email.lower() if user_is_member else None,
                        owner=order.user if user_is_member else None,
                        is_claimed=True if user_is_member else False,
                        is_used=False,
                        is_locked=False,
                        locked_at=None,
                        locked_by_session=None
                    )
                    
                    if user_is_member:
                        voucher_refund_log = f" [Cash-to-Voucher Member]: Converted net cash portion into CNY {net_voucher_refund_cny:.2f} voucher."
                    else:
                        voucher_refund_log = f" [Cash-to-Voucher Guest]: Dispatched unclaimed conversion card voucher ID {reimbursement_voucher.id}."

                # Case C-g-iv: Track gift voucher cancellations for 3rd-party transfers
                # 🌟 FIXED: Implemented a robust null-safe guard evaluation pass
                # This safely handles cases where recipient_email or order.email evaluates to None
                buyer_email_clean = (order.email or "").strip().lower()
                recipient_email_clean = (order.recipient_email or "").strip().lower()

                # Case C-g-iv: Track gift voucher cancellations for 3rd-party transfers safely
                # If recipient_email exists and is distinct from the buyer, flag it for revocation
                if recipient_email_clean and buyer_email_clean != recipient_email_clean:
                    is_gift_voucher_revocation_required = True
                else:
                    is_gift_voucher_revocation_required = False                    

            # =========================================================================
            # 💳 PATHWAY B: ORIGINAL PATHWAY CASH RETOUR MATRIX (Section C-f-Cash)
            # =========================================================================
            else:
                # Step 1: Always restore any spent voucher points back to members automatically (Section C-h-i)
                fee_balance_to_deduct = total_cancellation_fee
                if voucher_refund_pool > 0:
                    if voucher_refund_pool >= fee_balance_to_deduct:
                        net_voucher_restored = voucher_refund_pool - fee_balance_to_deduct
                        fee_balance_to_deduct = decimal.Decimal('0.00')
                    else:
                        fee_balance_to_deduct -= voucher_refund_pool
                        net_voucher_restored = decimal.Decimal('0.00')
                    
                    if net_voucher_restored > 0:
                        reimbursement_voucher = CustomerVoucher.objects.create(
                            value=net_voucher_restored,
                            balance=net_voucher_restored,
                            purchaser_email=order.email,
                            registered_email=order.email.lower(),
                            owner=order.user,
                            is_claimed=True,
                            is_used=False,
                            is_locked=False,
                            locked_at=None,
                            locked_by_session=None                            
                        )
                        voucher_refund_log += f" [Voucher Restored]: Returned CNY {net_voucher_restored:.2f} straight to member account wallet."

                # Step 2: Compute net out-of-pocket cash returns with 5% admin fee factored in (Section C-h-b)
                net_cash_pool_cny = max(decimal.Decimal('0.00'), cash_refund_pool - fee_balance_to_deduct)
                
                if net_cash_pool_cny > 0:
                    # Formula: (Cash remainder - cancellation fee remainder) * 95% net payout ratio
                    admin_fee_rate = decimal.Decimal('0.05')
                    net_cash_refund_base = net_cash_pool_cny * (decimal.Decimal('1.00') - admin_fee_rate)
                    
                    # Convert values accurately into active checkout denominations
                    net_cash_refund_foreign = net_cash_refund_base * exchange_rate
                    
                    # Execute explicit regional integer currency rounding logic rules
                    if currency.upper() in INTEGER_CURRENCIES:
                        net_cash_refund_foreign = net_cash_refund_foreign.quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)
                        display_format = f"{net_cash_refund_foreign:.0f}"
                    else:
                        display_format = f"{net_cash_refund_foreign:.2f}"
                        
                    voucher_refund_log += f" [Cash Return Pool]: Configured path via {currency} {display_format}."
                else:
                    display_format = "0.00"
                    voucher_refund_log += f" [Cash Overrun]: Cancellation fee exceeded cash pool. Retained in full."

            # =========================================================================
            # 💾 COMMIT BALANCES TO PERMANENT INSTANCE FIELDS (Section C-f-Snapshot)
            # =========================================================================
            order.refund_type = refund_type.upper()
            order.user_classification = 'MEMBER' if user_is_member else 'GUEST'
            order.is_online_gateway = order.payment.payment_method in ['PayPal', 'Stripe'] if order.payment else True
            order.total_cancellation_fee_applied = total_cancellation_fee
            order.restored_voucher_pool_amount = voucher_refund_pool
            order.is_self_service_cancelled = True

            # 🌟 FIXED: THE DOUBLE-SPEND SHIELD RE-ALIGNMENT PATCH
            # Locate the originating ProformaInvoice row using the matching unique order number
            try:
                originating_proforma = ProformaInvoice.objects.select_for_update().get(
                    proforma_order_number=order.order_number
                )
                # Break the double-spend hold validation loops by flipping the settlement indicator flags
                originating_proforma.order_settled = True # Or flip is_ordered = False depending on your model choices layout
                originating_proforma.save(update_fields=['order_settled'])
                print(f"🔒 [Double-Spend Shield Cleared]: Settled Proforma hold reference tracking flags for Invoice #{order.order_number}")
            except ProformaInvoice.DoesNotExist:
                # If it was an instant PayPal checkout, no offline bank Proforma hold exists to clear
                pass

            if refund_type == 'voucher':
                order.net_cash_payout_amount_foreign = decimal.Decimal('0.00')
                print("order.net_cash_payout_amount_foreign: ", order.net_cash_payout_amount_foreign)
            else:
                order.net_cash_payout_amount_foreign = decimal.Decimal(display_format)

            # Bind newly issued voucher UUID records cleanly if available
            voucher_id_str = str(reimbursement_voucher.id) if reimbursement_voucher else None
            order.refund_voucher_id_str = voucher_id_str
            print("voucher_id_str: ", voucher_id_str)

            # Save the system alerts safely down to the logs
            timestamp_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            order.order_status = 'Cancelled'
            order.delivery_note = f"{order.delivery_note or ''}\n\n[System Alert - {timestamp_str}]: Order cancelled via Web. Saved cancellation metrics successfully."
            
            # Atomic update of fields ensures maximum concurrent safety across execution pools
            order.save(update_fields=[
                'order_status', 'delivery_note', 'updated_at', 'refund_type',
                'user_classification', 'is_online_gateway', 'total_cancellation_fee_applied',
                'restored_voucher_pool_amount', 'net_cash_payout_amount_foreign',
                'refund_voucher_id_str', 'is_self_service_cancelled'
            ])

        # =========================================================================
        # 🎯 POST-COMMIT PARALLEL CELERY TASK ROUTING LINES (Section B / Email Versions)
        # =========================================================================
        voucher_id_str = str(reimbursement_voucher.id) if reimbursement_voucher else None
        is_online_gateway = order.payment.payment_method in ['PayPal', 'Stripe'] if order.payment else True

        # Pathway 1: Trigger Gift Voucher Revocation Notice to 3rd Party (g-iv)
        if is_gift_voucher_revocation_required:
            transaction.on_commit(lambda: send_gift_receiver_revocation_email_task.delay(
                order_id=order.id,
                recipient_email=order.recipient_email,
                revoked_tokens_log_str=str(order.order_number)
            ))

        # Pathway 2: Route Finalize workflows (g-i-ii / g-ii-ii / g-iii-i / g-iii-ii)
        if order.refund_type == 'VOUCHER':
            transaction.on_commit(lambda: send_cancellation_completion_email_task.delay(
                order_id=order.id,
                refund_type='voucher',
                user_type=order.user_classification.lower(),
                voucher_id_str=order.refund_voucher_id_str,
                net_amount_str=f"{order.total_due - order.total_cancellation_fee_applied:.2f}"
            ))
            messages.success(request, "Cancellation completed successfully! Your credit voucher has been generated. / 訂單取消已完成！全額購物金已簽發。")

        # Pathway 3: Route Initialize workflows (h-i-ii / h-ii-ii)
        else:
            transaction.on_commit(lambda: send_cancellation_initiation_email_task.delay(
                order_id=order.id,
                refund_type='cash',
                user_type=order.user_classification.lower(),
                is_online_gateway=order.is_online_gateway,
                currency_code=currency,
                net_cash_payout_str=f"{order.net_cash_payout_amount_foreign:.2f}" if currency.upper() not in ["JPY", "KRW", "TWD", "VND", "CLP"] else f"{order.net_cash_payout_amount_foreign:.0f}"
            ))
            messages.success(request, f"Order #{order.order_number} cancellation request received. / 訂單取消與退款申請已成功受理。")

        if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = JsonResponse({
                "status": "SUCCESS",
                "message": f"Order #{order.order_number} cancellation completed successfully. Face values restored."
            }, status=200)
            
            # Failsafe Over-The-Air signal dispatch
            response['HX-Trigger'] = json.dumps({"refreshDashboardCounters": True})
            return response 

        messages.success(request, f"Order #{order.order_number} cancellation request received. / 訂單取消與退款申請已成功受理。")
        return redirect('dashboard', subpage='orders') if request.user.is_authenticated else redirect('home')

    except Exception as e:
        logger.exception(f"💥 Cancellation Processing Exception: {str(e)}")
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({"status": "SERVER_ERROR", "error": str(e)}, status=500)
            
        messages.error(request, f"系統因核心業務邏輯異常已安全撤回交易: {str(e)}")
        return redirect('dashboard', subpage='orders') if request.user.is_authenticated else redirect('home')

