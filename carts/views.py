from django.shortcuts import render, redirect, get_object_or_404
from store.models import ProductVariation
from .models import Cart, CartItem, ShippingCharge, CheckoutInfo, ProformaInvoice
from accounts.models import Address
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from accounts.models import UserProductList
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.data import DESTINATIONS_GLOBAL, DESTINATIONS_GREATER_CHINA, DESTINATIONS_MAINLAND_CHINA, CURRENCIES, CURRENCY_SYMBOL
import json
from sqids import Sqids

from .utils import get_available_services, calculate_shipping_cost, \
htmx_invalid_offer_response, handle_perk_status, htmx_invalid_voucher_response, calculate_foreign_amount, \
get_grand_total_before_voucher, update_applied_voucher, update_total_payable, get_currency_format, broadcast_cart_change, \
get_or_lock_checkout_rate, get_cash_voucher_balance, update_costs_oobs, get_cart_totals

from accounts.models import Perk, CustomerVoucher, UserPerk, UserProfile
from .forms import ProformaInvoiceForm
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from accounts.evaluators import PerkEvaluator
from django.db import transaction
from django.db.models import F, Sum
# from .tax import calculate_free_port_tax, calculate_australia_tax, calculate_new_zealand_tax,calculate_singapore_tax,calculate_malaysia_tax,calculate_korea_tax,calculate_japan_tax, calculate_taiwan_tax


def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def set_currency(request):
    currency_code = request.GET.get('code', 'HKD')
    # We create a JsonResponse instead of HttpResponseRedirect
    response = JsonResponse({
        "status": "success",
        "redirect_url": request.META.get('HTTP_REFERER', '/'),
    })
    # Set the cookie on this JSON response
    response.set_cookie(
        'user_currency', 
        currency_code, 
        max_age=31536000, #365 days 
        samesite='Lax'
    )
    return response


def update_exchange_rate_api(request):
    # 1. Fetch current user context parameters safely
    is_integer, current_currency_code = get_currency_format(request)

    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request), user=None)

    # 2. Leverage our utility function to calculate fresh rates AND generate the absolute timestamp
    rate = get_or_lock_checkout_rate(request, current_currency_code)
    four_digit_rate = intcomma(f"{rate:.4f}")

    # Grab the precise UNIX millisecond milestone stamped by the utility function above
    rate_expiry_timestamp = request.session.get('rate_expiry_timestamp', 0)

    # 3. Pull cart details to construct structural displays
    cart_items = cart.cartitem_set.all()
    has_physical_items = cart_items.filter(product_variation__product__is_physical=True).exists()
    has_e_items = cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
    has_cash_voucher_items = cart_items.filter(product_variation__product__is_voucher=True).exists()

    # 0. Forex Rate Layout Definition
    if current_currency_code.upper() == "CNY":
        display_rate = f"{four_digit_rate} (Base Currency ｜ 本位貨幣)"
    else:
        display_rate = four_digit_rate

    ex_rate_html = f'<span id="locked_exchange_rate" hx-swap-oob="true" class="font-semibold">{ display_rate }</span>'
    
    # 1. Cart Subtotals
    cart_grand_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
    e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
    foreign_currency_symbol, cart_items_quantity = get_cart_totals(request, cart)

    physical_products_total_foreign_html = f'<span id="physical_products_total_foreign" hx-swap-oob="true">{ foreign_currency_symbol } { physical_products_total_foreign }</span>' if has_physical_items else ""
    e_products_total_foreign_html = f'<span id="e_products_total_foreign" hx-swap-oob="true">{ foreign_currency_symbol } { e_products_total_foreign }</span>' if has_e_items else  ""
    voucher_products_total_foreign_html = f'<span id="voucher_purchase_total_foreign" hx-swap-oob="true">{ foreign_currency_symbol } { voucher_products_total_foreign }</span>' if has_cash_voucher_items else ""

    # 2. Shipping Cost
    shipping_data = request.session.get('shipping_data', {})
    shipping_cost = Decimal(str(shipping_data.get('shipping_cost', '0.00')).replace(",", ""))
    foreign_currency_symbol, shipping_cost_foreign = calculate_foreign_amount(request, shipping_cost)
    shipping_cost_foreign_two_digit = Decimal(str(shipping_cost_foreign).replace(",", ""))
    shipping_cost_foreign = intcomma(f"{shipping_cost_foreign_two_digit:.0f}") if is_integer else intcomma(f"{shipping_cost_foreign_two_digit:.2f}")
    shipping_cost_foreign_html = f'<span id="shipping_cost_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } { shipping_cost_foreign }</span>' if has_physical_items else ""

    # # 3. Tax & Duty

    # 4. Discount / Offer
    discount_data = request.session.get('offer_applied', {})
    discount_amount = Decimal(str(discount_data.get('discount_amount', '0.00')).replace(",", ""))
    foreign_currency_symbol, offer_applied_foreign = calculate_foreign_amount(request, discount_amount)
    offer_applied_foreign_two_digit = Decimal(str(offer_applied_foreign).replace(",", ""))
    fmt_offer = intcomma(f"{offer_applied_foreign_two_digit:.0f}") if is_integer else intcomma(f"{offer_applied_foreign_two_digit:.2f}")
    display_offer = f"({fmt_offer})" if offer_applied_foreign_two_digit > 0 else fmt_offer
    offer_applied_foreign_html = f'<span id="discount_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({ display_offer })</span>'

    # 5. Voucher
    voucher_data = request.session.get("applied_voucher", {})
    voucher_applied_amount = Decimal(str(voucher_data.get("applied_voucher_amount", '0.00')).replace(",", ""))
    foreign_currency_symbol, voucher_applied_foreign = calculate_foreign_amount(request, voucher_applied_amount)
    voucher_applied_foreign_two_digit = Decimal(str(voucher_applied_foreign).replace(",", ""))
    fmt_voucher_applied_foreign = intcomma(f"{voucher_applied_foreign_two_digit:.0f}") if is_integer else intcomma(f"{voucher_applied_foreign_two_digit:.2f}")
    display_voucher_applied_foreign = f"({fmt_voucher_applied_foreign})" if voucher_applied_foreign_two_digit > 0 else fmt_voucher_applied_foreign
    voucher_applied_foreign_html = f'<span id="summary_voucher_applied_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({ display_voucher_applied_foreign })</span>'

    # 6. Total Payable
    total_payables_html, amount, amount_foreign = update_total_payable(request, cart)

    # 💡 BYPASS WARNINGS FOR CNY CODES
    if current_currency_code.upper() == "CNY":
        warning_html = '<div id="price-warning" hx-swap-oob="true" class="hidden"></div>'
        overlay_html = '<div id="price-overlay" hx-swap-oob="true" class="hidden"></div>'
    else:
        # Leave them alone for normal currencies to let the JS timer take control
        warning_html = ""
        overlay_html = ""

    summary_foreign_oob = [
        ex_rate_html,
        physical_products_total_foreign_html,
        e_products_total_foreign_html,
        voucher_products_total_foreign_html,
        shipping_cost_foreign_html,
        offer_applied_foreign_html,
        voucher_applied_foreign_html,
        total_payables_html,
        warning_html,  # 💡 Injected OOB state override
        overlay_html   # 💡 Injected OOB state override
    ]

    broadcast_cart_change(request)
    return HttpResponse("".join(filter(None, summary_foreign_oob)))


@require_POST
def add_to_cart(request):
    user = request.user if request.user.is_authenticated else None

    product_sku_id = request.POST["product_sku_id"]
    product = ProductVariation.objects.get(id=int(product_sku_id))
    quantity_added = int(request.POST.get("quantity"))

    # get cart
    try:
        if user:
            cart = Cart.objects.get(user=user) if Cart.objects.filter(user=user) else Cart.objects.create(cart_id=_cart_id(request), user=user)
            # if item was in wishlist, delete from wishlist
            if UserProductList.objects.filter(user=user, product_variation=product, list_type='WISHLIST').first():
                wishlist_item = UserProductList.objects.get(user=user, product_variation=product, list_type='WISHLIST')
                wishlist_item.delete()

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

    # get cart-item
    try:
        # if already in cart, add quantity
        cart_item = CartItem.objects.get(product_variation=product, cart=cart)
        cart_item.quantity += quantity_added
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product_variation = product,
            cart = cart,
            quantity = quantity_added,
            user = user if user else None
        )
        cart_item.save()
    
    # get all existing cart-items after the cart_item is saved
    try:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        cart_items_data = []
        for item in cart_items:
            cart_items_data.append({
                'product_variation': str(item.product_variation),
                'product': str(item.product_variation.product),
                'cart': str(item.cart),
                'quantity': item.quantity,
                'price': item.product_variation.price,
                'url': str(item.product_variation.product.get_url()),
                'image_url': item.product_variation.images.url if item.product_variation.images else ''
            })
        has_physical_items = cart_items.filter(product_variation__product__is_physical=True).exists()
        request.session["has_physical_items"] = bool(has_physical_items)

    except Cart.DoesNotExist:
        cart_items_count = 0
        cart_items_sub_total = 0

    cart_items_count = cart.get_items_count()
    cart_items_sub_total = cart.get_cart_total()

    context = {
        "status": "success",
        "cart_items_count": cart_items_count,
        "cart_items_sub_total": cart_items_sub_total,
        "cart_items": cart_items_data if cart_items else None,
        "quantity_added": quantity_added
    }


    return JsonResponse(context)


