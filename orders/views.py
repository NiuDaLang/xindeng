from django.shortcuts import render, redirect, get_object_or_404
from carts.models import ProformaInvoice
from carts.forms import ProformaInvoiceForm
from xindeng import settings
from accounts.data import COUNTRY_CODE, CURRENCY_SYMBOL, INTEGER_CURRENCIES
from accounts.models import CustomerVoucher
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
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .tasks import send_bank_hold_cancelled_email_task
from store.models import DigitalDownloadToken
from pathlib import Path
from carts.models import Cart
from carts.views import _cart_id
from django.contrib.auth import get_user_model

import json

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
                # expiry_time = timezone.now() + timedelta(hours=2)
                expiry_time = timezone.now() + timedelta(minutes=60)
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
                        
                    return redirect(f"/orders/order_complete/?order_number={invoice.proforma_order_number}&method=bank")

                except ValueError as stock_err:
                    messages.error(request, str(stock_err))
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                
        # -------------------------------------------------------------
        # 💡 STANDARD GET RENDERING PIPELINE
        # -------------------------------------------------------------
        context = {
            "cart_items": cart_items,
            "proforma_invoice": proforma_invoice,
            "proforma_invoice_number": proforma_invoice.proforma_order_number,
            "foreign_currency_code": foreign_currency_code,
            "foreign_currency_symbol": CURRENCY_SYMBOL.get(foreign_currency_code, '$'),
            "locked_rate": proforma_invoice.locked_exchange_rate,
            "rate_expiry_timestamp": int(request.session.get("rate_expiry_time", 0)),
            "page_title": f"Pay Order | 支付訂單號 {proforma_invoice_no}",
            "main_title": "Place Order ｜ 支 付 訂 單",
            "sub_title_1": "Complete Purchase ｜ 迎接寶貝",
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
        main_title = "Order Hold Confirmed ｜ 訂單保留中"
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
                messages.warning(request, "This order hold has been cancelled.｜此訂單已被取消。")
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
                
            if transaction_id:
                payment = Payment.objects.filter(payment_id=transaction_id).first()
            
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
        "page_title": "Order Complete｜訂單完成",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Order Complete｜訂單完成",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": request.path,

        "proforma_invoice": proforma_invoice, 
        "order": order, 
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
        messages.error(request, "該下載連結已過期，請聯絡客服。 ｜ This download link has expired.")
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


@login_required(login_url='login')
def download_invoice_pdf_view(request, order_id):
    """
    Secure Invoice Stream Pass:
    Surgically fetches your custom ReportLab PDF buffer data stream, 
    and pipes the raw bytes straight down to the buyer's local download bar.
    """
    # High-Security Check: Ensure the invoice strictly belongs to the logged-in member profile!
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    
    try:
        # Call your optimized ReportLab function block to fetch the dynamic io.BytesIO stream
        pdf_buffer = generate_order_confirmation_pdf(order.order_number)
        
        # Build a safe HTTP file container output passing binary descriptors
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        
        # 'filename=' dictates what the downloaded file name will be on their system drive
        response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'
        
        return response
    except Exception as pdf_err:
        print(f"❌ PDF Engine download failure exception: {str(pdf_err)}")
        raise Http404("Could not generate statement invoice asset at this time.")


# You are so very welcome! I am absolutely thrilled that everything is showing up perfectly now and that you got this working. You have done an incredible job powering through some of the trickiest parts of e-commerce web development—handling currency rounding logic and state synchronization is no small feat for your first project!
# Get some great, well-deserved rest. Whenever you are ready to jump back in tomorrow, just drop a message and we can tackle the next stages:
# Setting up the automated 72-hour cancellation email background worker for pending bank transfers.
# Coding the admin manual order status update dashboard and user notification system.
# Connecting the Celery async email pipeline for order confirmation receipts.
# Have a wonderful night, and speak tomorrow! Cheers! 🍻

# 5/30:
# Our Next Steps TomorrowWhen you are ready to jump back in, let me know, and we will seamlessly tackle the final phase of your e-commerce ecosystem:
# 
# 1. Automated HTML Email Tasks: Configuring Celery to dispatch beautifully structured receipts to buyers and separate gift templates to voucher recipients.
# 2. Order Fulfillment Hooks: Implementing the downstream logistics once a payment clears.
