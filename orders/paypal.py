# paypal.py (Part 1 - Authentication and Item Breakdown Engines)
from django.http import JsonResponse
from django.db import transaction
import requests
import base64
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings
from decimal import Decimal, ROUND_HALF_UP
from accounts.data import INTEGER_CURRENCIES, CURRENCY_SYMBOL
from store.models import ProductVariation
from .tasks import send_order_confirmation_email_task
from django.db import models 
from accounts.models import CustomerVoucher

# Modern paypalserversdk v6 bindings
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.configuration import Environment
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.logging.configuration.api_logging_configuration import LoggingConfiguration, RequestLoggingConfiguration
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.amount_breakdown import AmountBreakdown
from paypalserversdk.models.order_application_context import OrderApplicationContext
from paypalserversdk.models.order_application_context_user_action import OrderApplicationContextUserAction
from paypalserversdk.api_helper import APIHelper
from paypalserversdk.models.money import Money

from carts.models import ProformaInvoice, CartItem
from .models import Order, Payment, OrderProduct
from .utils import get_paypal_items, fmt, mark_off_perk_at_checkout, execute_atomic_voucher_deduction

import json
import logging

logger = logging.getLogger(__name__)

CLIENT_ID = settings.PAYPAL_CLIENT_ID
CLIENT_SECRET = settings.PAYPAL_SECRET
PAYPAL_MODE = settings.PAYPAL_MODE

# Dynamic environment routing configuration
paypal_env = Environment.LIVE if PAYPAL_MODE == 'live' else Environment.SANDBOX

client = PaypalServersdkClient(
    client_credentials_auth_credentials = ClientCredentialsAuthCredentials(
        o_auth_client_id = CLIENT_ID,
        o_auth_client_secret = CLIENT_SECRET
    ),
    environment=paypal_env,
    logging_configuration=LoggingConfiguration(
        log_level=10, # DEBUG
        request_logging_config=RequestLoggingConfiguration(log_body=True)
    )
)

def get_paypal_client_token(request):
    """Generates a short-lived client token authorizing front-end checkout button bindings."""
    # 🎯 FIX: Direct the engine to the official API endpoints instead of the standard landing domain
    if PAYPAL_MODE == 'live':
        url = "https://api-m.paypal.com/v1/oauth2/token"
    else:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    
    payload = {
        "grant_type": "client_credentials", 
        "response_type": "client_token"
    }

    try:
        # Use Basic Authentication (Client ID & Client Secret) automatically encoded by requests
        response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), headers=headers, data=payload)
        
        # This will catch bad request statuses (400, 401, 500) before trying to decode JSON
        response.raise_for_status()
        
        return JsonResponse(response.json())
        
    except requests.exceptions.HTTPError as http_err:
        # Capture raw text if PayPal responds with API validation error strings
        print(f"PayPal HTTP Error: {http_err} | Response Content: {response.text}")
        return JsonResponse({"error": "PayPal authentication rejected.", "details": response.text}, status=response.status_code)
        
    except requests.exceptions.RequestException as e:
        print("PayPal Connection Error: ", e)
        return JsonResponse({"error": "Network connection error.", "details": str(e)}, status=500)


