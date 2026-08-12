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
from store.models import ProductVariation
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .tasks import send_bank_hold_cancelled_email_task, send_inquiry_notification_email_task, send_cancellation_initiation_email_task
from store.models import DigitalDownloadToken
from pathlib import Path
from carts.models import Cart
from carts.views import _cart_id
from django.contrib.auth import get_user_model
from .models import OrderInquiry

import json
import decimal

# Import your explicit celery tasks directly
from .tasks import check_and_expire_hold, send_bank_hold_confirmation_email_task


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
                                "order_status": "New"
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
                            
                            # Perform structural stock clearance check
                            if variation.stock < item.quantity:
                                raise ValueError(f"商品 [{variation}] 庫存不足")

                            # Deduct warehouse stock
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
                                ordered=False
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
        has_self_voucher = order.orderproduct_set.filter(
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
def secure_file_download_gate(request, token_id):
    """
    Time-Locked Data Stream Matrix:
    Authenticates tokens, prevents direct hotlinking, and streams files 
    privately from secure local disk storage.
    """
    token = get_object_or_404(DigitalDownloadToken, id=token_id, user=request.user)

    if token.is_expired:
        # Redirect back to their digital wallet or dashboard with a helpful error message
        from django.contrib import messages
        messages.error(request, "This download link has expired.｜該下載連結已過期，請聯絡客服。")
        return redirect('dashboard', subpage='orders')

    # Resolve file system coordinates securely
    variation = token.variation
    if not variation.digital_file_path:
        raise Http404("Asset target record missing.")

    # Secure root vault assignment path
    vault_base_path = Path(settings.BASE_DIR) / 'private_digital_vault'
    target_file = (vault_base_path / variation.digital_file_path).resolve()

    # Security Guard Pass: Prevent directory traversal exploits
    if not target_file.is_file() or not target_file.startswith(str(vault_base_path)):
        raise Http404("File execution lookup failed.")

    # 🚀 SECURELY STREAM FILE BINARY DIRECTLY TO THEIR BROWSER
    # 'as_attachment=True' forces the browser to download the file instead of viewing it inline
    response = FileResponse(open(target_file, 'rb'), as_attachment=True, filename=target_file.name)
    
    # Optional: Set token to inactive after use to enforce a single-download rule,
    # though leaving it active for the full 48 hours is much friendlier for your customers!
    return response


# @login_required
# @require_POST
# def cancel_order(request, order_id):
#     """
#     Allows a user to manually cancel their active bank hold order early.
#     Replenishes inventory, releases the proforma invoice, and updates HTML via HTMX.
#     """
#     try:
#         with transaction.atomic():
#             # Restrict lookup to the authenticated user and ensure it's still an active hold
#             order = Order.objects.select_for_update().get(id=order_id, user=request.user, is_ordered=False)
            
#             if order.order_status == 'Cancelled':
#                 return HttpResponse("Order already cancelled.", status=400)

#             # 1. Replenish database stock values back onto ProductVariations
#             order_items = OrderProduct.objects.filter(order=order)
#             for item in order_items:
#                 if item.product_variation:
#                     variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
#                     variation.stock += item.quantity
#                     variation.save()

#             # 2. Revert Coupon/Voucher rules if applicable
#             if order.voucher_applied > 0:
#                 CustomerVoucher.objects.create(
#                     value=order.voucher_applied,
#                     balance=order.voucher_applied,
#                     owner=order.user,
#                     purchaser_email=order.email or "user-cancellation@domain.com",
#                     registered_email=order.user.email,
#                     is_claimed=True,
#                     claimed_date=timezone.now(),
#                     is_used=False
#                 )

#             # 3. Change status states
#             order.order_status = 'Cancelled'
#             order.save(update_fields=['order_status'])
            
#             # Unlock original Proforma Invoice profile
#             ProformaInvoice.objects.filter(proforma_order_number=order.order_number).update(is_ordered=False)

#         # Return a completely blank response to cause HTMX to swap out/remove the cancelled card element
#         return HttpResponse("", status=200)

#     except Order.DoesNotExist:
#         return HttpResponse("Order target invalid or processing state locked.", status=404)

@login_required
@require_POST
def cancel_order(request, order_id):
    """Allows members to manually release a pending hold on their dashboard early via HTMX."""
    try:
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=order_id, user=request.user, is_ordered=False)
            
            if order.order_status == 'Cancelled':
                return HttpResponse("Order already cancelled.", status=400)

            # 1. Replenish database inventory pools
            order_items = OrderProduct.objects.filter(order=order)
            for item in order_items:
                if item.product_variation:
                    variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                    variation.stock += item.quantity
                    variation.save(update_fields=['stock'])

            # 2. Reverse voucher split allocations cleanly to their original rows
            if order.voucher_applied > 0:
                usages = OrderVoucherUsage.objects.filter(order=order)
                for usage in usages:
                    voucher = CustomerVoucher.objects.select_for_update().get(id=usage.voucher.id)
                    voucher.balance += usage.amount_deducted
                    if voucher.is_used:
                        voucher.is_used = False
                        voucher.used_date = None
                    voucher.save(update_fields=['balance', 'is_used', 'used_date'])

            reverse_perk_usage_at_cancellation(order)

            # 4. Apply state cancellation transitions
            order.order_status = 'Cancelled'
            order.save(update_fields=['order_status'])

            ProformaInvoice.objects.filter(proforma_order_number=order.order_number).update(is_ordered=False)

        # 4. Trigger alert email outside the database lock
        transaction.on_commit(lambda: send_bank_hold_cancelled_email_task.delay(order.id))
        return HttpResponse("", status=200) # Returns empty string to clear HTMX row entry

    except Order.DoesNotExist:
        return HttpResponse("Order invalid or locked.", status=404)


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


