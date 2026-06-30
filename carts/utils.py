import math
from decimal import Decimal, InvalidOperation
from accounts.data import DESTINATIONS_GLOBAL, INTEGER_CURRENCIES
from accounts.models import Address, CustomerVoucher, Perk, CustomerVoucher, UserPerk
from .models import ShippingCharge, CartItem
from store.models import ProductVariation
import json
from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import intcomma
from django.template.defaultfilters import floatformat
from django.template.loader import render_to_string
from accounts.data import CURRENCY_SYMBOL
from django.http import HttpResponse
from django.db.models import F, Sum
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from decimal import Decimal, ROUND_HALF_UP
from orders.utils import get_current_rate
from django.utils import timezone
import time
from datetime import timedelta
from accounts.data import DESTINATIONS_GLOBAL, DESTINATIONS_GREATER_CHINA, DESTINATIONS_MAINLAND_CHINA, CURRENCY_SYMBOL
from accounts.evaluators import PerkEvaluator
from django.db import transaction
import socket
from django.core.exceptions import ValidationError



def clean_decimal(val):
    """Safely normalizes raw mixed text input variables into Decimals."""
    if not val:
        return Decimal('0.00')
    try:
        return Decimal(str(val).replace(",", ""))
    except (ValueError, TypeError):
        return Decimal('0.00')


def round_up_to_nearest_unit(number, unit):
    """
    Round up to the next multiple of the given unit
    """
    division_result = number / unit
    if division_result % unit != 0:
        division_result = math.ceil(division_result)
    
    return division_result * unit


def get_available_services(method, region, destination_id):
    if method == 'dropdown':
        if region == 'china':
            available_services = ShippingCharge.objects.filter(zone=destination_id, is_active=True)
        else:
            available_services = ShippingCharge.objects.filter(country_code=destination_id, is_active=True)
    elif method == 'saved_address':
        address = Address.objects.get(id=destination_id)
        if address.country == "CN":
            province = address.state_province_region
            available_services = ShippingCharge.objects.filter(zone=province, is_active=True)
        else:
            country = address.country
            available_services = ShippingCharge.objects.filter(country_code=country, is_active=True)

    return available_services


def calculate_shipping_cost(request, physical_items, available_services):
    total_standard_shipping_charge = Decimal(0)
    total_economy_shipping_charge = Decimal(0)
    single_package_items = []
    bulk_package_items = []
    
    # sort out SINGLE_package or BULK_package
    for item in physical_items:
        quantity = int(item.quantity)
        product_variation = ProductVariation.objects.get(id=item.product_variation.pk)
        if not product_variation.with_shipping:
            if product_variation.single_pack:
                single_package_items.append([product_variation, quantity])
            else:
                bulk_package_items.append([product_variation, quantity])

    # calculate costs - SINGLE packages
    if len(single_package_items) > 0:
        total_single_package_standard_charge = Decimal(0)
        total_single_package_economy_charge = Decimal(0)
        for item in single_package_items:
            single_package_charges = single_package_shipping_cost_selection(item, available_services)
            single_package_standard_charge = single_package_charges["standard_cost"]["total_charge"]
            single_package_economy_charge = single_package_charges["economy_cost"]["total_charge"]
            if single_package_standard_charge is not None:
                total_standard_shipping_charge += single_package_standard_charge
                total_single_package_standard_charge += single_package_standard_charge
            if single_package_economy_charge is not None:
                total_economy_shipping_charge += single_package_economy_charge
                total_single_package_economy_charge += single_package_economy_charge

    # calculate costs - BULK packages
    if len(bulk_package_items) > 0:
        bulk_package_charges = bulk_package_shipping_cost_selection(bulk_package_items, available_services, 2000)
        bulk_package_standard_charge = bulk_package_charges["standard_cost"]["total_charge"]
        bulk_package_economy_charge = bulk_package_charges["economy_cost"]["total_charge"]

        if bulk_package_standard_charge is not None:
            total_standard_shipping_charge += bulk_package_standard_charge
        if bulk_package_economy_charge is not None:
            total_economy_shipping_charge += bulk_package_economy_charge

    shipping_charge = min(total_standard_shipping_charge, total_economy_shipping_charge) \
                         if total_standard_shipping_charge != 0 \
                         and total_economy_shipping_charge != 0 \
                         else max(total_standard_shipping_charge, total_economy_shipping_charge)
    print("caluclated shipping cost: ", shipping_charge)
    return shipping_charge


def single_package_shipping_cost_selection(item, services):
    standard_cost_selection = []
    economy_cost_selection = []
    standard_cost = Decimal(0)
    economy_cost = Decimal(0)

    for service in services:
        # if LARGE package, exclude the for_small_package services (skip calculation)
        if item[0].weight > 2000 and service.for_small_package:
            continue

        min_charge_weight = service.min_charge_weight
        extra_weight = round_up_to_nearest_unit((item[0].weight - min_charge_weight), service.add_cost_weight)
        if extra_weight < 0:
            extra_weight = 0
        min_charge = service.min_charge
        extra_charge = service.add_cost_unit_price * Decimal(str(extra_weight).replace(",", "")) / service.add_cost_weight
        total_charge_per_unit = min_charge + extra_charge + service.other_fee
        total_charge = total_charge_per_unit * item[1]
        charge_info = {
            "service": service,
            "total_charge": total_charge,
        }
        if service.is_standard or service.is_express:
            standard_cost_selection.append(charge_info)
        elif service.is_economical:
            economy_cost_selection.append(charge_info)
        print(service, ", single_package_total_charge: ", total_charge)
    
    # STANDARD
    if len(standard_cost_selection) > 0:
        standard_cost = min(standard_cost_selection, key=lambda _item: _item["total_charge"])
    elif len(standard_cost_selection) == 0:
        standard_cost = {"service": None, "total_charge": None,}

    # ECONOMY
    if len(economy_cost_selection) > 0:
        economy_cost = min(economy_cost_selection, key=lambda _item: _item["total_charge"])
    elif len(economy_cost_selection) == 0:
        economy_cost = {"service": None, "total_charge": None,}

    return {"standard_cost": standard_cost, "economy_cost": economy_cost}