# paypal.py (Part 2 - Creation, Capture, and Callback Processors)
@require_POST
def create_paypal_order(request):
    """
    Builds the structural transaction request envelope. Absorbs integer 
    rounding variances surgically using PayPal's native handling fee block.
    """
    proforma_invoice_number = request.GET.get("invoice")

    try:
        # Wrap inventory check inside atomic block to read real-time stock levels
        with transaction.atomic():
            invoice = ProformaInvoice.objects.select_for_update().get(
                proforma_order_number=proforma_invoice_number, 
                is_ordered=False
            )
            cart_items = CartItem.objects.filter(cart=invoice.cart, is_active=True)
            
            # 🎯 ATOMIC SOURCE STOCK CHECK PASS
            for item in cart_items:
                variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                
                if variation.stock < item.quantity:
                    return JsonResponse({
                        "error_code": "OUT_OF_STOCK",
                        "title": "庫存不足 ｜ Out of Stock Alert",
                        "text": f"抱歉，商品 [{variation}] 僅剩 {variation.stock} 件可用庫存，無法完成鎖定。<br>Sorry, [{variation}] only has {variation.stock} units remaining.",
                        "redirect_url": "/carts/cart/"
                    }, status=400)


        user = request.user if request.user.is_authenticated else None
        foreign_currency_code = request.GET.get("foreign_currency_code", "HKD").upper().strip()
        locked_rate = request.GET.get("locked_rate")

        proforma_order = ProformaInvoice.objects.get(proforma_order_number=proforma_invoice_number, is_ordered=False)
        cart_items = CartItem.objects.filter(cart=proforma_order.cart)
        order = Order.objects.filter(order_number=proforma_invoice_number, is_ordered=False).first()
        
        is_int = foreign_currency_code in INTEGER_CURRENCIES
        exponent = Decimal('1') if is_int else Decimal('0.01')

        # 1. Fetch line items and extract precise decimal difference metrics
        items_breakdown = get_paypal_items(cart_items, foreign_currency_code, locked_rate, proforma_order.cart_total_foreign)
        items = items_breakdown["items_list"]
        rounding_variance = items_breakdown["rounding_adjustment"]  

        # 2. Map financial components safely using true numeric Decimals
        item_total = items_breakdown["amount_total_foreign"]
        shipping_cost = Decimal(str(proforma_order.shipping_cost_amount_foreign)).quantize(exponent, rounding=ROUND_HALF_UP)
        tax_total = Decimal(str(proforma_order.tax_amount_foreign)).quantize(exponent, rounding=ROUND_HALF_UP)
        
        d_foreign = Decimal(str(proforma_order.discount_amount_foreign))
        v_foreign = Decimal(str(proforma_order.applied_voucher_amount_foreign))
        discount_total = (d_foreign + v_foreign).quantize(exponent, rounding=ROUND_HALF_UP)

        # 3. ABSORB DEVIATIONS SURGICALLY (Never pass a negative value to PayPal)
        handling_cost = Decimal('0.00')

        if rounding_variance > Decimal('0.00'):
            # Positives increase the total; allocate safely to handling
            handling_cost = rounding_variance.quantize(exponent, rounding=ROUND_HALF_UP)
        elif rounding_variance < Decimal('0.00'):
            # Negatives decrease the total; add the positive absolute amount into the discount pile
            discount_total += abs(rounding_variance).quantize(exponent, rounding=ROUND_HALF_UP)

        # Calculate final clean absolute grand payable amount
        total_value = (item_total + shipping_cost + handling_cost + tax_total) - discount_total

        # 🚨 MASTER SAFEGUARD BALANCE ENFORCEMENT:
        # Securely double-verify that total_value matches proforma_order.total_due_foreign perfectly.
        target_due_foreign = Decimal(str(proforma_order.total_due_foreign)).quantize(exponent, rounding=ROUND_HALF_UP)
        
        if total_value != target_due_foreign:
            drift = target_due_foreign - total_value
            if drift > Decimal('0.00'):
                handling_cost += drift
            else:
                discount_total += abs(drift)
            # Recalculate definitive balanced aggregate
            total_value = (item_total + shipping_cost + handling_cost + tax_total) - discount_total

        # Format values strictly matching currency configuration metrics
        fmt_item_total = fmt(item_total, integer=is_int)
        fmt_shipping = fmt(shipping_cost, integer=is_int)
        fmt_discount = fmt(discount_total, integer=is_int)
        fmt_tax = fmt(tax_total, integer=is_int)
        fmt_handling = fmt(handling_cost, integer=is_int)
        fmt_total_value = fmt(total_value, integer=is_int)
        fmt_zero = "0" if is_int else "0.00"

        # Safe client IP compilation across reverse proxies
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
        print("paypal 1")
        if order is None:
            # Dynamic recipient name fallback strategy shielding digital checkouts from empty parameters
            r_first = proforma_order.recipient_first_name
            r_last = proforma_order.recipient_last_name
            if not r_first or not r_last:
                if user and user.first_name:
                    r_first = user.first_name
                    r_last = user.last_name if user.last_name else "Customer"
                else:
                    email_handle = proforma_order.email.split('@')[0] if proforma_order.email else "Guest"
                    r_first = email_handle
                    r_last = "Buyer"

            order = Order.objects.create(
                user=user, order_number=proforma_invoice_number, email=proforma_order.email,
                recipient_first_name=r_first, recipient_last_name=r_last,
                recipient_mobile_area=proforma_order.recipient_mobile_area if proforma_order.recipient_mobile_area else "",
                recipient_mobile_number=proforma_order.recipient_mobile_number if proforma_order.recipient_mobile_number else "",
                address_line_1=proforma_order.address_line_1, address_line_2=proforma_order.address_line_2,
                city=proforma_order.city, state_province_region=proforma_order.state_province_region,
                country=proforma_order.country if proforma_order.country else "XX", postal_code=proforma_order.postal_code,
                delivery_note=proforma_order.delivery_note, do_not_send_invoice=proforma_order.do_not_send_invoice,
                product_total=proforma_order.cart_total, shipping_cost=proforma_order.shipping_cost,
                discount=proforma_order.discount, tax=proforma_order.tax, voucher_applied=proforma_order.voucher_applied,
                total_due=proforma_order.total_due, product_total_foreign=proforma_order.cart_total_foreign,
                shipping_cost_foreign=proforma_order.shipping_cost_amount_foreign, discount_foreign=proforma_order.discount_amount_foreign,        
                tax_foreign=proforma_order.tax_amount_foreign, voucher_applied_foreign=proforma_order.applied_voucher_amount_foreign,  
                total_due_foreign=proforma_order.total_due_foreign, locked_exchange_rate=proforma_order.locked_exchange_rate,
                ip=ip, is_ordered=False, order_status="New"
            )

        # 4. Construct modern SDK Request payload objects explicitly
        amount_breakdown = AmountBreakdown(
            item_total=Money(currency_code=foreign_currency_code, value=fmt_item_total),
            shipping=Money(currency_code=foreign_currency_code, value=fmt_shipping),
            handling=Money(currency_code=foreign_currency_code, value=fmt_handling),
            tax_total=Money(currency_code=foreign_currency_code, value=fmt_tax),
            discount=Money(currency_code=foreign_currency_code, value=fmt_discount),
            insurance=Money(currency_code=foreign_currency_code, value=fmt_zero),
            shipping_discount=Money(currency_code=foreign_currency_code, value=fmt_zero)
        )
        print("paypal 2")

        purchase_unit = PurchaseUnitRequest(
            reference_id=str(proforma_order.proforma_order_number),
            amount=AmountWithBreakdown(currency_code=foreign_currency_code, value=fmt_total_value, breakdown=amount_breakdown),
            items=items
        )
        print("paypal 3")

        order_request = OrderRequest(
            intent=CheckoutPaymentIntent.CAPTURE,
            purchase_units=[purchase_unit],
            application_context=OrderApplicationContext(
                brand_name="Hṛdayadīpa ｜ 心燈",
                user_action=OrderApplicationContextUserAction.PAY_NOW,
                return_url=request.build_absolute_uri(f"/orders/order_complete/?order_number={proforma_order.proforma_order_number}"),
                cancel_url=request.build_absolute_uri("/carts/cart/")
            )
        )
        print("paypal 4")
        
        # 🎯 FIX: Wrap the OrderRequest wrapper inside a positional configuration dictionary 
        orders_controller = client.orders  
        print("paypal 5")
        
        api_response = orders_controller.create_order({
            "body": order_request
        })
        print("paypal 6")
        
        # 🎯 FIX: Parse the resulting data stream utilizing the official SDK serialization utility
        if api_response.status_code in [200, 201]:
            # Deserialize the native SDK body string safely into a clean JSON structure
            serialized_body = APIHelper.json_serialize(api_response.body)
            result_json = json.loads(serialized_body)
            
            print(f"PayPal Transaction Initialized Successfully! ID: {result_json.get('id')}")
            return JsonResponse({"id": result_json.get("id")}, status=200)
        else:
            print(f"PayPal API Error Status: {api_response.status_code} | Body: {api_response.body}")
            return JsonResponse({"error": "PayPal rejected order configuration parameters."}, status=400)

    except ProformaInvoice.DoesNotExist:
        print("proforma invoice doesn't exist")
        return JsonResponse({"error": "Invoice profile target invalid"}, status=404)
    except Exception as e:
        print(f"PayPal Order Generation Failure: {str(e)}")
        return JsonResponse({"error": f"Internal stock evaluation failure: {str(e)}"}, status=400)