def process_order_cancellation(request, order_number):
    """
    🔒 UNIVERSAL LIFECYCLE CANCELLATION ENGINE
    Secures cancellation permissions across both authenticated members and verified guest sessions,
    evaluates dispatch compliance states, atomically restocks inventory, dynamically generates 
    reimbursement vouchers for used credits, and routes the order state to 'Refunding'.
    """
    # 1. Fetch the target transaction safely
    order = get_object_or_404(Order, order_number=order_number)
    
    # 2. DUAL-AUTHORIZATION GATEKEEPER PASS
    is_authorized = False
    
    # Context A: Request is initiated by a logged-in member who owns the transaction record
    if request.user.is_authenticated:
        if order.user == request.user:
            is_authorized = True
            
    # Context B: Request is initiated by an unauthenticated guest user verified by session keys
    else:
        session_order_num = request.session.get('verified_guest_order')
        session_email = request.session.get('verified_guest_email')
        if session_order_num == order.order_number and session_email and session_email.lower() == order.email.lower():
            is_authorized = True

    # Access Denied Fallback Guard
    if not is_authorized:
        raise PermissionDenied("Unauthorized cancellation vector attempt. / 安全攔截：您無權取消此訂單。")

    # 3. MARKET-STANDARD COMPLIANCE EVALUATION
    # Block automated cancellations if the warehouse has already logged outbound items
    has_dispatched_items = order.orderproduct_set.filter(is_dispatched=True).exists()
    
    # Block automated cancellations if the order contains instantly fulfilled digital items/vouchers
    has_immutable_digital = order.orderproduct_set.filter(
        product_variation__product__is_voucher=True
    ).exists() or order.orderproduct_set.filter(
        product_variation__product__is_digital=True,
        product_variation__product__digital_fulfillment_type='INSTANT'
    ).exists()

    if order.order_status in ['Delivered', 'Cancelled', 'All_Dispatched', 'Partly_Dispatched', 'Refunding', 'Refunded'] or has_dispatched_items or has_immutable_digital:
        messages.error(request, "This order contains items that cannot be modified automatically. Please contact support. / 此訂單內含已發貨或不可取消之商品，請聯絡客服協助。")
        if request.user.is_authenticated:
            return redirect('dashboard_orders')
        return redirect('guest_order_verify')
    
    paid_entirely_by_voucher = (order.total_due <= 0 and order.voucher_applied > 0)
    refund_type = 'voucher' if paid_entirely_by_voucher else request.GET.get('refund_type', 'cash')
    user_is_member = order.user is not None

    # 4. ATOMIC EXECUTION, STOCK ADJUSTMENT & VOUCHER CREDIT REIMBURSEMENT
    try:
        with transaction.atomic():
            # Shift state engine directly to Refunding queue line matrix parameters
            order.order_status = 'Refunding'
            order.updated_at = timezone.now()
            
             # 📦 1. Restock physical inventory item variations
            for item in order.orderproduct_set.all():
                if item.product_variation:
                    variation = item.product_variation
                    variation.stock += item.quantity
                    variation.save(update_fields=['stock'])
                    print(f"📦 INVENTORY RESTOCK SUCCESS: Returned {item.quantity} units to SKU {variation.get_sku()}｜庫存補貨成功：已將 {item.quantity} 件商品退回至 SKU {variation.get_sku()}")

            # 🎫 PIPELINE (ii): Auto-reimburse Applied Vouchers back to member profile credit vaults
            voucher_refund_log = ""
            reimbursement_voucher = None

            # ─────────────────────────────────────────────────────────
            # 🏢 PATHWAY A: THE 100% FULL VOUCHER PURCHASE EDGE CASE
            # ─────────────────────────────────────────────────────────
            if paid_entirely_by_voucher:
                refund_value = order.voucher_applied
                
                # If they were a guest when buying a voucher but are a member now, link it
                reimbursement_voucher = CustomerVoucher.objects.create(
                    value=refund_value,
                    balance=refund_value,
                    purchaser_email=order.email,
                    registered_email=order.user.email.lower() if user_is_member else None,
                    owner=order.user if user_is_member else None,
                    is_claimed=True if user_is_member else False,
                    claimed_date=timezone.now() if user_is_member else None,
                    is_used=False
                )
                voucher_refund_log = f" [100% Voucher Refund]: This transaction was paid entirely via store credits. Generated a 100% full replacement voucher of CNY {refund_value} (Token ID: {reimbursement_voucher.id}).｜[100% 抵用券退款]：本次交易全額使用商店信用額度支付。已產生面額為 CNY {refund_value} 的 100% 全額替換抵用券（憑證 ID：{reimbursement_voucher.id}）。"
                print(f"✨ 100% VOUCHER LIFECYCLE REVERTED: Token {reimbursement_voucher.id} restored with CNY {refund_value}")

            # ─────────────────────────────────────────────────────────
            # 💳 PATHWAY B: MIXED OR PURE CASH PURCHASES
            # ─────────────────────────────────────────────────────────
            else:
                # 🎫 Step 1: Always mandatory refund for any spent voucher portion first
                if user_is_member and order.voucher_applied and order.voucher_applied > 0:
                    spent_voucher_amount = order.voucher_applied
                    original_credit_voucher = CustomerVoucher.objects.create(
                        value=spent_voucher_amount,
                        balance=spent_voucher_amount,
                        purchaser_email=order.user.email,
                        registered_email=order.user.email.lower(),
                        owner=order.user,
                        is_claimed=True,
                        claimed_date=timezone.now(),
                        is_used=False
                    )
                    voucher_refund_log += f" [Original Credit Restored]: Reimbursed original spent credit portion of CNY {spent_voucher_amount} straight to member account wallet (Token ID: {original_credit_voucher.id}).｜[原額度已退回]：已將原先使用的 {spent_voucher_amount} 元額度直接退回至會員帳戶錢包（憑證 ID：{original_credit_voucher.id}）。"

                # ⚙️ Step 2: Handle the remaining out-of-pocket 'total_due' balance
                if refund_type == 'voucher':
                    # Return 100% of the cash remainder as a second voucher with zero fees
                    refund_value = order.total_due
                    
                    reimbursement_voucher = CustomerVoucher.objects.create(
                        value=refund_value,
                        balance=refund_value,
                        purchaser_email=order.email,
                        registered_email=order.email.lower() if user_is_member else None,
                        owner=order.user if user_is_member else None,
                        is_claimed=True if user_is_member else False,
                        claimed_date=timezone.now() if user_is_member else None,
                        is_used=False
                    )
                    
                    if user_is_member:
                        voucher_refund_log += f" [Remaining Balance]: Reimbursed 100% full remaining cash balance of CNY {refund_value} directly to account wallet ID {reimbursement_voucher.id}.｜[剩餘餘額]：將剩餘的全部現金餘額（人民幣 {refund_value}）全額退還至帳戶錢包 ID {reimbursement_voucher.id}。"
                    else:
                        # Explicitly calculate and display the exact date parameters inside your database logs
                        expiry_date_str = reimbursement_voucher.expiry_date.strftime('%Y-%m-%d')
                        voucher_refund_log += f" [Remaining Balance]: Generated unclaimed guest voucher ID {reimbursement_voucher.id} for full remaining balance of CNY {refund_value}. Expiry set to: {expiry_date_str}.｜[剩餘餘額]：針對 CNY {refund_value} 的全部剩餘餘額，產生了未領取的訪客憑證 ID {reimbursement_voucher.id}。有效期限設定為：{expiry_date_str}。"

                else:
                    # Deduct the 3% admin handling fee exclusively from the cash portion
                    fee_rate = decimal.Decimal('0.03')
                    net_cash_refund = order.total_due * (decimal.Decimal('1.0') - fee_rate)
                    voucher_refund_log += f" [Remaining Balance]: Processed cancellation net of a 3% administration handling fee deduction applied to the remaining gateway balance portion. Estimated payout return total: CNY {net_cash_refund:.2f}.｜[剩餘餘額]：已處理退款，並從支付網關的剩餘餘額中扣除了 3% 的行政手續費。預計退款總金額：CNY {net_cash_refund:.2f}。"

            # Save the system alerts safely down to the logs
            timestamp_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            current_notes = order.delivery_note or ""
            order.delivery_note = f"{current_notes}\n\n[System Alert - {timestamp_str}]: Order cancelled by purchaser. Refund Method chosen: {refund_type.upper()}.{voucher_refund_log}｜[系統提示 - {timestamp_str}]：訂單已被買家取消。選擇的退款方式：{refund_type.upper()}。 {voucher_refund_log}"
            order.save(update_fields=['order_status', 'delivery_note', 'updated_at'])

        # 🎯 4. Trigger Celery Task to process emails
        # Pass the primary reimbursement voucher token if it needs to be claimed via a registration link
        voucher_id_str = str(reimbursement_voucher.id) if (refund_type == 'voucher' and reimbursement_voucher) else None
        send_cancellation_initiation_email_task.delay(order.id, refund_type, voucher_id_str)

        messages.success(request, f"Order #{order.order_number} cancellation request received. / 訂單取消與退款申請已成功受理。")

    except Exception as cancel_err:
        print(f"❌ Transaction cancellation catastrophic rollback: {str(cancel_err)}")
        messages.error(request, "An internal error occurred during processing. Please try again. / 處理中發生系統異常，請稍後再試。")

    # 5. CONTEXT-AWARE SMART REDIRECT ENDPOINT ROUTER
    if request.user.is_authenticated:
        return redirect('dashboard', subpage='orders')
    return redirect('guest_order_verify')



# Can you write the cancellation complete function that can be operated from the database by admin staff? 
# Along with a message to be added into the Order so that the next time when 
# (a)  member logs in (b) guest user inquires via contact page's form, 
# the status of cancellation complete can be displayed clearly (in addition to the 'status' label). 

# Also, I think I need to send emails in (i) cancellation process begins, triggered by the cancel button activation, 
# and (ii) cancellation completes. For (a), I will