def bulk_package_shipping_cost_selection(bulk_package_items, available_services, weight_threshold):
    standard_cost_selection = []
    economy_cost_selection = []
    standard_cost = Decimal(0)
    economy_cost = Decimal(0)
    total_weight = 0
    for item in bulk_package_items:
        total_weight += item[0].weight * item[1]

    full_package_num = total_weight // weight_threshold
    last_package_weight = total_weight % weight_threshold

    for service in available_services:
        # If less than 2kg, ONE package ONLY
        if total_weight <= weight_threshold:
            extra_weight = round_up_to_nearest_unit((total_weight - service.min_charge_weight), service.add_cost_weight)
            if extra_weight < 0:
                extra_weight = 0
            min_charge = service.min_charge
            extra_charge = service.add_cost_unit_price * Decimal(str(extra_weight).replace(",", "")) / service.add_cost_weight
            total_charge = min_charge + extra_charge + service.other_fee
        else:
        # If more than ONE package is needed (total_weight > 2kg)
            # if service is for small packages < 2kg
            if service.for_small_package:
                extra_weight = weight_threshold - service.min_charge_weight
                single_full_package_charge = service.min_charge + service.add_cost_unit_price * Decimal(str(extra_weight).replace(",", "")) / service.add_cost_weight + service.other_fee
                total_full_package_charge = single_full_package_charge * full_package_num
                # LAST package
                if last_package_weight > 0:
                    last_package_extra_weight = round_up_to_nearest_unit(last_package_weight, service.add_cost_weight)
                last_package_charge = service.min_charge + service.add_cost_unit_price * Decimal(str(last_package_weight).replace(",", "")) / service.add_cost_weight + service.other_fee

                total_charge = total_full_package_charge + last_package_charge
            else:
                extra_weight = round_up_to_nearest_unit((total_weight - service.min_charge_weight), service.add_cost_weight)
                total_charge = service.min_charge + service.add_cost_unit_price * Decimal(str(extra_weight).replace(",", "")) / service.add_cost_weight + service.other_fee
        
        charge_info = {
            "service": service,
            "total_charge": total_charge,
        }
        if service.is_standard or service.is_express:
            standard_cost_selection.append(charge_info)
        elif service.is_economical:
            economy_cost_selection.append(charge_info)
        print(service, ", bulk_package_total_charge: ", total_charge)
    
    # STANDARD
    if len(standard_cost_selection) > 0:
        standard_cost = min(standard_cost_selection, key=lambda _item: _item["total_charge"])
    elif len(standard_cost_selection) == 0:
        standard_cost = {"service": None, "total_charge": None,}

    # ECONOMY
    if len(economy_cost_selection) > 0:
        economy_cost = min(economy_cost_selection, key=lambda _item: _item["total_charge"])
    elif len(economy_cost_selection) == 0:
        economy_cost = {"service": None, "total_charge": None,}

    return {"standard_cost": standard_cost, "economy_cost": economy_cost}


def htmx_invalid_offer_response(request, title, text, icon="error"):
    response = render(request, 'store/partials/offer_input.html', {})
    response['HX-Trigger'] = json.dumps({
        "errorMssg": {  # Ensure this matches your JS event listener
            "title": title,
            "text": text,
            "icon": icon
        }
    })
    return response


def htmx_invalid_offer_update_response(request, title, text, icon="error"):
    offer_input_html = render_to_string('store/partials/offer_input.html', {}, request=request)
    trigger_data = {  # Ensure this matches your JS event listener
        "title": title,
        "text": text,
        "icon": icon
    }
    return offer_input_html, trigger_data


def handle_perk_status(request, status, cart, code, perk, formatted_min_spend, offer_context=None):
    match status:
        case "VALID" if Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", "")) < Decimal(str(perk.safe_min_spending).replace(",", "")):
            return htmx_invalid_offer_response(request, "Minimum Spend (Excl. Voucher Items) Not Met\n未達最低消費金額(現金禮券除外)", f"Sorry, this offer requires a minimum spending of CNY { formatted_min_spend }. Please add more items to your cart to qualify.<br>很抱歉，此優惠需消費滿 { formatted_min_spend } 元方可使用。請再多選購一些商品以符合資格。")
        
        case "OUT_OF_STOCK":
            return htmx_invalid_offer_response(request, "Limit Reached\n優惠名額已滿", "All available offers have been claimed.<br>此優惠名額已滿，感謝您的支持。")
        
        case "ALREADY_USED":
            return htmx_invalid_offer_response(request, "Already Redeemed\n此優惠碼已使用", "This promo code has already been used.<br>您已使用過此優惠碼。")
        
        case "NO_DOB_DATA":
            return htmx_invalid_offer_response(request, "Missing birthday information\n缺少您的生日資訊", "We don’t have your birthday data, so this promo cannot be applied.<br>我們沒有您的生日資料，因此無法套用此優惠。")

        case "FEMALE_ONLY" :
            return htmx_invalid_offer_response(request, "Ladies only\n女士專屬限定", "This promo code is only available for female members.<br>此優惠碼僅限女性會員使用。")
        
        case "EXPIRED" | "THIS_BIRTHDAY_PERK_EXPIRED" | "NEW_MEMBER_PERK_EXPIRED":
            return htmx_invalid_offer_response(request, "Offer Epxired\n優惠已過期", "Sorry, this offer has expired.<br>抱歉！您輸入的優惠碼已過期。")

        case "VALID": 
        # 1. 🔒 HARDEN CALCULATIONS: Explicitly cast parameters to Decimals to clear floating point drift
            discount_type = perk.discount_type
            discount_rate_or_amount = Decimal(str(perk.discount_value).replace(",", ""))
            cart_base_total = Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", ""))
            
            if discount_type == 'percentage':
                discount_amount = cart_base_total * discount_rate_or_amount / Decimal('100')
            elif discount_type == 'fixed_amount':
                discount_amount = min(discount_rate_or_amount, cart_base_total)
            else:
                discount_amount = Decimal('0.00')

            is_integer, currency_code = get_currency_format(request)
            rate = Decimal(str(request.session.get('locked_rate', '1.0000')).replace(",", ""))
            fx_offer = quantize_amount(discount_amount * rate, currency_code)

            # 2. 💡 THE FIX: Map 'is_oob': True to trigger the template's dynamic hx-swap-oob attribute!
            context = {
                'active_code': code, 
                'perk_code': perk.code, 
                'discount': intcomma(f"{discount_amount:.2f}"),
                'offer_applied_foreign': format_fx_value(fx_offer, currency_code),
                'foreign_currency_symbol': CURRENCY_SYMBOL.get(currency_code, '$'),
                'is_integer': is_integer,
                'is_oob': True  # <-- Direct target structural flag enforcer
            }
            
            # This now successfully compiles with the necessary hx-swap-oob="true" outer block string!
            offer_wrapper_oob = render_to_string('store/partials/offer_active.html', context, request=request)

            # 3. Build side panel summary table metrics indicators
            foreign_currency_symbol = CURRENCY_SYMBOL.get(currency_code, '$')
            formatted_foreign = format_fx_value(fx_offer, currency_code)
            
            pricing_oob = f'''
                <span id="summary-discount" hx-swap-oob="true">¥ ({intcomma(f"{discount_amount:.2f}")})</span>
                <span id="discount_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({ formatted_foreign })</span>
            '''

            # 4. Save accurate quantized variables securely inside the user session cache maps
            request.session["offer_applied"] = {
                "offer_code": code,
                "discount_amount": intcomma(f"{discount_amount:.2f}"),
                "discount_amount_foreign": formatted_foreign,
            }
            request.session.modified = True

            # 5. Append remaining layouts to run calculation ripple effects seamlessly
            voucher_oob = update_applied_voucher(request, cart)
            total_oob, amount, amount_foreign = update_total_payable(request, cart)

            # 6. Combine and serve safely as an isolated OOB block response
            final_payload = offer_wrapper_oob + pricing_oob + voucher_oob + total_oob

            broadcast_cart_change(request)
            return HttpResponse(final_payload)
            
        case _:
            return htmx_invalid_offer_response(request, "Invalid", "Error status matching case pattern.")