def get_cart_item_info(request):
    sku_id = request.GET.get("sku_id")
    user = request.user if request.user.is_authenticated else None
    try:
        if user:
            cart = Cart.objects.get(user=user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.filter(cart=cart, is_active=True, product_variation__id=int(sku_id))
    except:
        cart = None
        cart_item = None

    return JsonResponse({"sku_id": sku_id, "cart_item": list(cart_item.values()) if cart_item else None})


def cart(request):
    user = request.user if request.user.is_authenticated else None
    cart_id = _cart_id(request)
    wishlist = None
    addresses = None
    default_address = None
    cart = None
    cash_voucher_balance = None
    max_voucher_enterable = None

    # Foreign currency layout parameters
    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]
    locked_rate = get_or_lock_checkout_rate(request, foreign_currency_code)

    # 1. 🔥 THE INITIALIZATION FIX: Setup clean, blank baseline maps 
    # instead of completely deleting the dictionary reference frames!
    request.session["shipping_data"] = {
        "method": "DEFAULT",
        "region": "digital",
        "destination_id": "",
        "shipping_cost": "0.00",
        "shipping_cost_foreign": "0" if is_integer else "0.00"
    }
    request.session["offer_applied"] = {"offer_code": "", "discount_amount": "0.00", "discount_amount_foreign": "0" if is_integer else "0.00"}
    request.session["applied_voucher"] = {"applied_voucher_amount": "0.00", "applied_voucher_amount_foreign": "0" if is_integer else "0.00"}
    request.session.modified = True

    try:
        if user:
            cart, created = Cart.objects.get_or_create(user=user, defaults={'cart_id': cart_id})
            wishlist = UserProductList.objects.filter(user=user, list_type='WISHLIST').order_by('-added_date') or None 
            if wishlist:
                for wish in wishlist:
                    wish.sku = wish.product_variation.get_sku()
            
            addresses = Address.objects.filter(profile__user=user)
            default_address = addresses.filter(is_default=True).first()

            cash_voucher_balance = get_cash_voucher_balance(request)
            total_payable, total_payable_foreign = get_grand_total_before_voucher(request, cart)
            max_voucher_enterable = min(cash_voucher_balance, total_payable)
        else:
            cart, created = Cart.objects.get_or_create(cart_id=cart_id, user=None)
            cash_voucher_balance = None

        if created:
            cart.saved()
  
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
            '-product_variation__product__is_physical', 
            'product_variation__product__is_voucher',  
            'product_variation__product__product_name' 
        )
        has_physical_items = cart_items.filter(product_variation__product__is_physical=True).exists()
        has_e_items = cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
        has_cash_voucher_items = cart_items.filter(product_variation__product__is_voucher=True).exists()
        
    except Exception as e:
        print("Cart View Generation Exception: ", e)
        cart_total = "0.00"
        cart_items_quantity = 0
        cart_items = None
        has_physical_items = False
        has_e_items = False
        has_cash_voucher_items = False

    # 2. 🔥 FORCE MASTER LEDGER ENGINE RECALCULATION
    # Runs our unified component summation before building the template data context
    _, fmt_cny_payable, fmt_fx_payable = update_total_payable(request, cart)

    def get_session_fx(key, nested_key, fallback_val):
        val = request.session.get(key, {}).get(nested_key, None)
        return val if val is not None else fallback_val
    
    cart_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
    e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
    foreign_currency_symbol, cart_items_quantity = get_cart_totals(request, cart)

    context = {
        "physical_products_total": physical_products_total,
        "e_products_total": e_products_total,
        "voucher_products_total": voucher_products_total,
        "cart_total": cart_total,
        "total_payable": fmt_cny_payable, # Sourced directly from our locked ledger engine
        "cart_items_quantity": cart_items_quantity,
        "cart": cart,
        "has_physical_items": has_physical_items, 
        "has_e_items": has_e_items,
        "has_cash_voucher_items": has_cash_voucher_items,
        "cart_items": cart_items,

        "shipping_cost": get_session_fx("shipping_data", "shipping_cost", "0.00"),
        "offer_applied": get_session_fx("offer_applied", "discount_amount", "0.00"),
        "voucher_applied": get_session_fx("applied_voucher", "applied_voucher_amount", "0.00"),
        "wishlist": wishlist,
        "cash_voucher_balance": cash_voucher_balance,
        "max_voucher_enterable": max_voucher_enterable,

        # Foreign currency configuration metrics mappings
        "physical_products_total_foreign": physical_products_total_foreign,
        "e_products_total_foreign": e_products_total_foreign,
        "voucher_products_total_foreign": voucher_products_total_foreign,
        "cart_total_foreign": fmt_fx_payable,
        "total_payable_foreign": fmt_fx_payable, 
        "currency_selection": CURRENCIES,
        "locked_rate": locked_rate,
        "foreign_currency_symbol": foreign_currency_symbol,
        "is_integer": is_integer,
        "shipping_cost_foreign": get_session_fx("shipping_data", "shipping_cost_foreign", "0") if is_integer else get_session_fx("shipping_data", "shipping_cost_foreign", "0.00"),
        "offer_applied_foreign": get_session_fx("offer_applied", "discount_amount_foreign", "0") if is_integer else get_session_fx("offer_applied", "discount_amount_foreign", "0.00"),
        "voucher_applied_foreign": get_session_fx("applied_voucher", "applied_voucher_amount_foreign", "0") if is_integer else get_session_fx("applied_voucher", "applied_voucher_amount_foreign", "0.00"),

        "addresses": addresses,
        "default_address": default_address,
        "global_destinations": DESTINATIONS_GLOBAL,
        "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
        "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,

        "page_title": "Cart｜購物車", 
        "main_title": "Cart｜購物車",
        "sub_title_1": "Soon to be yours…Take the final step to bring them home.",
        "sub_title_2": "即刻擁有…只差一步，把心儀好物帶回家。",
        "bread_crumb_1": "首頁｜Home",
        "bread_crumb_2": "寶貝們｜Products",
        "bread_crumb_3": "購物車｜Cart",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/store/products/all",
        "bread_crumb_3_url": "/carts/cart",
    }

    return render(request, 'store/cart.html', context)


@require_POST
def calculate_shipping(request):
    cart = Cart.objects.filter(user=request.user).first()
    method = request.POST.get('shipping_accordion')
    region = request.POST.get("zone")
    destination_id = request.POST.get("destination") or request.POST.get("address_id")
    available_services = get_available_services(method, region, destination_id)
    available_services_pks = [service.pk for service in available_services]

    oob_updates = []

    # if no available_services
    if len(available_services) < 1:
        response = HttpResponse("", status=200)
        response['HX-Trigger'] = json.dumps({
            "noService": {
                "title": "Delivery Unavailable\n無法配送",
                "message": "We couldn't find a shipping method for this location.\n我們無法找到合適的配送方式。"
            }
        })
        return response
    # else:
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    physical_items = cart_items.filter(product_variation__product__is_physical=True)   
    raw_shipping_cost = calculate_shipping_cost(request, physical_items, available_services)
    formatted_shipping_cost = intcomma(f"{raw_shipping_cost:.2f}")
    foreign_currency_symbol, formatted_shipping_cost_foreign = calculate_foreign_amount(request, raw_shipping_cost)

    request.session['shipping_data'] = {
        "method": method,
        "region": region,
        "destination_id": destination_id,
        "is_calculated": True,
        "available_services_pks": available_services_pks,
        "shipping_cost": formatted_shipping_cost,
        "foreign_currency_symbol": foreign_currency_symbol,
        "shipping_cost_foreign": formatted_shipping_cost_foreign,
    }
    request.session.modified = True

    main_badge_html = render_to_string("store/partials/shipping_result.html", {"shipping_cost": formatted_shipping_cost}, request=request)
    shipping_cost_html = f"""
        <div id="shipping-result-container" hx-swap-oob="outerHTML" class="mt-4 border-t border-dashed border-base-300">
            {main_badge_html}
        </div>
    """
    summary_shipping_oob = f"""
        <span id="summary-shipping" hx-swap-oob="true">¥ { formatted_shipping_cost }</span>
        <span id="shipping_cost_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } { formatted_shipping_cost_foreign }</span>
    """
    oob_updates.append(shipping_cost_html)
    oob_updates.append(summary_shipping_oob)

    active_button_html = f"""
        <div id="checkout-btn-wrapper" hx-swap-oob="true" class="mt-6">
            <a href="/carts/checkout/" 
                hx-boost="true" 
                id="checkout-btn" 
                class="btn btn-success btn-block flex gap-3 h-auto py-2 min-h-0 animate-bounce-once"
            >
                <span>Proceed to Checkout<br>前往結帳</span>
                <span><i class="fa-solid fa-arrow-right fa-xl"></i></span>
            </a>
            <!-- payment methods -->
            <div class="flex justify-around fill-primary stroke-primary my-[30px]">
                <i class="fa-brands fa-cc-paypal fa-2xl"></i>
                <i class="fa-solid fa-money-bill-transfer fa-2xl"></i>
                <i class="fa-solid fa-qrcode fa-2xl"></i>
            </div>
            <!-- Persistent Inline Disclaimer Box -->
            <div id="dap-disclaimer-box" class="mt-4 p-3 bg-warning/10 border border-warning/30 rounded-lg text-xs space-y-2 text-base-content/80">
                <p class="font-bold text-warning-content"><i class="fa-solid fa-triangle-exclamation mr-1"></i> Import Duties & Taxes (DAP Notice)</p>
                <p>Please note that orders are shipped on a <strong>DAP (Delivered at Place)</strong> basis. Prices and shipping fees shown do not include import duties, VAT, or customs clearance fees. These charges must be paid by the recipient upon arrival.</p>
                <div class="border-t border-dashed border-warning/20 my-1"></div>
                <p class="font-bold text-warning-content"><i class="fa-solid fa-triangle-exclamation mr-1"></i> 關稅與稅項確認 (DAP 條款)</p>
                <p>請注意，所有訂單均以 <strong>DAP (目的地交貨)</strong> 條件寄出。顯示的商品價格及運費不包含進口關稅、加值稅 (VAT) 或海關清關手續費。此類費用將由當地海關評定，並須由收件人在簽收時自行支付。</p>
            </div>
        </div>
    """
    oob_updates.append(active_button_html)

    # check if voucher is applied, if so, check if voucher > total payable
    updated_voucher_oob_string = update_applied_voucher(request, cart)
    oob_updates.append(updated_voucher_oob_string)

    # update total payable
    updated_summary_total_oob_string, amount, amount_foreign = update_total_payable(request, cart)
    oob_updates.append(updated_summary_total_oob_string)
   
    broadcast_cart_change(request)

    response = HttpResponse("".join(filter(None, oob_updates)))

    if region != "china":
        response['HX-Trigger'] = json.dumps({
            "showDapDisclaimer": {
                "title_en": "Import Duties & Taxes",
                "title_zh": "進口關稅與稅項提示",
                "text_en": "Your order will be shipped on a DAP (Delivered at Place) basis. ",
                "text_en_bold": "Displayed totals exclude regional import taxes, VAT, or clearance tariffs. The courier will collect these fees directly from you prior to or upon delivery.",
                "text_zh": "您的訂單將以 DAP (目的地交貨) 條款寄出。",
                "text_zh_bold": "目前的結算總額不包含您所在國家/地區的進口關稅、增值稅或清關手續費。物流公司將在派送前或派送時直接向您收取此費用。",
                "delivery_policy_link": "/shipping_policy/",
                "delivery_policy_link_label": "Shipping Policy｜配送須知"
            }
        })

    return response


