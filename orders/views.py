from django.shortcuts import render, redirect, get_object_or_404
from carts.models import ProformaInvoice
from carts.forms import ProformaInvoiceForm
from xindeng import settings
from accounts.data import COUNTRY_CODE, CURRENCY_SYMBOL, INTEGER_CURRENCIES
from .models import Payment, Order, OrderProduct
from django.db import transaction
from django.http import FileResponse
from .utils import generate_order_confirmation_pdf, format_accounting_currency, mark_off_perk_at_checkout
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.contrib.humanize.templatetags.humanize import intcomma
from decimal import Decimal
from accounts.models import UserProfile, Address
from store.models import ProductVariation
from django.http import HttpResponse
from django.core.exceptions import ValidationError
import json

# Import your explicit celery tasks directly
from .tasks import check_and_expire_hold, send_bank_hold_confirmation_email_task


def place_order(request, proforma_invoice_no):
    try:
        # Look up by number only, dropping the restrictive 'is_ordered=False' blocker
        proforma_invoice = get_object_or_404(ProformaInvoice, proforma_order_number=proforma_invoice_no)
        
        # Safeguard: Bounces them to receipt if already finalized
        if proforma_invoice.is_ordered:
            return redirect(f"/orders/order_complete/?order_number={proforma_invoice_no}&method=bank")

        cart_items = proforma_invoice.cart.cartitem_set.all() if proforma_invoice.cart else []

        # Resolve currency mapping patterns matching earlier view setups
        foreign_currency_code = request.COOKIES.get('user_currency') or request.session.get('user_currency', 'HKD')
        country_code = COUNTRY_CODE.get(foreign_currency_code, 'HK')
        is_integer = True if foreign_currency_code in INTEGER_CURRENCIES else False

        # 🎯 TRACK COHESIVE RECIPIENT ACCURACY BOUNDARIES
        # If display_mode is digital, or if name values are missing, explicitly flag it False
        has_recipient_info = False
        if proforma_invoice.recipient_first_name and proforma_invoice.recipient_last_name:
            # Prevent string expressions of 'None' from slipping into the template variables
            if proforma_invoice.recipient_first_name.strip() != "None" and proforma_invoice.recipient_last_name.strip() != "None":
                has_recipient_info = True
        # -------------------------------------------------------------
        # 🔥 HANDLE BANK TRANSFER SUBMISSIONS DIRECTLY VIA NATIVE HTML/HTMX
        # -------------------------------------------------------------
        if request.method == "POST":
            action_method = request.POST.get("payment_method")
            
            if action_method == "BANK_TRANSFER":
                # expiry_time = timezone.now() + timedelta(hours=72)
                expiry_time = timezone.now() + timedelta(minutes=5)
                # expiry_time = timezone.now() + timedelta(seconds=30)

                try:
                    with transaction.atomic():
                        invoice = ProformaInvoice.objects.select_for_update().get(pk=proforma_invoice.pk)

                        if invoice.is_ordered:
                            return redirect(f"/orders/order_complete/?order_number={proforma_invoice_no}&method=bank")
                            
                        for item in cart_items:
                            variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                            
                            if variation.stock < item.quantity:
                                    out_of_stock_payload = {
                                        "title": "庫存不足 ｜ Out of Stock Alert",
                                        "text": f"抱歉，商品 [{variation}] 僅剩 {variation.stock} 件可用庫存，無法完成鎖定。<br>Sorry, [{variation}] only has {variation.stock} units remaining.",
                                        "redirect_url": "/carts/cart/"
                                    }
                                    
                                    # 💡 FIX: Return 200 OK to satisfy the browser network console log filters.
                                    # HX-Reswap: none tells HTMX explicitly to NOT touch, blink, or replace any page markup.
                                    response = HttpResponse("&nbsp;", content_type="text/html", status=200)
                                    response["HX-Reswap"] = "none"
                                    response["HX-Trigger"] = json.dumps({
                                        "errorMssg": out_of_stock_payload
                                    })
                                    return response
                            
                        # 🎯 ATOMIC COUPON MARK-OFF EXECUTION
                        offer_session = request.session.get("offer_applied", {})
                        offer_code = offer_session.get("offer_code")
                        
                        if offer_code:
                            try:
                                # This will raise a ValidationError if coupon checks fail
                                mark_off_perk_at_checkout(request.user, offer_code)
                            except ValidationError as perk_err:
                                # Intercept and pass cleanly to your front-end SWAL handler
                                response = HttpResponse("&nbsp;", content_type="text/html", status=200)
                                response["HX-Reswap"] = "none"
                                response["HX-Trigger"] = json.dumps({
                                    "errorMssg": {
                                        "title": "優惠校驗失敗 ｜ Offer Verification Failed",
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
                                
                                "is_ordered": True,
                                "order_status": "New"
                            }
                        )

                        # 3. Process inventory deductions and create permanent OrderProduct snapshots
                        for item in cart_items:
                            variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                            
                            # Deduct warehouse stock
                            variation.stock -= item.quantity
                            variation.save()
                            
                            # Save line item snapshot record attached to Order
                            OrderProduct.objects.create(
                                order=order,
                                user=invoice.user,
                                product=variation.product,
                                product_variation=variation,
                                quantity=item.quantity,
                                product_price=variation.price,
                                ordered=True
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

                    # 🔥 Trigger background processing safely outside atomic transaction lock block
                    transaction.on_commit(lambda: send_bank_hold_confirmation_email_task.delay(order.id))
                    transaction.on_commit(lambda: check_and_expire_hold.apply_async((order.id,), eta=expiry_time))
                    
                    if request.headers.get("HX-Request"):
                        response = HttpResponse("", status=200)
                        location_payload = {
                            "path": f"/orders/order_complete/?order_number={invoice.proforma_order_number}&method=bank",
                            "target": "body",      # Forces evaluation across the entire body layout
                            "swap": "innerHTML"    # Clean slate replacement tracking configuration
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
            "page_title": f"支付訂單號 | Pay Order {proforma_invoice_no}",
            "main_title": "支 付 訂 單 ｜ Place Order",
            "sub_title_1": "迎接寶貝 ｜ Complete Purchase",
            "bread_crumb_1": "首頁",
            "bread_crumb_2": "訂單支付",
            "bread_crumb_1_url": "/",
            "bread_crumb_2_url": request.path,
            
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
            "proforma_invoice_number": proforma_invoice.proforma_order_number,
            "is_integer": is_integer,
            "country_code": country_code,

            "display_mode": proforma_invoice.display_mode,
            "has_recipient_info": has_recipient_info,
        }

        print("display_mode: ", proforma_invoice.display_mode)
        print("has_recipient_info: ", has_recipient_info)
        return render(request, 'orders/place_order.html', context)
    
    except ProformaInvoice.DoesNotExist:
        return redirect('cart')


def order_complete(request):
    order_number = request.GET.get("order_number")
    transaction_id = request.GET.get("transaction_id")
    
    if not order_number:
        return redirect("home")

    # 1. Fetch the absolute baseline Invoice data
    proforma_invoice = get_object_or_404(ProformaInvoice, proforma_order_number=order_number, is_ordered=True)
    order = None
    ordered_products = []
    payment = None
    is_bank_transfer = (proforma_invoice.payment_method == "BANK_TRANSFER")

    # 2. Extract user configurations strictly from COOKIES lookup layers
    foreign_currency_code = request.COOKIES.get('user_currency', 'HKD')
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, f"{foreign_currency_code} ")
    is_integer = True if foreign_currency_code in INTEGER_CURRENCIES else False
    cny_symbol = '¥'

    # -----------------------------------------------------------------
    # OPTION A: Asynchronous 72-Hour Bank Transfer / Manual WeChat Hold
    # -----------------------------------------------------------------
    if is_bank_transfer:
        main_title = "Order Hold Confirmed ｜ 訂單保留中"
        sub_title_1 = "Please complete transfer within 72 hours. ｜ 請於72小時內完成付款以保留商品庫存。"
        
        # Read from un-deleted active cart via related set lookup engine
        cart_items = proforma_invoice.cart.cartitem_set.all() if proforma_invoice.cart else []
        for item in cart_items:
            ordered_products.append({
                'product_variation': item.product_variation,
                'quantity': item.quantity,
                'formatted_price': format_accounting_currency(item.product_variation.price, cny_symbol, False),
                'formatted_subtotal': format_accounting_currency(item.subtotal, cny_symbol, False)
            })
           
        # For Bank Transfer, pull base values directly from the Proforma Invoice
        base_product_total = proforma_invoice.cart_total
        base_shipping_cost = proforma_invoice.shipping_cost
        base_discount = proforma_invoice.discount
        base_voucher = proforma_invoice.voucher_applied
        base_total_due = proforma_invoice.total_due

        # 🎯 THE FIX: Atomically flush the shopping basket rows right after extraction
        if proforma_invoice.cart:
            with transaction.atomic():
                proforma_invoice.cart.cartitem_set.all().delete()

    # -----------------------------------------------------------------
    # OPTION B: Instant PayPal Checkout Execution
    # -----------------------------------------------------------------
    else:
        main_title = "Payment Complete | 訂單完成"
        sub_title_1 = "Thank You for Your Support! ｜ 感謝您對我們的支持！"
        
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
            cart_items = proforma_invoice.cart.cartitem_set.all()
            for item in cart_items:
                ordered_products.append({
                    'product_variation': item.product_variation,
                    'quantity': item.quantity,
                    'formatted_price': format_accounting_currency(item.product_variation.price, cny_symbol, False),
                    'formatted_subtotal': format_accounting_currency(item.subtotal, cny_symbol, False)
                })
            main_title = "Order Processing | 訂單處理中"
            sub_title_1 = "We are verifying your transaction message. ｜ 我們正在處理並核對您的支付訊息。"
            
            base_product_total = proforma_invoice.cart_total
            base_shipping_cost = proforma_invoice.shipping_cost
            base_discount = proforma_invoice.discount
            base_voucher = proforma_invoice.voucher_applied
            base_total_due = proforma_invoice.total_due

    # =============================================================
    # 📉 THE SUCCESS SCREEN BACKWARD-BALANCED LEDGER (CRITICAL)
    # =============================================================
    # Select our ground-truth row reference based on the active payment mode
    target_source = order if order else proforma_invoice

    # 1. Cast DB snapshot attributes back to true numeric Decimals to clear binary float drift
    if order:
        raw_db_shipping_fx = Decimal(str(target_source.shipping_cost_foreign))
        raw_db_discount_fx = Decimal(str(target_source.discount_foreign))
        raw_db_voucher_fx = Decimal(str(target_source.voucher_applied_foreign))
    else:
        raw_db_shipping_fx = Decimal(str(target_source.shipping_cost_amount_foreign))
        raw_db_discount_fx = Decimal(str(target_source.discount_amount_foreign))
        raw_db_voucher_fx = Decimal(str(target_source.applied_voucher_amount_foreign))

    raw_db_payable_fx = Decimal(str(target_source.total_due_foreign))
    raw_db_subtotal_fx = raw_db_payable_fx + raw_db_discount_fx + raw_db_voucher_fx - raw_db_shipping_fx

    # 3. Compile structural multi-currency visual parameters
    context = {
        "main_title": main_title,
        "sub_title_1": sub_title_1,
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
        
        # Base CNY values formatted uniformly with full decimal layouts
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

    # 4. Clear temporary session configurations safely post-render 
    if 'offer_applied' in request.session or 'applied_voucher' in request.session:
        request.session.pop("offer_applied", None)
        request.session.pop("applied_voucher", None)
        request.session.modified = True

    return render(request, "orders/order_complete.html", context)


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