def htmx_invalid_voucher_response(request, voucher_balance, title, text, icon="error"):
    context = {"cash_voucher_balance": voucher_balance}
    response = render(request, 'store/partials/voucher_input.html', context)
    response['HX-Trigger'] = json.dumps({
        "erroMssg": {  # Ensure this matches your JS event listener
            "title": title,
            "text": text,
            "icon": icon
        }
    })
    return response


def recalculate_cart_totals(cart):
    new_cart_total_count = cart.get_items_count()
    new_cart_grand_total = cart.get_cart_total()
    return new_cart_total_count, new_cart_grand_total


def update_header_cart_summary(cart):
    oob_updates = []
    new_cart_total_count, formatted_new_cart_grand_total = recalculate_cart_totals(cart)
    item_str = "Items" if new_cart_total_count > 1 else "Item"

    header_num_icon_html = f'''
        <span id="cart_count_icon" hx-swap-oob="true" 
              class="badge badge-sm indicator-item badge-primary cart-update-pop">
            { new_cart_total_count }
        </span>
    '''
    
    header_qty_html = f'<b id="cart_count" hx-swap-oob="true" class="font-bold">{ new_cart_total_count } {item_str}</b>'
    header_total_html = f'<b id="cart_sub_total" hx-swap-oob="true" class="font-bold">CNY ¥ { formatted_new_cart_grand_total }</b>'
    oob_updates.extend([header_num_icon_html, header_qty_html, header_total_html])
    return "".join(filter(None, oob_updates))


def calculate_foreign_amount(request, cny_amount):
    foreign_currency_code = request.COOKIES.get('user_currency', 'HKD')
    foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]
    is_integer = True if foreign_currency_code in INTEGER_CURRENCIES else False
    locked_rate = request.session.get('locked_rate')
    formatted_foreign = intcomma(f"{(cny_amount * Decimal(str(locked_rate).replace(",", ""))):.0f}") if is_integer else intcomma(f"{(cny_amount * Decimal(str(locked_rate).replace(",", ""))):.2f}")
    return foreign_currency_symbol, formatted_foreign


def get_row_oob(row_id, label_en, label_zh, id_local, id_foreign, amount=0.00, amount_foreign=0.00, symbol="", is_integer=False, show=True):
    """Surgically formats dynamic table row updates for out-of-band HTMX swaps."""
    try:
        clean_amount = Decimal(str(amount).replace(",", "")) if amount is not None else Decimal("0.00")
    except (ValueError, TypeError, InvalidOperation):
        clean_amount = Decimal("0.00")

    hidden_class = "" if show else "hidden"
    val_local = f"¥ {intcomma(f'{clean_amount:.2f}')}"
    
    if amount_foreign is not None and show:
        try:
            clean_foreign = Decimal(str(amount_foreign).replace(",", ""))
            val_foreign = f"{symbol} {intcomma(f'{clean_foreign:.0f}')}" if is_integer else f"{symbol} {intcomma(f'{clean_foreign:.2f}')}"
        except (ValueError, TypeError, InvalidOperation):
            zero_str = "0" if is_integer else "0.00"
            val_foreign = f"{symbol} {zero_str}"
    else:
        zero_str = "0" if is_integer else "0.00"
        val_foreign = f"{symbol} {zero_str}" if show else ""

    return f"""
        <tr id="{row_id}" class="font-normal {hidden_class}" hx-swap-oob="true">
            <td class="py-1 text-left text-xs/4">{label_en}<br>{label_zh}</td>
            <td class="py-1 mr-2 text-right text-sm">
                <span id="{id_local}">{val_local}</span>
            </td>
            <td class="py-1 text-right text-info-content text-sm">
                <span id="{id_foreign}">{val_foreign}</span>
            </td>
        </tr>
    """.strip().replace("\n", "").replace("    ", "")


def get_cash_voucher_balance(request):
    """Calculates true unallocated voucher funds remaining in a user's wallet."""
    if not request.user.is_authenticated:
        return Decimal('0.00')
    return CustomerVoucher.objects.filter(
        owner=request.user, 
        is_used=False,
        balance__gt=0
    ).aggregate(total=Sum('balance'))['total'] or Decimal('0.00')


def update_applied_voucher(request, cart):
    if not cart or cart.get_items_count() == 0:
        return ""
    
    voucher_applied = Decimal(str(request.session.get("applied_voucher", {}).get("applied_voucher_amount", 0)).replace(",", ""))
    voucher_balance = get_cash_voucher_balance(request)
    new_total_payable, new_total_payable_foreign = get_grand_total_before_voucher(request, cart)
    updated_oob_string = []

    if voucher_applied > 0 and new_total_payable < voucher_applied:
        updated_voucher_context = {'voucher_applied': new_total_payable}
        formatted_new_voucher_applied = intcomma(f"{new_total_payable:.2f}")
        formatted_new_remaining_balance = intcomma(f"{(voucher_balance - new_total_payable):.2f}")

        request.session["applied_voucher"]["applied_voucher_amount"] = str(new_total_payable)
        request.session["applied_voucher"]["applied_voucher_amount_foreign"] = str(new_total_payable_foreign)

        updated_voucher_html = render_to_string('store/partials/voucher_active.html', updated_voucher_context, request=request)
        updated_voucher_oob = f'<div id="voucher-form-wrapper" hx-swap-oob="true">{updated_voucher_html}</div>'
        oob_html_1 = f'<span id="voucher-balance" hx-swap-oob="true" class="badge badge-outline">CNY {formatted_new_remaining_balance}</span>'

        foreign_currency_symbol, formatted_voucher_applied_foreign = calculate_foreign_amount(request, new_total_payable)
        oob_html_2 = f'''
            <span id="summary_voucher_applied" hx-swap-oob="true">¥ ({formatted_new_voucher_applied})</span>
            <span id="summary_voucher_applied_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({formatted_voucher_applied_foreign})</span>
        '''
        updated_oob_string.append(updated_voucher_oob)
        updated_oob_string.append(oob_html_1)
        updated_oob_string.append(oob_html_2)
        final_oob = "".join(filter(None, updated_oob_string))
        return final_oob

    elif not voucher_applied:
        max_voucher_enterable = min(voucher_balance, new_total_payable)
        updated_voucher_context = {"max_voucher_enterable": max_voucher_enterable}
        updated_voucher_html = render_to_string('store/partials/voucher_input.html', updated_voucher_context, request=request)
        updated_voucher_oob = f'<div id="voucher-form-wrapper" hx-swap-oob="true">{updated_voucher_html}</div>'

        return updated_voucher_oob
    
    else:
        return ""