def clear_shipping_session(request):
    if 'shipping_data' in request.session:
        del request.session['shipping_data']
        
    return HttpResponse(status=204)


def reset_shipping_fragment(request):
    cart = Cart.objects.filter(user=request.user).first()

    if "shipping_data" in request.session:
        del request.session["shipping_data"]
    request.session.modified = True

    tba_display_html = '<div id="shipping-cost-display" class="my-4 alert alert-soft alert-success shadow-sm text-base-content/50 justify-center"> Shipping Cost｜配送費 - TBA｜待定</div>'

    foreign_currency_code = request.COOKIES.get('user_currency', 'HKD')
    foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]

    # CRITICAL VERIFICATION: Make absolutely sure hx-swap-oob="true" is written perfectly
    shipping_oob = (
        f'<div id="shipping-result-container" hx-swap-oob="outerHTML" class="mt-4 border-t border-dashed border-base-300">{tba_display_html}</div>'
        f'<span id="summary-shipping" hx-swap-oob="true">¥ 0.00</span>'
        f'<span id="shipping_cost_amount_foreign" hx-swap-oob="true">{foreign_currency_symbol} 0.00</span>'
    )    
    total_payable_html, amount, amount_foreign = update_total_payable(request, cart)

    combined_response = (shipping_oob + total_payable_html).strip().replace("\n", "").replace("    ", "")

    return HttpResponse(combined_response)


@require_POST
def apply_offer(request):
    """
    Polymorphically processes coupon codes submitted manually by the client.
    Safely resolves both member specific vouchers and global system coupon strings.
    """
    user = request.user
    
    # 1. Active Cart Retrieval Security Pass
    if user.is_authenticated:
        cart = Cart.objects.filter(user=user).first()
    else:
        cart = Cart.objects.filter(cart_id=_cart_id(request)).first()
        
    if not cart or cart.get_items_count() == 0:
        return htmx_invalid_offer_response(request, "Cart is Empty | 購物車是空的", "")
    
    # 2. Extract and Sanitize code inputs
    raw_code = request.POST.get('code')
    if not raw_code:
        return htmx_invalid_offer_response(request, "Please enter a code | 請輸入優惠碼", "")
        
    code = raw_code.strip().upper()
    perk = None

    # 3. Polymorphic Lookup Pipeline Track
    # First Track: Look up personal membership coupon mapping assignments safely
    if user and user.is_authenticated:
        try:
            user_perk = UserPerk.objects.select_related('perk').get(user=user, unique_code=code)
            perk = user_perk.perk
        except UserPerk.DoesNotExist:
            perk = None

    # Second Track: Fall back to checking global registry matrices if member lookup missed
    if not perk:
        perk = Perk.objects.filter(code=code, is_active=True).first()

    # 4. Error Catchment Defensive Boundary
    if not perk:
        return htmx_invalid_offer_response(request, "Invalid Code | 可能打錯了？", "")
    
    # 5. Check Eligibility Conditions via our custom validator helper
    status = PerkEvaluator.get_eligibility_status(user, perk)
    formatted_min_spend = intcomma(f"{perk.safe_min_spending:.2f}")

    # Process and return completed OOB block responses seamlessly to the DOM layers
    return handle_perk_status(request, status, cart, code, perk, formatted_min_spend)


def reset_offer(request):
    try:
        user = request.user
        # 1. Clear session safely
        if "offer_applied" in request.session:
            del request.session["offer_applied"]
            request.session.modified = True
            
        # 2. Fetch current cart
        try:
            cart = Cart.objects.get(user=user) if user.is_authenticated else Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = None

        # 3. Render the blank input form layout as a clean string
        form_content = render_to_string('store/partials/offer_input.html', {}, request=request)
        
        # 4. Securely wrap it in the Out-Of-Band container target block
        offer_wrapper_oob = f'<div id="offer-form-wrapper" hx-swap-oob="true">{form_content}</div>'
       
        # 5. Build currency indicators
        is_integer, foreign_currency_code = get_currency_format(request)
        foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
        amount_string = "0" if is_integer else "0.00"
        
        pricing_oob = f'''
            <span id="summary-discount" hx-swap-oob="true">¥ 0.00</span>
            <span id="discount_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } {amount_string}</span>
        '''

        # 6. Gather trailing layout updates (Ensuring they return strings)
        total_oob = ""
        voucher_oob = ""
        if cart:
            total_oob, amount, amount_foreign = update_total_payable(request, cart)
            voucher_oob = update_applied_voucher(request, cart)

        # 7. Combine all components into a clean, text-safe payload
        final_payload = offer_wrapper_oob + pricing_oob + total_oob + voucher_oob

        broadcast_cart_change(request)
        return HttpResponse(final_payload)
    
    except Exception as e:
        print(f"Reset Offer Error: {e}")
        # Fallback payload layout to avoid blank pages or broken containers on critical errors
        form_content = render_to_string('store/partials/offer_input.html', {}, request=request)
        fallback_oob = f'<div id="offer-form-wrapper" hx-swap-oob="true">{form_content}</div>'
        broadcast_cart_change(request)
        return HttpResponse(fallback_oob)
    

def apply_voucher(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    # voucher_balance = CustomerVoucher.objects.filter(
    #         owner=request.user, 
    #         is_used=False
    #     ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')

    voucher_balance = get_cash_voucher_balance(request)

    try:
        user_input = Decimal(str(request.POST.get('voucher_amount', '0')).replace(",", ""))
    except (ValueError, TypeError):
        return htmx_invalid_voucher_response(request, voucher_balance, "Input Error\n輸入錯誤", f"Please enter a valid number.<br>請輸入有效的數字。")

    if user_input <= 0:
        return htmx_invalid_voucher_response(request, voucher_balance, "Input Error\n輸入錯誤", f"Amount must be greater than zero.<br>輸入金額必須大於0。")

    grand_total, grand_total_foreign = get_grand_total_before_voucher(request, cart) 

    # Validity Check - amount > total payable:
    limit = min(voucher_balance, grand_total)
    formatted_limit = intcomma(f"{limit:.2f}")
    if user_input > limit:
        return htmx_invalid_voucher_response(request, str(voucher_balance), "Input Error\n輸入錯誤", f"You can only apply up to CNY {formatted_limit} to this order.<br>最高抵扣金额为 CNY {formatted_limit}。")

    formatted_voucher_applied = intcomma(f"{user_input:.2f}")
    reamining_balance = max(voucher_balance - user_input, 0)
    formatted_cash_voucher_balance = intcomma(f"{reamining_balance:.2f}")
        
    context = {'voucher_applied': user_input}
    voucher_wrapper_oob = render_to_string('store/partials/voucher_active.html', context, request=request)

    oob_html_1 = f'<span id="voucher-balance" hx-swap-oob="true" class="badge badge-outline">CNY {formatted_cash_voucher_balance}</span>'
    
    foreign_currency_symbol, formatted_voucher_applied_foreign = calculate_foreign_amount(request, user_input)
    oob_html_2 = f'''
        <span id="summary_voucher_applied" hx-swap-oob="true">¥ ({formatted_voucher_applied})</span>
        <span id="summary_voucher_applied_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({formatted_voucher_applied_foreign})</span>
    '''

    request.session["applied_voucher"] = {
        "applied_voucher_amount": str(user_input),
        "applied_voucher_amount_foreign": str(formatted_voucher_applied_foreign.replace(",", "")),
    }
    request.session.modified = True

    # update total payable
    updated_summary_total_oob_string, amount, amount_foreign = update_total_payable(request, cart)

    final_payload = voucher_wrapper_oob + oob_html_1 + oob_html_2 + updated_summary_total_oob_string

    broadcast_cart_change(request)
    return HttpResponse(final_payload)


def reset_voucher(request):
    if "applied_voucher" in request.session:
        del request.session["applied_voucher"]
        request.session.modified = True

    try:
        cart = Cart.objects.get(user=request.user)
        cash_voucher_balance = get_cash_voucher_balance(request)
        # calculate total payable and get max_voucher_enterable
        grand_total, grand_total_foreign = get_grand_total_before_voucher(request, cart)

        limit = min(cash_voucher_balance, grand_total)

        context = {"max_voucher_enterable": limit}
        form_content = render_to_string('store/partials/voucher_input.html', context, request=request)

        voucher_wrapper_oob = f'<div id="voucher-form-wrapper" hx-swap-oob="true">{form_content}</div>'
        
        formatted_cash_voucher_balance = intcomma(f"{cash_voucher_balance:.2f}")
        oob_html_1 = f'<span id="voucher-balance" hx-swap-oob="true" class="badge badge-outline">CNY {formatted_cash_voucher_balance}</span>'
        
        is_integer, foreign_currency_code = get_currency_format(request)
        foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]
        amount_string = "0" if is_integer else "0.00"

        oob_html_2 = f''' 
            <span id="summary_voucher_applied" hx-swap-oob="true">¥ 0.00</span>
            <span id="summary_voucher_applied_foreign" hx-swap-oob="true">{foreign_currency_symbol} {amount_string}</span>
        '''

        updated_summary_total_oob_string, amount, amount_foreign = update_total_payable(request, cart)

        final_payload = voucher_wrapper_oob + oob_html_1 + oob_html_2 + updated_summary_total_oob_string

        broadcast_cart_change(request)
        return HttpResponse(final_payload)
    except Exception as e:
        print(f"Reset Voucher Error: {e}")
        # Secure error fallback wrapper return view layout block
        form_content = render_to_string('store/partials/voucher_input.html', {}, request=request)
        fallback_oob = f'<div id="voucher-form-wrapper" hx-swap-oob="true">{form_content}</div>'

        broadcast_cart_change(request)
        return HttpResponse(fallback_oob)   