@require_POST
def capture_paypal_order(request):
    """
    Executes remote capture validations using orders_controller.capture_order().
    Locks rows atomically to execute sold variation inventory adjustments safely.
    """
    paypal_order_id = request.GET.get("paypal_order_id")
    proforma_invoice_number = request.GET.get("invoice") 
    
    # 🎯 SDK v6 Namespace Mapping Alignment
    orders_controller = client.orders
    
    try:
        # Pass a single dictionary with "id" as a positional parameter
        capture_response = orders_controller.capture_order({
            "id": paypal_order_id
        })
        
        # Verify status code limits on the network instance wrapper
        if 200 <= capture_response.status_code <= 299:
            # Safely deserialize the typed model object using official ApiHelper
            json_data = APIHelper.json_serialize(capture_response.body)
            capture_res_data = json.loads(json_data)
            
            purchase_unit = capture_res_data['purchase_units'][0]
            capture_object = purchase_unit['payments']['captures'][0]
            
            transaction_id = capture_object['id']
            payment_status = capture_object['status'] 
            
            fx_amount_paid = Decimal(str(capture_object["amount"]["value"]))
            fx_currency_code = capture_object["amount"]["currency_code"].upper().strip()
            
            try:
                # Open blocking transaction context boundary to isolate thread allocations safely
                with transaction.atomic():
                    proforma_order = get_object_or_404(
                        ProformaInvoice.objects.select_for_update(), 
                        proforma_order_number=proforma_invoice_number, 
                        is_ordered=False
                    )
                    order = get_object_or_404(
                        Order.objects.select_for_update(), 
                        order_number=proforma_invoice_number, 
                        is_ordered=False
                    )
                    
                    cart_items = CartItem.objects.filter(cart=proforma_order.cart, is_active=True)
                    
                    # 🎯 FINAL LAST-SECOND RACE CONDITION PROTECTION BLOCK
                    for item in cart_items:
                        variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                        
                        if variation.stock < item.quantity:
                            # Roll back the transaction if a race condition occurred
                            raise ValueError(f"Race condition stock failure caught for {variation}")

                    # 🎯 ATOMIC COUPON MARK-OFF EXECUTION
                    offer_session = request.session.get("offer_applied", {})
                    offer_code = offer_session.get("offer_code")
                    
                    if offer_code:
                        # This automatically locks row values, checks eligibility, and increments counters safely
                        mark_off_perk_at_checkout(request.user, offer_code)

                    # 🎯 3. ATOMIC CASH VOUCHER BALANCE DEDUCTION ENGINE (Using Vouchers)
                    # If the user used their own voucher balance to offset this order's total cost
                    voucher_session = request.session.get("applied_voucher", {})
                    voucher_amount_str = voucher_session.get("applied_voucher_amount", "0")
                    voucher_to_spend = Decimal(voucher_amount_str)

                    if voucher_to_spend > 0:
                        # This row-locks customer voucher assets and subtracts the balance atomically
                        execute_atomic_voucher_deduction(request.user, voucher_to_spend)   

                    # Create permanent Payment entry storing explicit authorized configurations
                    payment = Payment.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        invoice=proforma_order, 
                        order_id=capture_res_data["id"], 
                        payment_id=transaction_id,
                        payer_id=capture_res_data.get("payer", {}).get("payer_id"), 
                        payment_method='PayPal',
                        amount_paid=fx_amount_paid, 
                        currency=fx_currency_code,
                        exchange_rate=proforma_order.locked_exchange_rate, 
                        cny_equivalent=order.total_due,
                        status="Completed" if payment_status == "COMPLETED" else "Pending"
                    )
                    
                    order.payment = payment
                    order.is_ordered = True
                    order.order_status = "New" 
                    order.save()
                    
                    # Relocate items securely over to structural OrderProduct tables
                    for item in cart_items:
                        # Re-fetching using select_for_update keeps rows safely isolated
                        variation = ProductVariation.objects.select_for_update().get(id=item.product_variation.id)
                        
                        OrderProduct.objects.create(
                            order=order, 
                            payment=payment, 
                            user=request.user if request.user.is_authenticated else None,
                            product=variation.product, 
                            product_variation=variation,
                            quantity=item.quantity, 
                            product_price=variation.price, 
                            ordered=True
                        )
                        
                        # 💡 FIXED: Only deduct stock once. The double-deduction line has been removed.
                        variation.stock -= item.quantity
                        variation.save()   

                        # 🎯 4. ATOMIC CASH VOUCHER GENERATION ENGINE (Purchasing Vouchers)
                        # If the customer is explicitly buying a gift voucher item, generate its instances [1]
                        if variation.product.is_voucher:
                            # Generate an independent CustomerVoucher instance for EACH quantity units purchased
                            for _ in range(item.quantity):
                                CustomerVoucher.objects.create(
                                    value=variation.price,
                                    balance=variation.price,
                                    owner=None, # Leaves blank until a user manually hits your claim link mapping layer [1]
                                    purchaser_email=order.email if order.email else proforma_order.email,
                                    registered_email=None,
                                    is_claimed=False,
                                    is_used=False
                                )
                    
                    proforma_order.is_ordered = True
                    proforma_order.save()
                    
                    # Clear active shopping cart contents
                    proforma_order.cart.cartitem_set.all().delete()
                
                # Safe asynchronous worker email dispatch execution 
                transaction.on_commit(lambda: send_order_confirmation_email_task.delay(order.order_number))
                
                return JsonResponse({
                    "status": "SUCCESS", 
                    "transaction_id": transaction_id, 
                    "order_number": proforma_invoice_number
                }, status=200)

            except ValueError as stock_err:
                # 🎯 EXCEPTION HANDLING: Capture succeeded, but item inventory checks failed.
                logger.critical(f"⚠️ PAYPAL CHARGED BUT OUT OF STOCK: Invoice {proforma_invoice_number}. Error: {str(stock_err)}")
                
                # Proactively queue an internal alert task here so your team can process a manual refund
                # send_admin_inventory_panic_email.delay(proforma_invoice_number, transaction_id)
                
                return JsonResponse({
                    "status": "STOCK_CONFLICT",
                    "error": "Payment captured successfully, but one or more items ran out of stock. Our support team will contact you shortly to arrange a fulfillment update or refund.",
                    "order_number": proforma_invoice_number,
                    "transaction_id": transaction_id
                }, status=200) # Return 200 so your frontend can read the special status and route nicely

        else:
            return JsonResponse({"error": "Gateway capture execution verification failed"}, status=capture_response.status_code)

    except (ProformaInvoice.DoesNotExist, Order.DoesNotExist):
        return JsonResponse({"error": "Order target invalid or already fully processed"}, status=400)
    except Exception as e:
        logger.exception(f"💥 Capture Processing Exception: {str(e)}")
        return JsonResponse({"error": "Internal database synchronization error"}, status=500)