def get_grand_total_before_voucher(request, cart):
    """Computes absolute raw transactional limits using numeric Decimals."""
    is_integer, foreign_currency_code = get_currency_format(request)
    rate = Decimal(str(request.session.get('locked_rate', '1.0000')).replace(",", ""))

    cart_total_ex_voucher = Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", ""))
    
    shipping_data = request.session.get('shipping_data', {})
    shipping_cost = Decimal(str(shipping_data.get('shipping_cost', '0.00')).replace(",", "")) if shipping_data else Decimal('0.00')
    tax = Decimal(str(request.session.get('tax_amount', '0.00')).replace(",", ""))
    
    discount_data = request.session.get('offer_applied', {})
    discount_amount = Decimal(str(discount_data.get('discount_amount', '0.00')).replace(",", ""))

    # Compute absolute global totals using clean unrounded values
    grand_total_cny = max((cart_total_ex_voucher + shipping_cost + tax) - discount_amount, Decimal('0.00'))
    grand_total_foreign = quantize_amount(grand_total_cny * rate, foreign_currency_code)

    return grand_total_cny, grand_total_foreign


def get_currency_precision(currency_code: str) -> int:
    return 0 if currency_code.upper() in INTEGER_CURRENCIES else 2


def quantize_amount(value: Decimal, currency_code: str) -> Decimal:
    precision = get_currency_precision(currency_code)
    decimal_val = Decimal(str(value).replace(",", ""))
    if precision == 0:
        return decimal_val.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return decimal_val.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_fx_value(value: Decimal, currency_code: str) -> str:
    precision = get_currency_precision(currency_code)
    return intcomma(f"{value:.{precision}f}")


def update_total_payable(request, cart):
    """
    Component-by-Component Summation Ledger.
    Sums up the pre-quantized model subtotals to derive the Grand Total Due.
    This guarantees absolute vertical and horizontal consistency on all page loads!
    """
    if not cart or cart.get_items_count() == 0:
        return "", "0.00", "0"

    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(foreign_currency_code, '$')
    rate = Decimal(str(request.session.get('locked_rate', '1.0000')).replace(",", ""))
    
    def get_clean_decimal_from_session(key, nested_key):
        raw_val = request.session.get(key, {}).get(nested_key, 0)
        try:
            return Decimal(str(raw_val).replace(",", ""))
        except (ValueError, TypeError):
            return Decimal("0.00")

    # 1. Fetch unrounded core values straight from your session configurations
    shipping_cny = get_clean_decimal_from_session("shipping_data", "shipping_cost")
    offer_cny = get_clean_decimal_from_session("offer_applied", "discount_amount")
    voucher_applied_cny = get_clean_decimal_from_session("applied_voucher", "applied_voucher_amount")
    
    cny_subtotal = Decimal(str(cart.get_cart_total()).replace(",",""))
    cny_payable = max(cny_subtotal + shipping_cny - offer_cny - voucher_applied_cny, Decimal('0.00'))

    # 2. Extract perfectly aligned subtotals straight from our new model properties
    def clean_model_fx(val_str):
        return Decimal(str(val_str).replace(",", ""))

    fx_physical = clean_model_fx(cart.get_physical_products_subtotal_foreign(foreign_currency_code, rate))
    fx_electronic = clean_model_fx(cart.get_e_products_subtotal_foreign(foreign_currency_code, rate))
    fx_voucher_purchase = clean_model_fx(cart.get_voucher_products_subtotal_foreign(foreign_currency_code, rate))
    
    fx_shipping = quantize_amount(shipping_cny * rate, foreign_currency_code)
    fx_offer = quantize_amount(offer_cny * rate, foreign_currency_code)
    fx_voucher_applied = quantize_amount(voucher_applied_cny * rate, foreign_currency_code)

    # 3. 🎯 COMPUTE THE GRAND TOTAL DUE FROM THE BALANCED ATOMIC PIECES
    fx_payable = (fx_physical + fx_electronic + fx_voucher_purchase + fx_shipping) - fx_offer - fx_voucher_applied
    fx_payable = max(fx_payable, Decimal('0'))

    # 4. Save accurate quantized values back into user session maps safely
    if 'shipping_data' not in request.session:
        request.session['shipping_data'] = {}
    request.session['shipping_data']['shipping_cost_foreign'] = format_fx_value(fx_shipping, foreign_currency_code)
    request.session['shipping_data']['physical_products_total_foreign'] = format_fx_value(fx_physical, foreign_currency_code)
    
    if 'offer_applied' in request.session:
        request.session['offer_applied']['discount_amount_foreign'] = format_fx_value(fx_offer, foreign_currency_code)
    if 'applied_voucher' in request.session:
        request.session['applied_voucher']['applied_voucher_amount_foreign'] = format_fx_value(fx_voucher_applied, foreign_currency_code)
    request.session.modified = True

    formatted_net_total_payable = intcomma(f"{cny_payable:.2f}")
    formatted_net_total_payable_foreign = format_fx_value(fx_payable, foreign_currency_code)

    total_due_html = f'''
        <span id="total_payable_amount" hx-swap-oob="true">¥ {formatted_net_total_payable}</span>
        <span id="total_payable_amount_foreign" hx-swap-oob="true">{foreign_currency_symbol} {formatted_net_total_payable_foreign}</span>
    '''
    return total_due_html, formatted_net_total_payable, formatted_net_total_payable_foreign


def get_currency_format(request):
    current_currency_code = request.COOKIES.get('user_currency', 'HKD')
    is_integer = True if current_currency_code in INTEGER_CURRENCIES else False
    return is_integer, current_currency_code


def broadcast_cart_change(request):
    """Helper to notify open, dormant tabas to update their UI."""
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        if request.user.is_authenticated:
            group_name = f"cart_user_{request.user.id}"
        else:
            # Fallback to session key for guest sessions
            if not request.session.session_key:
                request.session.create()
            group_name = f"cart_session_{request.session.session_key}"
            
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "cart_update_message",
                "action": "refresh_cart"
            }
        )
    except Exception as e:
        print(f"WebSocket broadcast skipped: {e}")