@require_POST
def update_cart_item_qty(request, item_id):
    """
    Surgically updates a single cart item's quantity via HTMX POST.
    Enforces Ledger-First execution order to capture weight-based changes,
    while appending pre-built helper markup blocks to preserve structural layout styles.
    """
    htmx_htmls = []

    # 1. Update the Target Item's Quantity Natively
    cart_item = get_object_or_404(CartItem, id=item_id)
    new_qty = int(request.POST.get('quantity'))
    cart_item.quantity = new_qty
    cart_item.save()

    cart = cart_item.cart
    cart_items_quantity = cart.get_items_count()

    # forex
    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
    locked_rate = request.session.get('locked_rate', '1.0000')

    # costs updates
    oob_updates, triggers = update_costs_oobs(request, cart, is_integer, foreign_currency_code, foreign_currency_symbol, locked_rate)

    # quantity update
    subtotal = cart_item.subtotal
    formatted_subtotal = intcomma(f"{subtotal:.2f}")
    subtotal_html = f'<div id="subtotal_{item_id}" hx-swap-oob="true" class="text-right w-[calc((50%-4rem)/2)] text-[0.8rem] text-base-content font-semibold pr-3">CNY {formatted_subtotal}</div>'
    oob_updates.append(subtotal_html)

    updated_header_item_count_html = f'<span id="header_item_qty_{item_id}" hx-swap-oob="true" class="flex-grow-1">{ new_qty }</span>'
    oob_updates.append(updated_header_item_count_html)

    row_context = {
        "formated_subtotal": formatted_subtotal,
        "new_cart_total_count": cart_items_quantity,
        "formatted_new_cart_grand_total": cart.get_cart_total(),
    }

    change_qty_result_html = render_to_string('store/partials/change_qty_result.html', row_context, request=request)
    htmx_htmls.append(change_qty_result_html)

    # COMPILE
    final_html = "".join(filter(None, htmx_htmls))
    final_oob = "".join(filter(None, oob_updates))

    response = HttpResponse(final_html)
    response.content += final_oob.encode()
    if triggers:
        response['HX-Trigger'] = json.dumps(triggers)

    broadcast_cart_change(request)
    return response


@login_required(login_url="login")
@require_POST
def add_wish_to_cart(request, wish_id):
    user = request.user if request.user.is_authenticated else None
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': _cart_id(request)})
    cart_item_list_container_was_physical = cart.needs_shipping
    
    wish_item = UserProductList.objects.filter(pk=wish_id, user=user, list_type="WISHLIST").first()
    is_available = ProductVariation.objects.filter(pk=wish_item.product_variation.pk).first().stock > 0

    cart_was_not_empty = cart.get_items_count() > 0

    variation_id = request.POST.get('variation_id')
    target_variation_pk = wish_item.product_variation.pk if wish_item else variation_id

    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
    locked_rate = get_or_lock_checkout_rate(request, foreign_currency_code)

    final_oob_fragments = []
    need_broadcast = False
    triggers = {}

    if wish_item and is_available:
        try:
            with transaction.atomic():
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product_variation=wish_item.product_variation,
                    defaults={'quantity': 1, 'is_active': True}
                )
                if not item_created:
                    cart_item.quantity += 1
                    cart_item.save()
                wish_item.delete()
        except Exception as e:
            # Elegant fallback: Send a non-crashing alert toast to the UI on DB error
            response = HttpResponse(status=200)
            response["HX-Trigger"] = json.dumps({
                "errorMssg": {"title": "Error｜錯誤", "html": "Database action failed.<br>資料庫操作失敗。", "icon": "error"}
            })
            return response
    elif wish_item and not is_available:
        wish_item_name = f'{wish_item.product_variation.product.product_name}｜{wish_item.product_variation.get_sku}'
        response = HttpResponse(status=204)
        response['HX-Trigger'] = json.dumps({
            "infoMssg": {
                "title": "Out of Stock!\n暫時缺貨！",
                "html": f"{wish_item_name} is already in your favorites.!<br><br>{wish_item_name}已在您的收藏清單中！",
                "icon": "error"
            }
        })
        return response
    elif not wish_item:
        need_broadcast = True
        
    cart_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
    e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
    foreign_currency_symbol, cart_items_quantity = get_cart_totals(request, cart)
    
    cart_items_quantity = cart.get_items_count()
    cart_total = cart.get_cart_total()

    # 0. PRIMARY TARGET INLINE SWAP
    updated_cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
        '-product_variation__product__is_physical', 
        'product_variation__product__is_voucher',  
        'product_variation__product__product_name' 
    )
    cart_row_context = {
        "cart_items": updated_cart_items,
        "cart_items_quantity": cart_items_quantity,
        "cart_total": cart_total,
    }
    main_cart_html = render_to_string("store/partials/cart_item_row.html", cart_row_context, request=request)
    final_oob_fragments.append(f'<div id="cart_item_list_container" hx-swap-oob="true">{main_cart_html}</div>')

    request.session["has_physical_items"] = bool(updated_cart_items.filter(product_variation__product__is_physical=True).exists())
    request.session.modified = True

    has_physical_items = updated_cart_items.filter(product_variation__product__is_physical=True).exists()
    has_e_items = updated_cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
    has_cash_voucher_items = updated_cart_items.filter(product_variation__product__is_voucher=True).exists()
    
    # 1. NAV HEADER DROPDOWN SLIDER CONTAINER (OOB)
    header_context = {
        "current_cart_items": updated_cart_items,
        "is_htmx_update": True
    }
    header_list_html = render_to_string("store/partials/header_cart_list.html", header_context, request=request)
    final_oob_fragments.append(header_list_html)
    
    # # 2. UNIVERSAL NAVIGATION MINI METADATA COUNTERS (OOB)
    final_oob_fragments.append(f'<b id="cart_count" hx-swap-oob="true" class="font-bold">{cart_items_quantity} item{"s" if cart_items_quantity > 1 else ""}</b>')
    final_oob_fragments.append(f'<b id="cart_sub_total" hx-swap-oob="true" class="font-bold">CNY ¥ {cart_total}</b>')
    final_oob_fragments.append(f'<span id="cart_count_icon" hx-swap-oob="true" class="badge badge-sm indicator-item">{cart_items_quantity}</span>')

    # 3. WISHLIST WRAPPER PANEL (OOB)
    updated_wishlist = UserProductList.objects.filter(user=user, list_type='WISHLIST').order_by('-added_date') if user else []
    wishlist_html = render_to_string("store/partials/wishlist_row.html", {"wishlist": updated_wishlist}, request=request)
    final_oob_fragments.append(
        f'<div id="wishlist_wrapper_ul" hx-swap-oob="true" class="wishlist_wrapper flex flex-col divide-y divide-white/10">{wishlist_html}</div>'
    )

    # 4. INTEGRATED COSTS CALCULATIONS RIPPLE EFFECTS
    if cart_was_not_empty:
        has_physical_items_now = updated_cart_items.filter(product_variation__product__is_physical=True).exists()
        flipped_from_digital_to_physical = has_physical_items_now and not cart_item_list_container_was_physical
        if flipped_from_digital_to_physical:
        # swap for shipping_section_wrapper
            context = {
                "is_oob": True,
                "cart": cart,
                "has_physical_items": has_physical_items
            }
            shipping_section_html = render_to_string("store/partials/shipping_section_wrapper.html", context, request=request)
            final_oob_fragments.append(shipping_section_html)

            disabled_checkout_btn_html = """
                <button id="checkout-btn" hx-swap-oob="true" class="flex gap-3 btn btn-block btn-disabled opacity-80 cursor-not-allowed h-auto py-2 min-h-0" disabled>
                    <span>Please calculate shipping first<br>請先計算運費</span>
                    <span><i class="fa-solid fa-arrow-up fa-xl"></i></span>
                </button>
            """
            final_oob_fragments.append(disabled_checkout_btn_html)

        # update various costs calculation items - update costs oob
        oob_updates, costs_triggers = update_costs_oobs(
            request, cart, is_integer, foreign_currency_code, foreign_currency_symbol, locked_rate
        )
        if costs_triggers:
            triggers.update(costs_triggers)
        if oob_updates:
            final_oob_fragments.extend(oob_updates)    
        
    else:
        # update costs_calculations
        # addresses = Address.objects.filter(profile__user=user) if user else Address.objects.none()
        cash_voucher_balance = get_cash_voucher_balance(request) if user != None else 0
        total_payable, total_payable_foreign = get_grand_total_before_voucher(request, cart)
        max_voucher_enterable = min(cash_voucher_balance, total_payable)

        # context
        context = {
            # cart contents
            "physical_products_total": physical_products_total,
            "e_products_total": e_products_total,
            "voucher_products_total": voucher_products_total,
            "cart_total": cart_total,
            "total_payable": cart_total,
            "cart_items_quantity": cart_items_quantity,
            "cart": cart,
            "has_physical_items": has_physical_items,
            "has_e_items": has_e_items,
            "has_cash_voucher_items": has_cash_voucher_items,
            "cart_items": updated_cart_items,
            
            # other amounts
            "cash_voucher_balance": cash_voucher_balance,
            "max_voucher_enterable": max_voucher_enterable,
            "offer_applied": 0,
            "voucher_applied": 0,

            # foreign currency
            "physical_products_total_foreign": physical_products_total_foreign,
            "e_products_total_foreign": e_products_total_foreign,
            "voucher_products_total_foreign": voucher_products_total_foreign,
            "cart_total_foreign": cart_total_foreign,
            "total_payable_foreign": cart_total_foreign,
            "currency_selection": CURRENCIES,
            "locked_rate": locked_rate,
            "foreign_currency_symbol": foreign_currency_symbol,
            "is_integer": is_integer,
            "offer_applied_foreign": 0,
            "voucher_applied_foreign": 0,

            # shipping
            "global_destinations": DESTINATIONS_GLOBAL,
            "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
            "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
            "is_htmx_update": True
        }            
        
        full_calculations_html = render_to_string("store/partials/costs_calculations.html", context, request=request)
        final_oob_fragments.append(full_calculations_html)
        pass

    broadcast_cart_change(request)

    clean_unified_payload = "".join(filter(None, final_oob_fragments))
    response = HttpResponse(clean_unified_payload)
    
    if need_broadcast and user and target_variation_pk:
        is_already_moved = CartItem.objects.filter(cart=cart, product_variation_id=variation_id).exists()

        if is_already_moved:
            title = "Already Syncing | 已同步"
            msg =  "Item was already moved to cart.<br>該項目已移入購物車。"
            triggers["infoMssg"] = {"title": title, "html": msg, "icon": "info"}

    if triggers:
        response['HX-Trigger'] = json.dumps(triggers)

    return response