@require_POST
def paypal_order_success(request):
    """Secondary customer-side validation webhook backup sync script mapper."""
    user = request.user if request.user.is_authenticated else None
    invoice_id = request.GET.get("invoice_id")
    exchange_rate = request.GET.get("exchange_rate")
    
    try:
        body = json.loads(request.body)
        purchase_unit = body["purchase_units"][0]
        capture_object = purchase_unit["payments"]["captures"][0]
        
        fx_amount = Decimal(str(capture_object["amount"]["value"]))
        fx_currency = str(capture_object["amount"]["currency_code"]).upper().strip()

        with transaction.atomic():
            order = Order.objects.select_for_update().get(order_number=invoice_id, is_ordered=False)
            proforma_invoice = ProformaInvoice.objects.select_for_update().get(proforma_order_number=invoice_id, is_ordered=False)
            
            payment = Payment.objects.create(
                user=user, 
                invoice=proforma_invoice, 
                order_id=body["id"],
                payment_id=capture_object["id"], 
                payer_id=body["payer"]["payer_id"], 
                payment_method="PayPal",
                amount_paid=fx_amount, 
                currency=fx_currency, 
                exchange_rate=Decimal(str(exchange_rate)),
                cny_equivalent=order.total_due,
                status="Completed" if capture_object["status"] == "COMPLETED" else "Pending"
            )

            order.payment = payment
            order.is_ordered = True
            order.order_status = "New" 
            order.save()

            cart_items = CartItem.objects.filter(cart=proforma_invoice.cart)
            for item in cart_items:
                OrderProduct.objects.create(
                    order=order, 
                    payment=payment, 
                    user=user,
                    product=item.product_variation.product, 
                    product_variation=item.product_variation,
                    quantity=item.quantity, 
                    product_price=item.product_variation.price, 
                    ordered=True
                )

                ProductVariation.objects.filter(pk=item.product_variation.pk).update(
                    stock=models.F('stock') - item.quantity
                )

            proforma_invoice.is_ordered = True
            proforma_invoice.save()
            
            active_cart = proforma_invoice.cart
            proforma_invoice.cart = None
            proforma_invoice.save()
            
            if active_cart:
                active_cart.cartitem_set.all().delete()

        transaction.on_commit(lambda: send_order_confirmation_email_task.delay(order.order_number))

        return JsonResponse({"order_number": order.order_number, "transaction_id": capture_object["id"]}, status=200)
        
    except (Order.DoesNotExist, ProformaInvoice.DoesNotExist):
        return JsonResponse({"error": "Order target invalid or already fully processed"}, status=400)
    except Exception as e:
        print(f"💥 Success Callback Pipeline Exception: {str(e)}")
        return JsonResponse({"error": "Internal ledger execution exception"}, status=500)


# def paypal_order_failure(request, order_id=None):
#     user = request.user
#     context = {"user": user, "order_id": order_id, "page_title": "Payment Failed ｜ 支付失敗"}
#     return render(request, "orders/payment_failure.html", context)