def get_or_lock_checkout_rate(request, currency_code):
    """
    Get or lock the latest rate for each user (session). 
    Bypasses external lookups for base CNY currency with a strict 1.0000 multiplier.
    """
    currency_code = currency_code.upper() # Ensure consistency
    
    # 💡 BYPASS RULE FOR BASE CURRENCY
    if currency_code == "CNY":
        request.session['locked_rate'] = "1.0000"
        request.session['locked_at'] = timezone.now().isoformat()
        request.session['locked_currency_code'] = "CNY"
        
        # Give it the standard 24-hour expiry footprint so JavaScript timers don't crash
        current_time_ms = int(time.time() * 1000)
        request.session['rate_expiry_timestamp'] = current_time_ms + (24 * 60 * 60 * 1000)
        request.session.modified = True
        return Decimal("1.0000")

    refresh_needed = False
    locked_rate = request.session.get('locked_rate')
    locked_at = request.session.get('locked_at')
    locked_currency = request.session.get('locked_currency_code')

    if not locked_rate or locked_currency != currency_code:
        refresh_needed = True
    
    if locked_rate and locked_at:
        lock_time = timezone.datetime.fromisoformat(locked_at)
        if timezone.now() > lock_time + timedelta(hours=24):
            refresh_needed = True

    if refresh_needed:
        new_rate = get_current_rate(base_currency_code="CNY", target_currency_code=currency_code)
        request.session['locked_rate'] = str(new_rate)
        request.session['locked_at'] = timezone.now().isoformat()
        request.session['locked_currency_code'] = currency_code
        
        current_time_ms = int(time.time() * 1000)
        request.session['rate_expiry_timestamp'] = current_time_ms + (24 * 60 * 60 * 1000)
        request.session.modified = True
        locked_rate = Decimal(new_rate).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    else:
        locked_rate = Decimal(locked_rate).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

    return locked_rate


def update_shipping_cost(request, cart):
    print("update_shipping_cost triggered")
    if not cart or cart.get_items_count() == 0:
        return "", ""
        
    print("has_physical_items", request.session["has_physical_items"])
    user = request.user if request.user.is_authenticated else None
    shipping_data = request.session.get("shipping_data", {})
    print("shipping_data: ", shipping_data)
    
    physical_cart_items = CartItem.objects.filter(cart=cart, is_active=True, product_variation__product__is_physical=True)
    addresses = Address.objects.filter(profile__user=user) if user else None
    default_address = addresses.filter(is_default=True).first() if user else None
    shipping_html = summary_html = ""

    # Fetch currency format configurations safely
    is_integer, foreign_currency_code = get_currency_format(request)

    # IF SHIPPING COST WAS CALCULATED PREVIOUSLY
    if shipping_data and shipping_data.get("is_calculated"):
        # If cart still has physical items
        if len(physical_cart_items) > 0:
            available_services = ShippingCharge.objects.filter(pk__in=shipping_data['available_services_pks'])
            raw_new_shipping_cost = calculate_shipping_cost(request, physical_cart_items, available_services)
            formatted = intcomma(f"{raw_new_shipping_cost:.2f}")

            foreign_currency_symbol, raw_foreign_amount = calculate_foreign_amount(request, raw_new_shipping_cost)
            try:
                # Strip out any commas if they were pre-applied inside the helper function
                clean_foreign_decimal = Decimal(str(raw_foreign_amount).replace(',', ''))
            except (ValueError, TypeError):
                clean_foreign_decimal = 0.0
            
            if is_integer:
                # JPY/KRW - safely runs formatting logic on actual parsed decimal numbers
                formatted_foreign = intcomma(f"{clean_foreign_decimal:.0f}")
            else:
                # USD/EUR/HKD - standard decimal layout
                formatted_foreign = intcomma(f"{clean_foreign_decimal:.2f}")
            # -----------------------------------------------------------------
            
            # 4-1. Shipping Cost Badges
            shipping_html = f'<strong id="shipping_cost_amount" hx-swap-oob="true" class="font-semibold">CNY ¥ { formatted }</strong>'
            
            # 4-2. Summary-Shipping Row Modification (Swaps target via get_row_oob)
            summary_html = get_row_oob(
                "shipping_cost_row", "Shipping", "運費",
                id_local="summary-shipping",
                id_foreign="shipping_cost_amount_foreign",
                amount=formatted,
                amount_foreign=formatted_foreign,
                symbol=foreign_currency_symbol,
                is_integer = is_integer,
                show=True
            )

            # Save in session safely
            request.session['shipping_data']['shipping_cost'] = str(formatted)
            request.session['shipping_data']['foreign_currency_symbol'] = foreign_currency_symbol
            request.session['shipping_data']['shipping_cost_foreign'] = str(formatted_foreign)
            request.session.modified = True

        # If cart no longer has physical items
        else:
            foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]
            request.session.pop('shipping_data', None)
            request.session.modified = True
            shipping_html = """
                <div id="shipping-section-wrapper" hx-swap-oob="true">
                    <h2 class="text-[1.25rem] mb-5">Shipping｜配送</h2>
                    <div class="alert alert-info shadow-sm mb-4 justify-center">
                        <span>No shipping required for digital products.｜數位產品無需物流。</span>
                    </div>
                </div>
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
                </div>
            """
            summary_html = get_row_oob(
                "shipping_cost_row", "Shipping", "運費",
                id_local="summary-shipping",
                id_foreign="shipping_cost_amount_foreign",
                amount=None,
                amount_foreign=None,
                symbol=foreign_currency_symbol,
                is_integer = is_integer,
                show=False
            )
    
    # IF NO PHYSICAL ITEMS WERE THERE BEFORE
    elif not request.session.get("has_physical_items"):
        if len(physical_cart_items) > 0:
            shipping_section_context = {
                "cart": cart,
                "addresses": addresses,
                "default_address": default_address,
                "global_destinations": DESTINATIONS_GLOBAL,
                "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
                "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
            }
            rendered_form = render_to_string('store/partials/shipping_section.html', shipping_section_context, request=request) 
            shipping_html = f"""
                <div id="shipping-section-wrapper" hx-swap-oob="true">
                    {rendered_form}
                </div>
            """
            foreign_currency_symbol, raw_foreign_amount = calculate_foreign_amount(request, 0)
            summary_html = get_row_oob(
                "shipping_cost_row", "Shipping", "運費",
                id_local="summary-shipping",
                id_foreign="shipping_cost_amount_foreign",
                amount=0,
                amount_foreign=0,
                symbol=foreign_currency_symbol,
                is_integer = is_integer,
                show=True
            )
        else:
            shipping_html = """
                <div id="shipping-section-wrapper" hx-swap-oob="true">
                    <h2 class="text-[1.25rem] mb-5">Shipping｜配送</h2>
                    <div class="alert alert-info shadow-sm mb-4 justify-center">
                        <span>No shipping required for digital products.｜數位產品無需物流。</span>
                    </div>
                </div>
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
                </div>
            """
            summary_html = get_row_oob(
                "shipping_cost_row", "Shipping", "運費",
                id_local="summary-shipping",
                id_foreign="shipping_cost_amount_foreign",
                amount=None,
                amount_foreign=None,
                symbol="",
                is_integer = is_integer,
                show=False,
            )
    # IF PHYSICAL ITEMS WERE THERE BEFORE BUT ONLY NOT CALCULATED YET
    elif request.session.get("has_physical_items"):
        if len(physical_cart_items) > 0:
            if shipping_data:
                return "", ""
            else:
                shipping_section_context = {
                    "cart": cart,
                    "addresses": addresses,
                    "default_address": default_address,
                    "global_destinations": DESTINATIONS_GLOBAL,
                    "greater_china_destinations": DESTINATIONS_GREATER_CHINA,
                    "mainland_china_destinations": DESTINATIONS_MAINLAND_CHINA,
                }
                rendered_form = render_to_string('store/partials/shipping_section.html', shipping_section_context, request=request) 
                shipping_html = f"""
                    <div id="shipping-section-wrapper" hx-swap-oob="true">
                        {rendered_form}
                    </div>
                    <button id="checkout-btn" hx-swap-oob="true" class="flex gap-3 btn btn-block btn-disabled opacity-80 cursor-not-allowed h-auto py-2 min-h-0" disabled>
                        <span>Please calculate shipping first<br>請先計算運費</span>
                        <span><i class="fa-solid fa-arrow-up fa-xl"></i></span>
                    </button>
                """
                foreign_currency_symbol, raw_foreign_amount = calculate_foreign_amount(request, 0)
                summary_html = get_row_oob(
                    "shipping_cost_row", "Shipping", "運費",
                    id_local="summary-shipping",
                    id_foreign="shipping_cost_amount_foreign",
                    amount=0,
                    amount_foreign=0,
                    symbol=foreign_currency_symbol,
                    is_integer = is_integer,
                    show=True
                )
        else:
            shipping_html = """
                <div id="shipping-section-wrapper" hx-swap-oob="true">
                    <h2 class="text-[1.25rem] mb-5">Shipping｜配送</h2>
                    <div class="alert alert-info shadow-sm mb-4 justify-center">
                        <span>No shipping required for digital products.｜數位產品無需物流。</span>
                    </div>
                </div>
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
                </div>
            """
            summary_html = get_row_oob(
                "shipping_cost_row", "Shipping", "運費",
                id_local="summary-shipping",
                id_foreign="shipping_cost_amount_foreign",
                amount=None,
                amount_foreign=None,
                symbol="",
                is_integer = is_integer,
                show=False
            )

    return shipping_html, summary_html