@require_POST
def delete_cart_item(request, item_id):
    """
    Surgically removes a target item row from the database via HTMX POST.
    Integrates the restructured, outsourced costs calculation engine smoothly
    to update totals, weight brackets, coupons, and vouchers in perfect sync.
    """
    user = request.user if request.user.is_authenticated else None
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': _cart_id(request)})
    cart_item = CartItem.objects.filter(pk=item_id, cart=cart).first()

    variation_id = request.POST.get('variation_id')
    target_variation_pk = cart_item.product_variation.pk if cart_item else variation_id

    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
    locked_rate = request.session.get('locked_rate', '1.0000')

    htmx_htmls = []
    triggers = {}
    need_broadcast = False

    # 1. Execute DB Atomic Removal Track
    if cart_item:
        try:
            with transaction.atomic():
                cart_item.delete()
        except Exception as e:
            response = HttpResponse(status=200)
            response["HX-Trigger"] = json.dumps({
                "errorMssg": {"title": "Error｜錯誤", "html": "Database action failed.<br>資料庫操作失敗。", "icon": "error"}
            })
            return response
    else:
        need_broadcast = True

    # 2. Extract Post-Save Active Cart QuerySets
    updated_cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
        '-product_variation__product__is_physical', 
        'product_variation__product__is_voucher',  
        'product_variation__product__product_name' 
    )

    cart_items_quantity = cart.get_items_count()
    cart_total = cart.get_cart_total()

    # 3. Re-render Content Card Rows List Out-of-Band
    cart_row_context = {
        "cart_items": updated_cart_items,
        "cart_items_quantity": cart_items_quantity,
        "cart_total": cart_total,
    }

    main_cart_html = render_to_string("store/partials/cart_item_row.html", cart_row_context, request=request)
    htmx_htmls.append(f'<div id="cart_item_list_container" hx-swap-oob="true">{main_cart_html}</div>')

    # Update background session flags
    request.session["has_physical_items"] = bool(updated_cart_items.filter(product_variation__product__is_physical=True).exists())
    request.session.modified = True

    # NAV HEADER DROPDOWN SLIDER CONTAINER (OOB)
    header_context = {
        "current_cart_items": updated_cart_items,
        "is_htmx_update": True
    }
    header_list_html = render_to_string("store/partials/header_cart_list.html", header_context, request=request)
    htmx_htmls.append(header_list_html)

    # COSTS_CALCULATIONS
    if cart_items_quantity > 0:
        # 💡 Sourced sequentially to pull perfectly balanced coupon, voucher, and shipping rules!
        oob_updates, costs_triggers = update_costs_oobs(
            request, cart, is_integer, foreign_currency_code, foreign_currency_symbol, locked_rate
        )
        if costs_triggers:
            triggers.update(costs_triggers)
        if oob_updates:
            htmx_htmls.extend(oob_updates)
            
    else:
        # 📉 5. EMPTY CART FALLBACK: Reset everything back to pristine baseline layout parameters
        cart_grand_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
        e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
        foreign_currency_symbol, cart_items_quantity = get_cart_totals(request, cart)

        addresses = Address.objects.filter(profile__user=user) if user else Address.objects.none()
        has_e_items = updated_cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
        has_cash_voucher_items = updated_cart_items.filter(product_variation__product__is_voucher=True).exists()
        cash_voucher_balance = get_cash_voucher_balance(request) if user is not None else 0
        
        total_payable, total_payable_foreign = get_grand_total_before_voucher(request, cart)
        max_voucher_enterable = min(cash_voucher_balance, total_payable)
        
        context = {
            "physical_products_total": physical_products_total,
            "e_products_total": e_products_total,
            "voucher_products_total": voucher_products_total,
            "cart_total": cart_total,
            "total_payable": cart_total,
            "cart_items_quantity": cart_items_quantity,
            "cart": cart,
            "has_physical_items": False,
            "has_e_items": has_e_items,
            "has_cash_voucher_items": has_cash_voucher_items,
            "cart_items": updated_cart_items,
            
            "cash_voucher_balance": cash_voucher_balance,
            "max_voucher_enterable": max_voucher_enterable,

            "physical_products_total_foreign": physical_products_total_foreign,
            "e_products_total_foreign": e_products_total_foreign,
            "voucher_products_total_foreign": voucher_products_total_foreign,
            "cart_total_foreign": cart_total_foreign,
            "total_payable_foreign": cart_total_foreign,
            "currency_selection": CURRENCIES,
            "locked_rate": locked_rate,
            "foreign_currency_symbol": foreign_currency_symbol,
            "is_integer": is_integer,
            "offer_applied_foreign": "0" if is_integer else "0.00",
            "voucher_applied_foreign": "0" if is_integer else "0.00",

            "addresses": addresses,
            "default_address": addresses.filter(is_default=True).first(),
            "global_destinations": DESTINATIONS_GLOBAL,
            "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
            "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
            "is_htmx_update": True
        }            
        
        empty_calculations_html = render_to_string("store/partials/costs_calculations.html", context, request=request)
        htmx_htmls.append(empty_calculations_html)

    # 6. Dispatch Payload Package
    broadcast_cart_change(request)

    clean_unified_htmx_htmls = "".join(filter(None, htmx_htmls))
    response = HttpResponse(clean_unified_htmx_htmls)

    if need_broadcast and target_variation_pk:
        is_still_in_basket = CartItem.objects.filter(cart=cart, product_variation_id=target_variation_pk).exists()
        if not is_still_in_basket:
            title, msg = ("Already Deleted | 已刪除", "This item was already removed from your cart in another window.<br>該項目已在其他視窗中從購物車中刪除。") 
            triggers["infoMssg"] = {"title": title, "html": msg, "icon": "info"}

    if triggers:
        response["HX-Trigger"] = json.dumps(triggers)

    return response