def update_offer(request, cart):
    """
    Safely scales active promo codes during basket mutations.
    💡 FIXED: Removed all redundant offer-error-container tags to perfectly match
    your actual template files and permanently eliminate HTMX target errors.
    """
    offer_data = request.session.get("offer_applied", {})
    code = offer_data.get("offer_code")
    
    is_integer, currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL.get(currency_code, '$')
    rate = Decimal(str(request.session.get('locked_rate', '1.0000')).replace(",", ""))

    # If no coupon code is active, return clean empty strings
    if not code:
        return "", "", None

    perk = None
    user = request.user if request.user.is_authenticated else None

    try:
        user_perk = UserPerk.objects.select_related('perk').get(user=user, unique_code=code) if user else None
        if user_perk:
            perk = user_perk.perk
    except UserPerk.DoesNotExist:
        perk = None

    if not perk:
        perk = Perk.objects.filter(code=code, is_active=True).first()

    # If code has expired or been removed from admin database
    if not perk:
        request.session.pop("offer_applied", None)
        request.session.modified = True
        
        fresh_input_html = render_to_string('store/partials/offer_input.html', {}, request=request)
        fresh_input_wrapper = f'<div id="offer-form-wrapper" hx-swap-oob="true">{fresh_input_html}</div>'
        
        fx_zero = "0" if is_integer else "0.00"
        clear_pricing_oob = f'''
            <span id="summary-discount" hx-swap-oob="true">¥ 0.00</span>
            <span id="discount_amount_foreign" hx-swap-oob="true">{foreign_currency_symbol} ({fx_zero})</span>
        '''
        return clear_pricing_oob + fresh_input_wrapper, fresh_input_wrapper, {"title": "Expired｜已失效", "html": "Sorry, this offer is no longer valid.｜抱歉！此優惠已失效。", "icon": "warning"}
    
    status = PerkEvaluator.get_eligibility_status(request.user, perk)
    formatted_min_spend = intcomma(f"{perk.safe_min_spending:.2f}")
    offer_input_html = None
    update_offer_error_trigger_data = None

    if status == "VALID" and Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", "")) < Decimal(str(perk.safe_min_spending).replace(",", "")):
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Minimum Spend Not Met\n未達最低消費金額", f"Sorry, this offer requires a minimum spending of CNY { formatted_min_spend }.<br>很抱歉，此優惠需消費滿 { formatted_min_spend } 元方可使用。請再多選購一些商品以符合資格。")
    elif status == "OUT_OF_STOCK":
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Limit Reached\n優惠名額已滿", "All available offers have been claimed.")
    elif status == "ALREADY_USED":
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Already Redeemed\n此優惠碼已使用", "This promo code has already been used.")
    elif status == "NO_DOB_DATA":
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Missing birthday information\n缺少您的生日資訊", "We don’t have your birthday data, so this promo cannot be applied.")
    elif status == "FEMALE_ONLY" :
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Ladies only\n女士專屬限定", "This promo code is only available for female members.")
    elif status == "EXPIRED" or status == "THIS_BIRTHDAY_PERK_EXPIRED" or status == "NEW_MEMBER_PERK_EXPIRED":
        offer_input_html, update_offer_error_trigger_data = htmx_invalid_offer_update_response(request, "Offer Expired\n優惠已過期", "Sorry, this offer has expired.")
    
    # Successful Validated Path
    elif status == "VALID":
        discount_type = perk.discount_type
        discount_rate_or_amount = Decimal(str(perk.discount_value).replace(",", ""))
        cart_base_total = Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", ""))
        
        if discount_type == 'percentage':
            discount_amount = cart_base_total * discount_rate_or_amount / Decimal('100')
        elif discount_type == 'fixed_amount':
            discount_amount = min(discount_rate_or_amount, cart_base_total)
        else:
            discount_amount = Decimal('0.00')

        fx_offer = quantize_amount(discount_amount * rate, currency_code)

        request.session["offer_applied"] = {
            "offer_code": code,
            "discount_amount": intcomma(f"{discount_amount:.2f}"),
            "discount_amount_foreign": format_fx_value(fx_offer, currency_code),
        }
        request.session.modified = True

        context = {
            'active_code': code, 
            'perk_code': perk.code, 
            'discount': intcomma(f"{discount_amount:.2f}"),
            'offer_applied_foreign': format_fx_value(fx_offer, currency_code),
            'foreign_currency_symbol': foreign_currency_symbol,
            'is_integer': is_integer,
            'is_oob': True
        }
        
        offer_oob_html = render_to_string('store/partials/offer_active.html', context, request=request)
        pricing_oob = f'''
            <span id="summary-discount" hx-swap-oob="true">¥ ({intcomma(f"{discount_amount:.2f}")})</span>
            <span id="discount_amount_foreign" hx-swap-oob="true">{foreign_currency_symbol} ({format_fx_value(fx_offer, currency_code)})</span>
        '''
        
        # 💡 Return exactly three items cleanly
        return offer_oob_html + pricing_oob, "", None
        
    # Invalid / Ineligible Track
    if offer_input_html is not None and update_offer_error_trigger_data is not None:
        updated_offer_input_oob = f'<div id="offer-form-wrapper" hx-swap-oob="true">{offer_input_html}</div>'
        
        fx_offer_zero = "0" if is_integer else "0.00"
        pricing_resets_oob = f'''
            <span id="summary-discount" hx-swap-oob="true">¥ (0.00)</span>
            <span id="discount_amount_foreign" hx-swap-oob="true">{ foreign_currency_symbol } ({fx_offer_zero})</span>
        '''

        request.session.pop("offer_applied", None)
        request.session.modified = True
        return pricing_resets_oob, updated_offer_input_oob, update_offer_error_trigger_data

    else:
        return "", "", None


def update_costs_oobs(request, cart, is_integer, foreign_currency_code, foreign_currency_symbol, locked_rate):
    """
    Unified Shared Cost Calculation Matrix.
    Enforces a strict Ledger-First execution order while filtering out empty 
    string elements to completely prevent id="undefined" console errors.
    """
    oob_updates = []
    triggers = {}

    # 1. Run dynamic background calculations silently inside session states
    shipping_html, summary_html = update_shipping_cost(request, cart)

    offer_oob_html, updated_offer_input_oob, update_offer_error_trigger_data = update_offer(request, cart)
    
    # Securely append non-empty string payloads to your OOB updates list
    if offer_oob_html and str(offer_oob_html).strip(): 
        oob_updates.append(offer_oob_html)
    if updated_offer_input_oob and str(updated_offer_input_oob).strip(): 
        oob_updates.append(updated_offer_input_oob)
        
    if update_offer_error_trigger_data is not None:
        triggers["errorMssg"] = update_offer_error_trigger_data 

    # Execute Voucher Applied Deductions
    updated_voucher_oob_string = update_applied_voucher(request, cart)
    if updated_voucher_oob_string and str(updated_voucher_oob_string).strip(): 
        oob_updates.append(updated_voucher_oob_string)

    # =============================================================
    # 🔒 2. RUN THE MASTER LEDGER CORE ANCHOR
    # =============================================================
    _, fmt_cny_payable, fmt_fx_payable = update_total_payable(request, cart)

    # 3. Extract freshly updated, balanced data metrics out of session safety logs
    def get_session_fx(key, nested_key):
        return request.session.get(key, {}).get(nested_key, "0")
    
    cny_shipping_str = get_session_fx("shipping_data", "shipping_cost")
    cny_offer_str = get_session_fx("offer_applied", "discount_amount")
    cny_voucher_applied_str = get_session_fx("applied_voucher", "applied_voucher_amount")

    fx_shipping_str = get_session_fx("shipping_data", "shipping_cost_foreign")
    fx_offer_str = get_session_fx("offer_applied", "discount_amount_foreign")
    fx_voucher_applied_str = get_session_fx("applied_voucher", "applied_voucher_amount_foreign")

    def clean_model_fx(val_str):
        return Decimal(str(val_str).replace(",", ""))

    # Pull component metrics straight from model tracking rows
    cny_physical = cart.get_physical_products_subtotal()
    cny_electronic = cart.get_e_products_subtotal()
    cny_voucher_p = cart.get_voucher_products_subtotal()

    fx_physical_str = get_session_fx("shipping_data", "physical_products_total_foreign")
    fx_electronic_str = format_fx_value(clean_model_fx(cart.get_e_products_subtotal_foreign(foreign_currency_code, locked_rate)), foreign_currency_code)
    fx_voucher_p_str = format_fx_value(clean_model_fx(cart.get_voucher_products_subtotal_foreign(foreign_currency_code, locked_rate)), foreign_currency_code)

    # Header calculations summary row
    updated_header_summary = update_header_cart_summary(cart)
    if updated_header_summary and str(updated_header_summary).strip():
        oob_updates.append(updated_header_summary)

    # Costs layout items formatting via pure Python conditional expressions
    cny_discount_val = clean_decimal(cny_offer_str)
    fx_discount_val = clean_decimal(fx_offer_str)
    cny_voucher_applied_val = clean_decimal(cny_voucher_applied_str)
    fx_voucher_applied_val = clean_decimal(fx_voucher_applied_str)

    cny_discount_display = f"{intcomma(f'{cny_discount_val:.2f}')}" if cny_discount_val > 0 else "0.00"
    fx_discount_display = f"{fx_offer_str}" if fx_discount_val > 0 else f"0{'' if is_integer else '.00'}"
    cny_voucher_display = f"{intcomma(f'{cny_voucher_applied_val:.2f}')}" if cny_voucher_applied_val > 0 else "0.00"
    fx_voucher_display = f"{fx_voucher_applied_str}" if fx_voucher_applied_val > 0 else f"0{'' if is_integer else '.00'}"

    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    has_physical_items = cart_items.filter(product_variation__product__is_physical=True).exists()
    has_e_items = cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
    has_cash_voucher_items = cart_items.filter(product_variation__product__is_voucher=True).exists()

    summary_context = {
        "has_physical_items": has_physical_items,
        "has_e_items": has_e_items,
        "has_cash_voucher_items": has_cash_voucher_items,

        "foreign_currency_symbol": foreign_currency_symbol,
        "physical_products_total": cny_physical,
        "physical_products_total_foreign": fx_physical_str,
        "shipping_cost": cny_shipping_str,
        "shipping_cost_foreign": fx_shipping_str,
        "e_products_total": cny_electronic,
        "e_products_total_foreign": fx_electronic_str,
        "offer_applied": cny_discount_display,
        "offer_applied_foreign": fx_discount_display,
        "voucher_applied": cny_voucher_display,
        "voucher_applied_foreign": fx_voucher_display,
        "voucher_products_total": cny_voucher_p,
        "voucher_products_total_foreign": fx_voucher_p_str,
        "total_payable": fmt_cny_payable,
        "total_payable_foreign": fmt_fx_payable,
        "is_oob": True,
    }
    summary_cart_total_html = render_to_string("store/partials/cart_summary.html", summary_context, request)
    summary_cart_wrapper_html = f"""
        <table>
            <tbody id="cart_summary_section"
                hx-get="/carts/update_exchange_rate_api/"
                hx-trigger="refresh_forex from:body"
                hx-swap-oob="true"
                hx-swap="none"
            >
                {summary_cart_total_html}
            </tbody>
        </table>
    """
    oob_updates.append(summary_cart_wrapper_html)

    if shipping_html:
        styled_shipping_oob = shipping_html.replace(
            'id="shipping-cost-display"', 
            'id="shipping-cost-display" hx-swap-oob="true"'
        )
        oob_updates.append(styled_shipping_oob)
    
    return oob_updates, triggers