@require_POST
@login_required(login_url="login")
def add_to_wishlist(request, item_id):
    user = request.user if request.user.is_authenticated else None
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': _cart_id(request)})
    cart_item = CartItem.objects.filter(pk=item_id, cart=cart).first()
    
    variation_id = request.POST.get('variation_id')
    target_variation_pk = cart_item.product_variation.pk if cart_item else variation_id

    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
    locked_rate = request.session.get('locked_rate', '1.0000')

    final_oob_fragments = []
    triggers = {}
    need_broadcast = False
    
    if cart_item and user:
        try:
            with transaction.atomic():
                UserProductList.objects.get_or_create(
                    user=user,
                    product_variation=cart_item.product_variation,
                    list_type='WISHLIST'
                )
                cart_item.delete()
        except Exception as e:
            response = HttpResponse(status=200)
            response["HX-Trigger"] = json.dumps({
                "errorMssg": {"title": "Error｜錯誤", "html": "Database action failed.<br>資料庫操作失敗。", "icon": "error"}
            })
            return response
    else:
        need_broadcast = True
    
    updated_cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by(
        '-product_variation__product__is_physical', 
        'product_variation__product__is_voucher',  
        'product_variation__product__product_name' 
    )

    cart_items_quantity = cart.get_items_count()
    cart_total = cart.get_cart_total()

    # 0. PRIMARY TARGET INLINE SWAP
    # updated_cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    cart_row_context = {
        "cart_items": updated_cart_items,
        "cart_items_quantity": cart_items_quantity,
        "cart_total": cart_total,
    }
    main_cart_html = render_to_string("store/partials/cart_item_row.html", cart_row_context, request=request)
    final_oob_fragments.append(f'<div id="cart_item_list_container" hx-swap-oob="true">{main_cart_html}</div>')

    request.session["has_physical_items"] = bool(updated_cart_items.filter(product_variation__product__is_physical=True).exists())
    request.session.modified = True

    # 1. NAV HEADER DROPDOWN SLIDER CONTAINER (OOB)
    header_context = {
        "current_cart_items": updated_cart_items,
        "is_htmx_update": True
    }
    header_list_html = render_to_string("store/partials/header_cart_list.html", header_context, request=request)
    final_oob_fragments.append(header_list_html)

    # COSTS_CALCULATIONS
    if cart_items_quantity > 0:
        # 💡 Sourced sequentially to pull perfectly balanced coupon, voucher, and shipping rules!
        oob_updates, costs_triggers = update_costs_oobs(
            request, cart, is_integer, foreign_currency_code, foreign_currency_symbol, locked_rate
        )
        if costs_triggers:
            triggers.update(costs_triggers)
        if oob_updates:
            final_oob_fragments.extend(oob_updates)

    else:
        cart_grand_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
        e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
        foreign_currency_symbol, cart_items_quantity = get_cart_totals(request, cart)

        addresses = Address.objects.filter(profile__user=user) if user else Address.objects.none()
        has_e_items = updated_cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
        has_cash_voucher_items = updated_cart_items.filter(product_variation__product__is_voucher=True).exists()
        cash_voucher_balance = get_cash_voucher_balance(request) if user is not None else 0
        
        total_payable, total_payable_foreign = get_grand_total_before_voucher(request, cart)
        max_voucher_enterable = min(cash_voucher_balance, total_payable)
        
        context = {
            "physical_products_total": physical_products_total,
            "e_products_total": e_products_total,
            "voucher_products_total": voucher_products_total,
            "cart_total": cart_total,
            "total_payable": cart_total,
            "cart_items_quantity": cart_items_quantity,
            "cart": cart,
            "has_physical_items": False,
            "has_e_items": has_e_items,
            "has_cash_voucher_items": has_cash_voucher_items,
            "cart_items": updated_cart_items,
            
            "cash_voucher_balance": cash_voucher_balance,
            "max_voucher_enterable": max_voucher_enterable,

            "physical_products_total_foreign": physical_products_total_foreign,
            "e_products_total_foreign": e_products_total_foreign,
            "voucher_products_total_foreign": voucher_products_total_foreign,
            "cart_total_foreign": cart_total_foreign,
            "total_payable_foreign": cart_total_foreign,
            "currency_selection": CURRENCIES,
            "locked_rate": locked_rate,
            "foreign_currency_symbol": foreign_currency_symbol,
            "is_integer": is_integer,
            "offer_applied_foreign": "0" if is_integer else "0.00",
            "voucher_applied_foreign": "0" if is_integer else "0.00",

            "addresses": addresses,
            "default_address": addresses.filter(is_default=True).first(),
            "global_destinations": DESTINATIONS_GLOBAL,
            "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
            "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
            "is_htmx_update": True
        }            
        
        empty_calculations_html = render_to_string("store/partials/costs_calculations.html", context, request=request)
        final_oob_fragments.append(empty_calculations_html)

    # 3. WISHLIST WRAPPER PANEL (OOB)
    updated_wishlist = UserProductList.objects.filter(user=user, list_type='WISHLIST').order_by('-added_date') if user else []
    wishlist_html = render_to_string("store/partials/wishlist_row.html", {"wishlist": updated_wishlist}, request=request)
    final_oob_fragments.append(
        f'<div id="wishlist_wrapper_ul" hx-swap-oob="true" class="wishlist_wrapper flex flex-col divide-y divide-white/10">{wishlist_html}</div>'
    )

    broadcast_cart_change(request)

    clean_unified_payload = "".join(filter(None, final_oob_fragments))
    response = HttpResponse(clean_unified_payload)

    if need_broadcast and user and target_variation_pk:
        is_already_moved = UserProductList.objects.filter(
            user=user, 
            product_variation_id=target_variation_pk, 
            list_type='WISHLIST'
        ).exists()
        
        if is_already_moved:
            title = "Already Synchronized | 已同步"
            msg = "This item was already moved to your wishlist in another window.<br>該項目已在其他視窗中移入未來購物清單。"
            triggers["infoMssg"] = {"title": title, "html": msg, "icon": "info"}

    if triggers:
        response["HX-Trigger"] = json.dumps(triggers)

    return response


@login_required(login_url="login")
@require_POST
def delete_wishlist_item(request, wish_id):
    user = request.user if request.user.is_authenticated else None
    cart, _ = Cart.objects.get_or_create(user=user, defaults={'cart_id': _cart_id(request)})
    wish_item = UserProductList.objects.filter(pk=wish_id, user=request.user, list_type="WISHLIST").first()
    source = request.POST.get("source")

    variation_id = request.POST.get('variation_id')
    target_variation_pk = wish_item.product_variation.pk if wish_item else variation_id

    response_html = ""
    need_broadcast = False
    triggers = {}

    if wish_item:
        try:
            with transaction.atomic():        
                wish_item.delete()
        except Exception as e:
            # Elegant fallback: Send a non-crashing alert toast to the UI on DB error
            response = HttpResponse(status=200)
            response["HX-Trigger"] = json.dumps({
                "errorMssg": {"title": "Error｜錯誤", "html": "Database action failed.<br>資料庫操作失敗。", "icon": "error"}
            })
            return response
    else:
        need_broadcast = True

    updated_wishlist = UserProductList.objects.filter(user=user, list_type="WISHLIST")
    context = {
        "wishlist": updated_wishlist,
        "is_htmx_update": True  # To trigger hx-swap-oob="true" in the partial
    }

    if source == "dashboard":
        response_html = render_to_string('accounts/partials/wishlist_item.html', context, request=request)

    elif source == "cart":
        response_html = render_to_string('store/partials/wishlist_row.html', context, request=request)


    broadcast_cart_change(request)
    response = HttpResponse(response_html)


    if need_broadcast and user and target_variation_pk:
        is_still_in_wishlist = UserProductList.objects.filter(user=user, list_type="WISHLIST", product_variation_id=target_variation_pk).exists()
        
        if not is_still_in_wishlist:
            title, msg = ("Item Removed | 項目已移除", "This item was removed from your wishlist in another tab.<br>此項目已在另一分頁中從清單移除。"),
            triggers["infoMssg"] = {"title": title, "html": msg, "icon": "info"}

    if triggers:
        response["HX-Trigger"] = json.dumps(triggers)

    return response


@require_POST
@login_required(login_url="login")
def add_to_favorite(request, variation_id):
    user = request.user
    product_variation = ProductVariation.objects.filter(pk=variation_id, is_available=True).first()
    if product_variation:
        try:
            favorite_item = UserProductList.objects.get(user=user, product_variation=product_variation, list_type="FAVORITE")
            favorite_item_name = favorite_item.product_variation.product.product_name
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                "infoMssg": {
                    "title": "Already done!\n已在您的收藏清單中！",
                    "html": f"{favorite_item_name} is already in your favorites.!<br><br>{favorite_item_name}已在您的收藏清單中！",
                    "icon": "info"
                }
            })
            return response
        except UserProductList.DoesNotExist:
            favorite_item = UserProductList.objects.create(
                user=user,
                product_variation=product_variation,
                list_type="FAVORITE"
            )
            favorite_item_name = favorite_item.product_variation.product.product_name
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({
                "successMssg": {
                    "title": "Added!｜已收藏！",
                    "html": f"{favorite_item_name} has been added to your favorites.!<br><br>{favorite_item_name}已被收藏在您的收藏清單中！",
                    "icon": "success"
                }
            })
            return response