def update_header_cart_list(request, updated_cart_items):
    context = {
        "current_cart_items": updated_cart_items
    }
    return render_to_string('store/partials/header_cart_list.html', context, request=request)


def update_cart_totals(request, updated_cart_items, cart):
    """
    Surgically pushes category subtotal fragments to the client.
    Reads directly from your locked component entries to enforce absolute balance.
    """
    if not cart or cart.get_items_count() == 0:
        return ""
        
    is_integer, currency_code = get_currency_format(request)
    symbol = CURRENCY_SYMBOL.get(currency_code, '$')
    rate = Decimal(str(request.session.get('locked_rate', '1.0000')).replace(",", ""))

    has_physical_items = updated_cart_items.filter(product_variation__product__is_physical=True).exists()
    has_e_items = updated_cart_items.filter(product_variation__product__is_physical=False, product_variation__product__is_voucher=False).exists()
    has_cash_voucher_items = updated_cart_items.filter(product_variation__product__is_voucher=True).exists()

    cny_physical = Decimal(str(cart.get_physical_products_subtotal() or 0).replace(",", ""))
    cny_electronic = Decimal(str(cart.get_e_products_subtotal() or 0).replace(",", ""))
    cny_voucher_p = Decimal(str(cart.get_voucher_products_subtotal() or 0).replace(",", ""))
    
    # Force a master ledger calculation pass to align session indicators first
    _, _, _ = update_total_payable(request, cart)

    # Pull the frozen component parameters straight out of session safety logs
    def get_clean_fx(key, nested_key):
        val = request.session.get(key, {}).get(nested_key, "0")
        return Decimal(str(val).replace(",", ""))

    fx_physical = get_clean_fx("shipping_data", "physical_products_total_foreign")
    fx_electronic = quantize_amount(cny_electronic * rate, currency_code)
    fx_voucher_p = quantize_amount(cny_voucher_p * rate, currency_code)

    cart_totals_html = []
    cart_totals_html.append(get_row_oob("physical_items_row", "Physical Products", "實物商品小計", "physical_products_total", "physical_products_total_foreign", intcomma(f"{cny_physical:.2f}"), format_fx_value(fx_physical, currency_code), symbol, is_integer))
    cart_totals_html.append(get_row_oob("e_items_row", "eProducts", "電子商品小計", "e_products_total", "e_products_total_foreign", intcomma(f"{cny_electronic:.2f}"), format_fx_value(fx_electronic, currency_code), symbol, is_integer))
    cart_totals_html.append(get_row_oob("voucher_items_row", "Voucher Purchase", "禮品券購買金額", "voucher_purchase_total", "voucher_purchase_total_foreign", intcomma(f"{cny_voucher_p:.2f}"), format_fx_value(fx_voucher_p, currency_code), symbol, is_integer))
    return "".join(filter(None, cart_totals_html))


def get_cart_totals(request, cart):
    is_integer, foreign_currency_code = get_currency_format(request)
    foreign_currency_symbol = CURRENCY_SYMBOL[foreign_currency_code]
    locked_rate = get_or_lock_checkout_rate(request, foreign_currency_code)
    
    cart_grand_total = cart.get_cart_total()
    cart_total_foreign = cart.get_cart_total_foreign(foreign_currency_code, locked_rate)

    physical_products_total = cart.get_physical_products_subtotal()
    physical_products_total_foreign = cart.get_physical_products_subtotal_foreign(foreign_currency_code, locked_rate)

    e_products_total = cart.get_e_products_subtotal()
    e_products_total_foreign = cart.get_e_products_subtotal_foreign(foreign_currency_code, locked_rate)

    voucher_products_total = cart.get_voucher_products_subtotal()
    voucher_products_total_foreign = cart.get_voucher_products_subtotal_foreign(foreign_currency_code, locked_rate)

    cart_items_quantity = cart.get_items_count()
    print("get_cart_totals - cart_items_quantity: ",  cart.get_items_count())
    return cart_grand_total, cart_total_foreign, physical_products_total, physical_products_total_foreign, \
        e_products_total, e_products_total_foreign, voucher_products_total, voucher_products_total_foreign, \
        foreign_currency_symbol, cart_items_quantity


def validate_email_mx_domain(email_string):
    """
    Verifies that the target email's domain actually has active 
    routing records to catch dead domains or typos before payment processes.
    """
    if not email_string or "@" not in email_string:
        return
        
    try:
        # Extract the domain string parameter cleanly
        _, domain = email_string.split('@', 1)
        domain = domain.strip()
        
        # Perform a fast native low-level DNS lookup check for the domain's server records
        # This will fail quickly if the domain is completely fictional (e.g., "gamil.con")
        socket.gethostbyname(domain)
        
    except (socket.gaierror, ValueError):
        # Raise an explicit validation error caught cleanly by your Django form loop layout
        raise ValidationError(
            "The email domain appears to be invalid or unavailable. Please check your spelling. ｜ 電子郵件網域無效，請檢查拼字。"
        )


# def checkout_apply_voucher(request, user_input): # save for later use
#     try:
#         with transaction.atomic():
#             # 1. Lock the user's voucher row so no other tab can read the balance yet
#             vouchers = (
#                 CustomerVoucher.objects
#                 .filter(owner=request.user, is_used=False, balance__gt=0)
#                 .select_for_update()
#                 .order_by('created_date')
#             )
#             remaining_to_deduct = user_input

#             for voucher in vouchers:
#                 if remaining_to_deduct <= 0:
#                     break

#                 # Determine how much to take from THIS specific voucher
#                 deduction = min(voucher.balance, remaining_to_deduct)

#                 # Update voucher balance
#                 voucher.balance = F('balance') - deduction
#                 voucher.save()

#                 # Refresh to check if it's now empty
#                 voucher.refresh_from_db()
#                 if voucher.balance <= 0:
#                     voucher.is_used = True
#                     voucher.used_date = timezone.now()
#                     voucher.save()

#                 remaining_to_deduct -= deduction

#             # Final safety check
#             if remaining_to_deduct > 0:
#                 # This should technically not happen due to initial total_avilable check
#                 raise ValueError("Balance mismatch during processing.")
#     except Exception as e:
#         return htmx_invalid_offer_response(request, "Input Error\輸入錯誤", f"An error occurred while applying your balance.<br>禮品券適用過程中有錯誤。")