def checkout(request):
    user = request.user if request.user.is_authenticated else None
    cart = Cart.objects.filter(user=user).first() if user else Cart.objects.filter(cart_id=_cart_id(request)).first()
    
    # -------------------------------------------------------------
    # 1. SHARED PRE-FLIGHT BOUNDARY CONTEXT (Executes for both GET & POST)
    # -------------------------------------------------------------
    if not cart or not cart.cartitem_set.filter(is_active=True).exists():
        return redirect("cart")
    
    cart_items = cart.cartitem_set.filter(is_active=True)
    has_physical_items = cart_items.filter(product_variation__product__is_physical=True).exists()
    
    shipping_data = request.session.get("shipping_data", {})
    offer_data = request.session.get("offer_applied", {})
    voucher_data = request.session.get("applied_voucher", {})

    is_integer, current_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL[current_currency_code]

    if not shipping_data or shipping_data == {}:
        if has_physical_items:
            messages.warning(request, "請先計算運費以繼續結帳。 | Please calculate shipping first.")
            return redirect('cart')

        else:
            shipping_data = {
                "method": "DEFAULT",
                "region": "digital",
                "destination_id": "",
                "shipping_cost": "0.00",
                "shipping_cost_foreign": "0" if is_integer else "0.00"
            }
            request.session["shipping_data"] = shipping_data
            request.session.modified = True

    # 🌟 THE TRANSLATION LAYER: Map lowercase session strings cleanly to database choices
    raw_method = shipping_data.get("method", "dropdown")
    method_to_source_map = {
        "saved_address": "ADDRESS_BOOK",
        "ADDRESS_BOOK": "ADDRESS_BOOK",
        "dropdown": "DEFAULT",
        "DEFAULT": "DEFAULT"
    }
    db_destination_source = method_to_source_map.get(raw_method, "DEFAULT")

    # 🔒 EXECUTE THE MASTER LEDGER ANCHOR RECALCULATION
    _, total_due_str, total_due_foreign_str = update_total_payable(request, cart)
    locked_rate = get_or_lock_checkout_rate(request, current_currency_code)

    def clean_for_db(val):
        """
        Surgically sanitises financial values into floating-point numbers.
        Wipes away commas, currency signs (€, £, ¥, $, etc.), or alphabetical symbols (AUD, HKD) via regex.
        """
        if val is None:
            return 0.00
        if isinstance(val, str):
            import re
            # 🌟 REGEX MATCH: Keep only numbers (\d), dots (.), and minus signs (-)
            sanitized = re.sub(r'[^\d.-]', '', val).strip()
            return float(sanitized) if sanitized else 0.00
        return float(val)

    # 💡 FIXED ASSIGNMENTS: Pull pre-calculated balanced targets out of session points maps
    fx_shipping_clean = clean_for_db(shipping_data.get("shipping_cost_foreign"))
    fx_offer_clean = clean_for_db(offer_data.get("discount_amount_foreign"))
    fx_voucher_clean = clean_for_db(voucher_data.get("applied_voucher_amount_foreign"))
    fx_payable_clean = clean_for_db(total_due_foreign_str)

    # Backward-derive the physical entry for CheckoutInfo matching your screen lines exactly
    fx_physical_clean = (
        fx_payable_clean 
        + fx_offer_clean 
        + fx_voucher_clean 
        - fx_shipping_clean 
        - clean_for_db(cart.get_e_products_subtotal_foreign(current_currency_code, locked_rate)) 
        - clean_for_db(cart.get_voucher_products_subtotal_foreign(current_currency_code, locked_rate))
    )
   
    has_e_items = cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
    has_voucher_items = cart_items.filter(product_variation__product__is_voucher=True).exists()

    # Establish display constraints based on composition metrics
    if has_physical_items and has_voucher_items:
        display_mode = "PHYSICAL_AND_VOUCHER"
    elif has_physical_items:
        display_mode = "PHYSICAL"
    elif has_voucher_items:
        display_mode = "VOUCHER_ONLY"
    else:
        display_mode = "EPRODUCT_ONLY"
    
    checkout_info, _ = CheckoutInfo.objects.update_or_create(
        cart=cart,
        defaults={
            "user": user,
            "display_mode": display_mode,
            "cart_total": clean_for_db(cart.get_cart_total()),
            
            # Synchronised balanced metrics
            "cart_total_foreign": float(fx_physical_clean) + clean_for_db(cart.get_e_products_subtotal_foreign(current_currency_code, locked_rate)) + clean_for_db(cart.get_voucher_products_subtotal_foreign(current_currency_code, locked_rate)),
            "destination_source": db_destination_source,
            "default_zone": shipping_data.get("region") if db_destination_source == "DEFAULT" else "",
            "default_destination": shipping_data.get("destination_id") if db_destination_source == "DEFAULT" else "",
            "address_id": shipping_data.get("destination_id") if db_destination_source == "ADDRESS_BOOK" else "",
            "shipping_cost": clean_for_db(shipping_data.get("shipping_cost")),
            "shipping_cost_amount_foreign": fx_shipping_clean,
            "offer_code": offer_data.get("offer_code", ""),
            "discount_amount": clean_for_db(offer_data.get("discount_amount")),
            "discount_amount_foreign": fx_offer_clean,
            "voucher_applied": clean_for_db(voucher_data.get("applied_voucher_amount")),
            "applied_voucher_amount_foreign": fx_voucher_clean,
            "tax_amount": 0.00,
            "tax_amount_foreign": 0.00,
            "total_due": clean_for_db(total_due_str),
            "total_due_foreign": fx_payable_clean,
            "locked_exchange_rate": clean_for_db(locked_rate),
            "currency_code": request.session.get('foreign_currency_code', 'HKD'),
        }
    )

    # Establish baseline geography contexts
    address = None
    state = None
    country = ""

    if display_mode in ["EPRODUCT_ONLY", "VOUCHER_ONLY"]:
        state = "Digital"
        country = "XX"  # Safe generic ISO token or "Digital" depending on your database constraint schema
    else:
        session_method = shipping_data.get("method", "").strip()
        session_dest_id = shipping_data.get("destination_id", "").strip()
        session_region = shipping_data.get("region", "").strip()

        if session_method in ["saved_address", "ADDRESS_BOOK", "address_id"] and session_dest_id:
            address = Address.objects.filter(id=int(session_dest_id)).first() if session_dest_id.isdigit() else Address.objects.filter(id=session_dest_id).first()
            if address:
                state = address.state_province_region
                country = address.country
        elif session_method == "dropdown" or session_region:
            if session_region == "china":
                state = session_dest_id  
                country = "CN"
            else:
                state = None
                country = session_dest_id 

        if not country and user.is_authenticated:
            fallback_address = Address.objects.filter(profile__user=user, is_default=True).first()
            if fallback_address:
                address = fallback_address
                state = fallback_address.state_province_region
                country = fallback_address.country

    # -------------------------------------------------------------
    # 2. POST ORDER SUBMISSION PIPELINE
    # -------------------------------------------------------------
    if request.method == "POST":
        post_data = request.POST.copy()
        
        if display_mode in ["EPRODUCT_ONLY", "VOUCHER_ONLY"]:
            post_data['country'] = "XX"
            post_data['state_province_region'] = "Digital"

        proforma_invoice_form = ProformaInvoiceForm(post_data, display_mode=display_mode)

        # Enforce destination locks for physical transactions
        if display_mode not in ["EPRODUCT_ONLY", "VOUCHER_ONLY"] and country:
            proforma_invoice_form.data = proforma_invoice_form.data.copy()
            proforma_invoice_form.data['country'] = country
            if country == "CN" and state:
                proforma_invoice_form.data['state_province_region'] = state

        if proforma_invoice_form.is_valid():
            try:
                proforma_invoice = ProformaInvoice.objects.filter(cart=cart).order_by('-updated_at').first()
                
                if proforma_invoice and proforma_invoice.is_ordered:
                    proforma_invoice.cart = None
                    proforma_invoice.save()
                    proforma_invoice = None 

                if display_mode in ["EPRODUCT_ONLY", "VOUCHER_ONLY"]:
                    cleaned_country = "XX"
                    cleaned_state = "Digital"
                else:
                    cleaned_country = country if country else proforma_invoice_form.cleaned_data.get('country')
                    cleaned_state = state if state else proforma_invoice_form.cleaned_data.get('state_province_region')

                field_mapping_defaults = {
                    "user": user if user.is_authenticated else None,
                    "display_mode": display_mode,
                    "email": proforma_invoice_form.cleaned_data.get("email"),
                    "recipient_first_name": proforma_invoice_form.cleaned_data.get("recipient_first_name"),
                    "recipient_last_name": proforma_invoice_form.cleaned_data.get("recipient_last_name"),
                    "recipient_mobile_area": proforma_invoice_form.cleaned_data.get("recipient_mobile_area"),
                    "recipient_mobile_number": proforma_invoice_form.cleaned_data.get("recipient_mobile_number"),
                    "address_line_1": proforma_invoice_form.cleaned_data.get("address_line_1"),
                    "address_line_2": proforma_invoice_form.cleaned_data.get("address_line_2"),
                    "city": proforma_invoice_form.cleaned_data.get("city"),
                    "state_province_region": cleaned_state,
                    "country": cleaned_country,
                    "postal_code": proforma_invoice_form.cleaned_data.get("postal_code"),

                    "recipient_email": proforma_invoice_form.cleaned_data.get("recipient_email"),
                    "gift_message": proforma_invoice_form.cleaned_data.get("gift_message"),

                    "delivery_note": proforma_invoice_form.cleaned_data.get("delivery_note"),
                    "do_not_send_invoice": proforma_invoice_form.cleaned_data.get("do_not_send_invoice"),
                    
                    "google_place_id": proforma_invoice_form.cleaned_data.get("google_place_id"),
                    "latitude": proforma_invoice_form.cleaned_data.get("latitude"),
                    "longitude": proforma_invoice_form.cleaned_data.get("longitude"),
                    "is_verified_by_google": proforma_invoice_form.cleaned_data.get("is_verified_by_google", False),
                    
                    "cart_total": checkout_info.cart_total,
                    "shipping_cost": checkout_info.shipping_cost,
                    "discount": checkout_info.discount_amount,
                    "tax": checkout_info.tax_amount,
                    "voucher_applied": checkout_info.voucher_applied,
                    "total_due": checkout_info.total_due,
                    "cart_total_foreign": checkout_info.cart_total_foreign,
                    "shipping_cost_amount_foreign": checkout_info.shipping_cost_amount_foreign,
                    "discount_amount_foreign": checkout_info.discount_amount_foreign,
                    "tax_amount_foreign": checkout_info.tax_amount_foreign,
                    "applied_voucher_amount_foreign": checkout_info.applied_voucher_amount_foreign,
                    "total_due_foreign": checkout_info.total_due_foreign,
                    "locked_exchange_rate": checkout_info.locked_exchange_rate,
                    "currency_code": request.session.get('foreign_currency_code', 'HKD'),
                }
                if proforma_invoice:
                    for key, value in field_mapping_defaults.items():
                        setattr(proforma_invoice, key, value)
                    proforma_invoice.save()
                else:
                    proforma_invoice = ProformaInvoice.objects.create(cart=cart, **field_mapping_defaults)
                
                # 1. High-Security Order Number Auto Generation Loop (Sqids Fix)
                if not proforma_invoice.proforma_order_number:
                    sqids = Sqids(min_length=6, alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")
                    country_prefix = proforma_invoice.country if proforma_invoice.country else "XX"
                    
                    # 🌟 FIXED: Remove '.int' and pass the integer ID directly into the list bracket
                    invoice_num = f"{country_prefix}-{sqids.encode([proforma_invoice.id])}"
                    
                    proforma_invoice.proforma_order_number = invoice_num
                    proforma_invoice.save()
                else:
                    invoice_num = proforma_invoice.proforma_order_number

                # 2. Sync Address Book Configuration Checks for Tracked Locations
                if checkout_info.destination_source == "ADDRESS_BOOK" and checkout_info.address_id:
                    address_record = Address.objects.filter(id=checkout_info.address_id).first()
                    if address_record:
                        proforma_invoice.is_default_address = address_record.is_default
                        proforma_invoice.save()

                # 🎯 3. CONTEXT-AWARE ADDRESS PERSISTENCE ENGINE (UPGRADE MODULE)
                if user.is_authenticated and proforma_invoice_form.cleaned_data.get('save_to_address_book'):
                    if display_mode in ["PHYSICAL", "PHYSICAL_AND_VOUCHER"]:
                        user_profile, _ = UserProfile.objects.get_or_create(user=user)
                        
                        # Determine baseline default constraints for new cards
                        has_preexisting_default = Address.objects.filter(profile=user_profile, is_default=True).exists()
                        target_default_flag = False if has_preexisting_default else True

                        # ─────────────────────────────────────────────────────────
                        # 🔄 JOURNEY (i): User checked out using a Saved Address Card ➔ UPDATE EXISTING
                        # ─────────────────────────────────────────────────────────
                        if checkout_info.destination_source == "ADDRESS_BOOK" and checkout_info.address_id:
                            # Fetch the exact existing address row owned by this specific member profile
                            address_record = Address.objects.filter(id=int(checkout_info.address_id), profile=user_profile).first()
                            
                            if address_record:
                                # Surgically overwrite fields on the existing row instance
                                address_record.recipient_first_name = proforma_invoice.recipient_first_name
                                address_record.recipient_last_name = proforma_invoice.recipient_last_name
                                address_record.mobile_area = proforma_invoice.recipient_mobile_area
                                address_record.mobile_number = proforma_invoice.recipient_mobile_number
                                address_record.address_line_1 = proforma_invoice.address_line_1
                                address_record.address_line_2 = proforma_invoice.address_line_2
                                address_record.city = proforma_invoice.city
                                address_record.state_province_region = proforma_invoice.state_province_region
                                address_record.country = proforma_invoice.country
                                address_record.postal_code = proforma_invoice.postal_code
                                address_record.google_place_id = proforma_invoice.google_place_id
                                address_record.latitude = proforma_invoice.latitude
                                address_record.longitude = proforma_invoice.longitude
                                address_record.save()
                                print(f"🔄 ADDRESS BOOK UPGRADE: Successfully updated existing card ID {address_record.id}")

                        # ─────────────────────────────────────────────────────────
                        # ✨ JOURNEY (ii): User checked out via Dropdown Destinations ➔ CREATE NEW
                        # ─────────────────────────────────────────────────────────
                        else:
                            new_address = Address.objects.create(
                                profile=user_profile,
                                recipient_first_name=proforma_invoice.recipient_first_name,
                                recipient_last_name=proforma_invoice.recipient_last_name,
                                mobile_area=proforma_invoice.recipient_mobile_area,
                                mobile_number=proforma_invoice.recipient_mobile_number,
                                address_line_1=proforma_invoice.address_line_1,
                                address_line_2=proforma_invoice.address_line_2,
                                city=proforma_invoice.city,
                                state_province_region=proforma_invoice.state_province_region,
                                country=proforma_invoice.country,
                                postal_code=proforma_invoice.postal_code,
                                google_place_id=proforma_invoice.google_place_id,
                                latitude=proforma_invoice.latitude,
                                longitude=proforma_invoice.longitude,
                                is_default=target_default_flag
                            )
                            print(f"✨ ADDRESS BOOK SAVE: Generated fresh entry card ID {new_address.id}")

                # 4. Process Unified HTMX AJAX Redirect Routing
                if request.headers.get("HX-Request"):
                    response = render(request, 'store/checkout.html', {'proforma_invoice_form': proforma_invoice_form})
                    response["HX-Redirect"] = f"/carts/place_order/{invoice_num}/"
                    return response
                    
                return redirect("place_order", proforma_invoice_no=invoice_num)
        
            except Exception as e:
                print(f"Checkout system processing failure: {str(e)}")
                messages.error(request, "系統錯誤，請稍後再試 | Execution Exception.")

        else:
            # 🎯 DETAILED DEBUG LAYER: Print out the exact failures directly to your terminal screen
            print("\n==================================================")
            print("❌ FORM VALIDATION FAILED!")
            print("Display Mode:", display_mode)
            print("Raw POST Data:", dict(request.POST))
            print("Cleaned Data up to failure:", proforma_invoice_form.cleaned_data)
            print("Explicit Errors Matrix:")
            for field, error_list in proforma_invoice_form.errors.items():
                print(f"   👉 Field [{field}]: {error_list}")
            print("==================================================\n")
            
            messages.error(request, "請確認填寫內容 | Please check input details.")

    # -------------------------------------------------------------
    # 3. GET INITIAL VIEW SETUP LIFECYCLE
    # -------------------------------------------------------------
    else:
        initial_data = {
            "email": user.email if user.is_authenticated else None,
            "recipient_first_name": address.recipient_first_name if address else None,
            "recipient_last_name": address.recipient_last_name if address else None,
            "recipient_mobile_area": address.mobile_area if address else None,
            "recipient_mobile_number": address.mobile_number if address else None,
            "address_line_1": address.address_line_1 if address else None,
            "address_line_2": address.address_line_2 if address else None,
            "city": address.city if address else None,
            "state_province_region": state,
            "country": country,
            "postal_code": address.postal_code if address else None,
            "google_place_id": address.google_place_id if address else checkout_info.address_id,
            "latitude": address.latitude if address else None,
            "longitude": address.longitude if address else None,
            "is_verified_by_google": True if address else False,
        }
        proforma_invoice_form = ProformaInvoiceForm(initial=initial_data, display_mode=display_mode)

    # 💡 FALL-THROUGH SAFETY POINT: If the POST form fails validation,
    # execution skips the "else:" block below and moves straight to widget attributes styling and rendering.
    # -------------------------------------------------------------
    # 4. MUTUAL WIDGET FORMATTING & RENDER FALLBACK
    # -------------------------------------------------------------
    if "country" in proforma_invoice_form.fields:
        proforma_invoice_form.fields["country"].widget.attrs["readonly"] = True
        proforma_invoice_form.fields["country"].widget.attrs["class"] = "bg-base-200 pointer-events-none"
    if "state_province_region" in proforma_invoice_form.fields and country == "CN":
        proforma_invoice_form.fields["state_province_region"].widget.attrs["readonly"] = True
        proforma_invoice_form.fields["state_province_region"].widget.attrs["class"] = "bg-base-200 pointer-events-none"
    
    context = {
        "proforma_invoice_form": proforma_invoice_form,
        "page_title": "Checkout｜結算",
        "cart_items": cart_items,
        "main_title": "Order Form｜訂單訊息",
        "sub_title_1": "Looking forward to seeing you!｜寶貝們期待著早日與您會面！",
        "bread_crumb_1": "首頁｜Home",
        "bread_crumb_2": "Order Details｜訂單訊息",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/carts/checkout",
        "cart_total": checkout_info.cart_total,
        "shipping_cost": checkout_info.shipping_cost,
        "discount_amount": checkout_info.discount_amount,
        "voucher_applied": checkout_info.voucher_applied,
        "tax_amount": checkout_info.tax_amount,
        "total_due": checkout_info.total_due,
        "foreign_currency_code": current_currency_code,
        "is_integer": is_integer,
        "foreign_currency_symbol": foreign_currency_symbol,
        "cart_total_foreign": checkout_info.cart_total_foreign,
        "shipping_cost_amount_foreign": checkout_info.shipping_cost_amount_foreign,
        "discount_amount_foreign": checkout_info.discount_amount_foreign,
        "tax_amount_foreign": checkout_info.tax_amount_foreign,
        "applied_voucher_amount_foreign": checkout_info.applied_voucher_amount_foreign,
        "total_due_foreign": checkout_info.total_due_foreign,
        "locked_exchange_rate": checkout_info.locked_exchange_rate,
        "display_mode": display_mode,
        "is_china_order": (country == "CN"),
        "destination_source": checkout_info.destination_source,
    }
    
    _, _, _ = update_total_payable(request, cart)

    def get_session_fx(key, nested_key, fallback_val):
        val = request.session.get(key, {}).get(nested_key, None)
        return val if val is not None else fallback_val

    context.update({
        "physical_products_total_foreign": get_session_fx("shipping_data", "physical_products_total_foreign", context.get("physical_products_total_foreign")),
        "shipping_cost_foreign": get_session_fx("shipping_data", "shipping_cost_foreign", context.get("shipping_cost_foreign")),
        "offer_applied_foreign": get_session_fx("offer_applied", "discount_amount_foreign", context.get("offer_applied_foreign")),
        "voucher_applied_foreign": get_session_fx("applied_voucher", "applied_voucher_amount_foreign", context.get("voucher_applied_foreign")),
    })

    print("checkoutInfo: ", checkout_info)

    return render(request, "store/checkout.html", context)


# @require_POST
# def calculate_tax_duty_api(request):
#     cart = Cart.objects.get(user=request.user)
    
#     # 1. Get destination
#     destination = request.POST.get("destination")
    
#     if destination.isdigit():
#         destination_id = int(destination)
#         address = Address.objects.get(id=destination_id)
#         destination = address.country

#     if any(item[0] == destination for item in (DESTINATIONS_GLOBAL + DESTINATIONS_GREATER_CHINA)):
#         print(f"tax required for {destination}!")
#     else:
#         return HttpResponse(status=204)

#     # 2. Get taxable total (physical products only)
#     taxable_total = cart.get_physical_products_subtotal()

#     # Map country codes to their respective logic
#     TAX_MAP = {
#         'HK': calculate_free_port_tax,
#         'MO': calculate_free_port_tax,
#         'AU': calculate_australia_tax,
#         'NZ': calculate_new_zealand_tax,
#         'SG': calculate_singapore_tax,
#         'MY': calculate_malaysia_tax,
#         'KR': calculate_korea_tax,
#         'JP': calculate_japan_tax,
#         'TW': calculate_taiwan_tax,
#     }

#     # 3. Separate logic for your 9 destinations
#     # This is where you will call your specific backend tax functions later
#     tax_amount = 0
#     duty_amount = 0

#     # Execute the specific function
#     calc_func = TAX_MAP.get(destination)
#     if calc_func:
#         # result = calc_func(taxable_total, ...) # Pass necessary rates/costs
#         # Update your session and return HTMX partial
#         pass
    
#     if destination in ['AU', 'NZ']:
#         # Example: Simplified 10% GST logic
#         tax_amount = taxable_total * Decimal('0.10')
    
#     # 4. Store in session (to match your existing pattern)
#     request.session['tax_handling'] = {
#         "tax_amount": f"{tax_amount:.2f}",
#         "duty_amount": f"{duty_amount:.2f}",
#         "destination_code": destination,
#         "is_calculated": True,
#     }

#     # 5. Return updated summary and unlock checkout button if applicable
#     # We leverage your existing total payable calculation logic
#     return update_total_payable(request, cart) # Returns the OOB summary update


# def get_compliance_fields(request):
#     country_code = request.GET.get('country')
#     context = {}
    
#     if country_code == 'TW':
#         context['label'] = "Taiwan ID / EZ WAY Number｜身分證字號"
#         context['placeholder'] = "e.g. A123456789"
#         context['field_name'] = "destination_tax_id"
#     elif country_code == 'KR':
#         context['label'] = "Korea PCCC｜個人海關通關代碼"
#         context['placeholder'] = "e.g. P123456789012"
#         context['field_name'] = "destination_tax_id"
#     else:
#         return HttpResponse("") # Return nothing for HK, AU, etc.

#     return render(request, 'store/partials/compliance_field_snippet.html', context)
