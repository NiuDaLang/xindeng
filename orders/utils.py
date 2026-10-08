# orders/utils.py
from django.core.cache import cache
from accounts.data import DEFAULT_EXCHANGE_RATE_VS_CNY, INTERNAL_CURRENCY_ADJUSTMENT, CURRENCY_SYMBOL, INTEGER_CURRENCIES
from decimal import Decimal, ROUND_HALF_UP
from .models import Order, OrderProduct
from carts.models import ProformaInvoice
import io
import os
import logging
from django.conf import settings
from accounts.models import Perk, UserPerk
from accounts.evaluators import PerkEvaluator
from django.utils import timezone, formats
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import intcomma
from accounts.models import CustomerVoucher
from django.db.models import F

# reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, PageBreak, KeepTogether
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from core.pdf_utils import (
    ensure_fonts_registered,
    wrap_font, 
    safe_paragraph,
    safe_image,
    safe_decimal,
    format_currency,
    escape_for_pdf
)

# paypal
from paypalserversdk.models.item import Item
from paypalserversdk.models.money import Money

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

logger = logging.getLogger(__name__)


def get_current_rate(base_currency_code="CNY", target_currency_code="HKD"):
    """
    Retrieves the rate from Redis cache.
    If cache is empty or the target currency is missing from the snapshot,
    falls back to DEFAULT_EXCHANGE_RATE_VS_CNY.

    Always returns a positive float. Never returns None.
    """
    all_rates = cache.get('exchange_rates') or {}

    try:
        # CNY has no self-pair; the rate against the USD base is stored
        # under "CNH" (offshore yuan). Fall back to that when CNY is missing.
        base_key = base_currency_code if all_rates.get(base_currency_code) is not None else "CNH"
        usd_base_currency = all_rates.get(base_key)
        usd_target_currency = all_rates.get(target_currency_code)

        if usd_base_currency is not None and usd_target_currency is not None:
            raw = (usd_target_currency / usd_base_currency) * INTERNAL_CURRENCY_ADJUSTMENT
            quantized = Decimal(str(raw).replace(",", "")).quantize(
                Decimal('0.0001'), rounding=ROUND_HALF_UP
            )
            return float(quantized)

        logger.warning(
            "get_current_rate: cache miss for %s->%s; using static fallback",
            base_currency_code, target_currency_code,
        )
    except (KeyError, TypeError, ValueError, ZeroDivisionError, InvalidOperation) as exc:
        logger.warning(
            "get_current_rate: cache read failed for %s->%s (%s); using static fallback",
            base_currency_code, target_currency_code, exc,
        )

    # Static fallback path — reached on cache miss, or on any of the above errors.
    fallback_rate = DEFAULT_EXCHANGE_RATE_VS_CNY.get(target_currency_code)
    if fallback_rate is None:
        logger.error(
            "get_current_rate: no fallback rate for %s; returning 1.0",
            target_currency_code,
        )
        return 1.0

    fallback_rate = (
        Decimal(str(fallback_rate).replace(",", ""))
        * Decimal(str(INTERNAL_CURRENCY_ADJUSTMENT))
    ).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    return float(fallback_rate)


def get_pdf_styles():
    styles = getSampleStyleSheet()

    # Register all fonts (idempotent — safe to call on every request).
    ensure_fonts_registered()

    styles.add(ParagraphStyle(
        name='ShopName', fontName='NotoSansTC-Bold', fontSize=16, leading=24
    ))
    styles.add(ParagraphStyle(
        name='OrderTitle',
        fontName='NotoSansTC-Bold', fontSize=22, leading=26,
        spaceAfter=0, spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name='Barcode',
        fontName='Barcode128', fontSize=32, leading=32,
        spaceAfter=0, spaceBefore=0,
    ))
    styles.add(ParagraphStyle(
        name='Greeting',
        fontName='NotoSansTC-Bold', fontSize=13, leading=18, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='BodyTextCustom',
        fontName='NotoSansTC-Regular', fontSize=10, leading=15, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='BodyTextCustomBold',
        fontName='NotoSansTC-Bold',
        fontSize=10, leading=15, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name='ProductDescription',
        fontName='NotoSansTC-Regular', fontSize=10, leading=15, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name='LabelXS',
        fontName='NotoSansTC-Regular', fontSize=8,
        textColor=colors.HexColor('#666666'), spaceAfter=1.0,
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle',
        fontName='NotoSansTC-Bold', fontSize=12, spaceBefore=20, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='FooterBold',
        fontName='NotoSansTC-Bold', fontSize=10, spaceBefore=18, spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name='SanskritTitle', fontName='SanskritFont', fontSize=16, leading=24
    ))
    styles.add(ParagraphStyle(name='AlignLeft', alignment=TA_LEFT))
    styles.add(ParagraphStyle(
        name='AlignCenter', fontName='NotoSansTC-Regular', alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(name='AlignRight', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='AlignJustify', alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontName='NotoSansTC-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#686461'),
        spaceBefore=10,
        spaceAfter=6,
        alignment=TA_LEFT,
    ))

    return styles


def get_header_element(styles):
    shop_name_html = (
        wrap_font("Hṛdayadīpa (हृदयदीप)", "SanskritFont", 15)
        + "｜心燈"
    )
    mixed_style = ParagraphStyle(
        "MixedStyle",
        fontName="NotoSansTC-Bold",
        fontSize=16,
        leading=20,
    )
    return Paragraph(shop_name_html, mixed_style)


def generate_order_confirmation_pdf(order_id):
    # Data Retrieval
    order = Order.objects.get(order_number=order_id)
    order_products = OrderProduct.objects.filter(order=order)
    payment = order.payment
    user = order.user if order.user else None
    proforma_invoice = ProformaInvoice.objects.get(proforma_order_number=order_id)
    # Safely extract your local currency code assignment
    currency_code = getattr(order, 'currency_code', 'CNY') or 'CNY'
    currency_code = currency_code.upper().strip()
    is_integer = currency_code in INTEGER_CURRENCIES
    is_bank_transfer = (proforma_invoice.payment_method == "BANK_TRANSFER")

    buffer = io.BytesIO()
    styles = get_pdf_styles()

    # set up document
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        title=f"Order Confirmation｜訂單確認 - {order.order_number}",
        topMargin=10*mm, bottomMargin=10*mm,
        leftMargin=15*mm, rightMargin=15*mm,
    )
    elements = []

    # (a) Top Line (Logo + Shop Name)
    logo_path = os.path.join(str(settings.BASE_DIR), 'static', 'images', 'logos', 'logo_square.png')
    logo_flowable = safe_image(logo_path, 15*mm, 15*mm)
    logo = logo_flowable if logo_flowable else Paragraph("[Logo]", styles['BodyTextCustom'])    

    shop_paragraph = get_header_element(styles) # Hṛdayadīpa (हृदयदीप)｜心燈

    header_table = Table([[logo, shop_paragraph]], colWidths=[15*mm, 130*mm])
    header_table.hAlign = 'LEFT'
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,0), 0),
    ]))

    # (b) Order Confirmation Title + Barcode
    title_data = [[
        Paragraph(
            "Order Hold Confirmation｜訂單保留確認"
            if is_bank_transfer
            else "Order Confirmation｜訂單確認",
            styles['OrderTitle'],
        ),
        Paragraph(order.order_number, styles['Barcode']),
    ]]

    title_table = Table(title_data, colWidths=[120*mm, 40*mm])
    title_table.hAlign = 'LEFT'
    title_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,0), 0),
        ('BOTTOMPADDING', (1, 0), (1, 0), 10), # Nudge the barcode cell specifically
    ]))

    # (c) Greeting & Paragraphs
    username = user.username if user else "Guest｜訪客"

    if is_bank_transfer:
        p1 = (
            "Thank you for your order. Your item(s) have been reserved for 72 hours.<br/>"
            "感謝您的訂購！您的商品庫存已為您保留 72 小時。"
        )
        p2 = (
            "Please complete your bank transfer within this 72-hour window. "
            "Once payment is verified, we will notify you when your physical "
            "product(s) parcel is dispatched. Please note: if payment is not "
            "received by the end of this period, the order will be treated as "
            "cancelled and we cannot guarantee stock retention.<br/>"
            "請在 72 小時內完成銀行轉帳。經確認付款後，我們將在您的實體產品包裹"
            "發出時通知您。請注意：若逾期未收到款項，本訂單將視為取消，"
            "我們亦無法保證為您保留商品庫存，敬請留意。"
        )
        p3 = (
            "Any e-product(s) in this order will be delivered after payment "
            "clearance: (a) instant digital items — a time-limited secure download "
            "link will be emailed to you; (b) made-to-order digital items — the "
            "artisan will begin production after payment and will be in touch to "
            "confirm delivery; (c) e-vouchers — if you purchased for yourself, the "
            "credit is added instantly to your member wallet on payment. If you "
            "gifted it to someone else, an email invitation to claim will be sent "
            "to the recipient; they can claim it by logging in (or registering "
            "first) and requesting their redemption PIN, at which point the credit "
            "is added to their wallet.<br/>"
            "本訂單中的電子產品將於確認付款後交付：(a) 隨選即發之數位商品——"
            "我們將以電子郵件寄送具時效性的安全下載連結；(b) 接單訂製之數位商品——"
            "匠人將於確認付款後開始製作，並與您聯繫確認交付時程；"
            "(c) 電子禮品券——若為自用，購物金將於付款後即時存入您的會員錢包。"
            "若為餽贈，我們將以電子郵件向收件人發送領取邀請；收件人可透過登入"
            "（或先註冊會員）申請領取驗證碼，經核銷後購物金即存入其會員錢包。"
        )
    else:
        p1 = f"Thank you for shopping with us!<br/>感謝您在本店購物！"
        p2 = "We will notify you when your physical product(s) parcel is dispatched.<br/>我們會在您的實體產品包裹發出時通知您。"
        p3 = "Your e-product(s), if any, will be sent via another email.<br/>如果您有購買電子產品，我們將透過另一封電子郵件發送給您。"

    # (d) Order Details Section
    # *** Name ***
    if user:
        name_data = [[
            [
                Paragraph("First Name｜名", styles['LabelXS']),
                safe_paragraph(user.first_name, styles['BodyTextCustomBold']),
            ],
            [
                Paragraph("Last Name｜姓", styles['LabelXS']),
                safe_paragraph(user.last_name, styles['BodyTextCustomBold']),
            ],
            [
                Paragraph("Username｜用戶名", styles['LabelXS']),
                safe_paragraph(username, styles['BodyTextCustomBold']),
            ],
        ]]
        name_table = Table(name_data, colWidths=[58*mm, 58*mm, 58*mm])
    else:
        name_data = [[
            Paragraph("Guest User｜訪客用戶", styles["BodyTextCustom"]),
            "", "",
        ]]
        name_table = Table(name_data, colWidths=[174*mm])

    name_table.hAlign = "LEFT"

    # *** contact ***
    contact_data = [[
        [
            Paragraph("Email｜電郵", styles['LabelXS']),
            safe_paragraph(order.email, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Phone｜電話", styles['LabelXS']),
            safe_paragraph(
                f"{(order.recipient_mobile_area or '')} {(order.recipient_mobile_number or '')}".strip(),
                styles['BodyTextCustomBold'],
            ),
        ],
    ]]
    contact_table = Table(contact_data, colWidths=[87*mm, 87*mm])
    contact_table.hAlign = "LEFT"

    # *** payment line_1 ***
    payment_method_display = (
        order.payment.payment_method if order.payment else "Bank Transfer｜銀行轉帳"
    )
    payment_id_display = (
        order.payment.payment_id if order.payment else "Pending Manual Hold｜待核對"
    )
    payment_1_data = [[
        [
            Paragraph("Payment Method｜支付方式", styles['LabelXS']),
            safe_paragraph(payment_method_display, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Transaction ID｜交易ID", styles['LabelXS']),
            safe_paragraph(payment_id_display, styles['BodyTextCustomBold']),
        ],
    ]]
    payment_1_table = Table(payment_1_data, colWidths=[87*mm, 87*mm])
    payment_1_table.hAlign = "LEFT"

    # *** payment line_2 ***
    # Payment amount is always the order's foreign-currency total.
    # total_due_foreign is the amount the buyer paid (PayPal) or must
    # wire (bank transfer) in their chosen currency. total_due is the
    # CNY base and would mislabel the amount when currency_code != CNY.
    payment_amount_decimal = safe_decimal(order.total_due_foreign)

    if payment_amount_decimal == Decimal("0") and currency_code != "CNY":
        logger.warning(
            "generate_order_confirmation_pdf: order %s has no total_due_foreign "
            "for currency %s; displaying a placeholder.",
            order.order_number, currency_code,
        )
        payment_amount_display = "—"
    else:
        currency_symbol = CURRENCY_SYMBOL.get(currency_code, "")
        payment_amount_display = format_currency(
            payment_amount_decimal, currency_symbol, is_integer=is_integer,
        )

    payment_2_data = [[
        [
            Paragraph("Payment Currency｜付款貨幣", styles['LabelXS']),
            safe_paragraph(currency_code, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Payment Amount｜支付金額", styles['LabelXS']),
            safe_paragraph(
                payment_amount_display,
                styles['BodyTextCustomBold'],
                apply_fallback=False,
            ),
        ],
    ]]
    payment_2_table = Table(payment_2_data, colWidths=[87*mm, 87*mm])
    payment_2_table.hAlign = "LEFT"

    # *** shipping info_1 ***
    phone_combined = (
        f"{(order.recipient_mobile_area or '')} {(order.recipient_mobile_number or '')}".strip()
    )
    shipping_1_data = [[
        [
            Paragraph("Recipient Last Name｜收件人 姓", styles['LabelXS']),
            safe_paragraph(order.recipient_first_name, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Recipient First Name｜收件人 名", styles['LabelXS']),
            safe_paragraph(order.recipient_last_name, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Recipient Phone｜收件人電話", styles['LabelXS']),
            safe_paragraph(phone_combined, styles['BodyTextCustomBold']),
        ],
    ]]
    shipping_1_table = Table(shipping_1_data, colWidths=[58*mm, 58*mm, 58*mm])
    shipping_1_table.hAlign = "LEFT"
    
    # *** shipping info_2 ***
    street_address_data = (
        f"{order.address_line_1}, {order.address_line_2}"
        if order.address_line_2
        else (order.address_line_1 or "")
    )
    shipping_2_data = [[
        [
            Paragraph("Street Address｜街道地址", styles['LabelXS']),
            safe_paragraph(street_address_data, styles['BodyTextCustomBold']),
        ],
    ]]
    shipping_2_table = Table(shipping_2_data, colWidths=[174*mm])
    shipping_2_table.hAlign = "LEFT"

    # *** shipping info_3 ***
    shipping_3_data = [[
        [
            Paragraph("City｜城市", styles['LabelXS']),
            safe_paragraph(order.city, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("State/Province｜州/省/縣", styles['LabelXS']),
            safe_paragraph(order.state_province_region, styles['BodyTextCustomBold']),
        ],
    ]]
    shipping_3_table = Table(shipping_3_data, colWidths=[87*mm, 87*mm])
    shipping_3_table.hAlign = "LEFT"

    # *** shipping info_4 ***
    raw_country = order.get_country_display() if hasattr(order, 'get_country_display') else ""
    name_part = raw_country[:-2].strip() if raw_country and " " in raw_country else raw_country

    shipping_4_data = [[
        [
            Paragraph("Country / Region｜國家/地區", styles['LabelXS']),
            safe_paragraph(name_part, styles['BodyTextCustomBold']),
        ],
        [
            Paragraph("Post Code｜郵編", styles['LabelXS']),
            safe_paragraph(order.postal_code, styles['BodyTextCustomBold']),
        ],
    ]]
    shipping_4_table = Table(shipping_4_data, colWidths=[87*mm, 87*mm])
    shipping_4_table.hAlign = "LEFT"

    # *** shipping info_5 ***
    shipping_5_data = [[
        [
            Paragraph("Delivery Note｜配送備注", styles['LabelXS']),
            safe_paragraph(order.delivery_note, styles['BodyTextCustomBold']),
        ],
    ]]
    shipping_5_table = Table(shipping_5_data, colWidths=[174*mm])
    shipping_5_table.hAlign = "LEFT"

    # *** shipping info_6 ***
    send_invoice = (
        "Yes, include invoice with delivery.｜是，將帳單一起配送。"
        if order.do_not_send_invoice == False
        else "No, do NOT include invoice with delivery.｜不，不要將帳單一起配送。"
    )
    shipping_6_data = [[
        [
            Paragraph("Include invoice?｜附上帳單?", styles['LabelXS']),
            safe_paragraph(send_invoice, styles['BodyTextCustomBold'], apply_fallback=False),
        ],
    ]]
    shipping_6_table = Table(shipping_6_data, colWidths=[174*mm])
    shipping_6_table.hAlign = "LEFT"

    shipping_manifest_elements = [shipping_1_table, shipping_2_table, shipping_3_table, 
                                  shipping_4_table, shipping_5_table, shipping_6_table]

    # details tables style formatting
    detail_tables = [name_table, contact_table, payment_1_table, payment_2_table]
   
    for table in detail_tables:
        table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

    # (e) Product List Container (#e8e7e7 background)
    product_data = [["", "Product｜商品", "", "Price｜價格", "Qty｜數量", "Sub-Total｜小計"]]

    for idx, item in enumerate(order_products, start=1):
        # Image — guard with safe_image() which handles robust_exists and
        # catches Image() construction errors.
        img_path = None
        if item.product_variation and item.product_variation.images:
            try:
                img_path = item.product_variation.images.path
            except (ValueError, NotImplementedError):
                img_path = None
        p_img = safe_image(img_path, width=15*mm, height=12*mm) or ""

        # Product name — safe_paragraph escapes user-supplied content.
        product_name_flowable = safe_paragraph(
            str(item.product_variation) if item.product_variation else "—",
            styles['ProductDescription'],
        )

        product_data.append([
            idx,
            p_img,
            product_name_flowable,
            f"CNY ¥ {safe_decimal(item.product_price):,.2f}",
            safe_paragraph(str(item.quantity), styles["AlignCenter"], apply_fallback=False),
            f"CNY ¥ {safe_decimal(item.get_subtotal()):,.2f}",
        ])

    p_table = Table(product_data, colWidths=[8*mm, 20*mm, 60*mm, 32*mm, 22*mm, 32*mm])
    p_table.hAlign = "LEFT"
    p_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#e8e7e7")),
        ("FONTNAME", (0,0), (-1,0), "NotoSansTC-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "NotoSansTC-Regular"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("LINEBELOW", (0,0), (-1,0), 1, colors.HexColor("#686461")),
        ("LINEBELOW", (0,1), (-1,-2), 0.5, colors.grey),
        ("LINEBELOW", (0,-1), (-1,-1), 1, colors.grey),
        ("ALIGN", (3,0), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (0, -1), 10),
        ('RIGHTPADDING', (-1, 0), (-1, -1), 10),
        ("SPAN", (1,0), (2,0))
    ]))

    # =============================================================
    # 📉 (f) PRICE SUMMARY SECTION (BACKWARD-BALANCED PDF LEDGER)
    # =============================================================
    # Extract baseline numbers as raw, clean numeric Decimal structures
    cny_prod = safe_decimal(order.product_total)
    cny_ship = safe_decimal(order.shipping_cost)
    cny_disc = safe_decimal(order.discount)
    cny_tax  = safe_decimal(order.tax)
    cny_vouch = safe_decimal(order.voucher_applied)
    cny_due  = safe_decimal(order.total_due)    

    if currency_code != "CNY":
        fx_currency = currency_code
        fx_symbol = CURRENCY_SYMBOL.get(fx_currency, "")

        fx_ship = safe_decimal(order.shipping_cost_foreign)
        fx_disc = safe_decimal(order.discount_foreign)
        fx_tax  = safe_decimal(order.tax_foreign)
        fx_vouch = safe_decimal(order.voucher_applied_foreign)
        fx_due  = safe_decimal(order.total_due_foreign)

        # Backwards-derive the subtotal from the total and its components,
        # since the DB doesn't store the FX subtotal directly.
        fx_subtotal = fx_due + fx_disc + fx_vouch - fx_tax - fx_ship

        summary_data = [
            ["", "CNY", f"{fx_currency}"],
            [
                "Products｜商品小計",
                format_currency(cny_prod, "¥"),
                format_currency(fx_subtotal, fx_symbol, is_integer=is_integer),
            ],
            [
                "Shipping｜運費費率",
                format_currency(cny_ship, "¥"),
                format_currency(fx_ship, fx_symbol, is_integer=is_integer),
            ],
        ]

        # Negated values: the "Less" convention uses format_currency's
        # negative-parenthesis branch, so both columns read identically.
        if cny_disc > 0:
            summary_data.append([
                "Discount (Less)｜優惠折抵 (扣減)",
                format_currency(-cny_disc, "¥"),
                format_currency(-fx_disc, fx_symbol, is_integer=is_integer),
            ])
        if cny_tax > 0:
            summary_data.append([
                "Tax & Duty｜代繳稅金",
                format_currency(cny_tax, "¥"),
                format_currency(fx_tax, fx_symbol, is_integer=is_integer),
            ])
        if cny_vouch > 0:
            summary_data.append([
                "Voucher (Less)｜禮品卡折抵 (扣減)",
                format_currency(-cny_vouch, "¥"),
                format_currency(-fx_vouch, fx_symbol, is_integer=is_integer),
            ])

        summary_data.append([
            "Total Received｜總計應收",
            format_currency(cny_due, "¥"),
            format_currency(fx_due, fx_symbol, is_integer=is_integer),
        ])
        s_table = Table(summary_data, colWidths=[70*mm, 52*mm, 52*mm])

    else:
        # Base-currency-only checkout; no FX column at all.
        summary_data = [
            ["", "CNY"],
            ["Products｜商品小計", format_currency(cny_prod, "¥")],
            ["Shipping｜運費費率", format_currency(cny_ship, "¥")],
        ]
        if cny_disc > 0:
            summary_data.append([
                "Discount (Less)｜優惠折抵 (扣減)",
                format_currency(-cny_disc, "¥"),
            ])
        if cny_tax > 0:
            summary_data.append([
                "Tax & Duty｜代繳稅金",
                format_currency(cny_tax, "¥"),
            ])
        if cny_vouch > 0:
            summary_data.append([
                "Voucher (Less)｜禮品卡折抵 (扣減)",
                format_currency(-cny_vouch, "¥"),
            ])

        summary_data.append([
            "Total Received｜總計應收",
            format_currency(cny_due, "¥"),
        ])
        s_table = Table(summary_data, colWidths=[100*mm, 74*mm])

    # Apply global summary layout aesthetics
    s_table.hAlign = 'LEFT'
    s_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'NotoSansTC-Regular'),
        ('FONTNAME', (0,-1), (-1,-1), 'NotoSansTC-Bold'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.lightgrey),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor("#686461")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    # 🌟 NEW INJECTED SUBSECTION: OFFLINE REMITTANCE & MOBILE QR CODES (CONDITIONAL)
    offline_payment_table = None
    if is_bank_transfer:
        # ── Pick the account block matching this order's currency ──
        account = settings.XINDENG_BANK_ACCOUNTS.get(currency_code)
        if account is None:
            # Should be unreachable: the checkout flow only offers bank
            # transfer when currency_code is HKD or CNY. If we hit this,
            # something bypassed that gate. Log it and render a support
            # notice instead of a wrong account.
            logger.error(
                "generate_order_confirmation_pdf: bank-transfer order %s "
                "has unsupported currency %s; no bank account configured",
                order.order_number, currency_code,
            )
            unavailable_html = (
                "Bank remittance details for this currency are not currently "
                "available online. Please contact our support team to complete "
                "your payment.<br/>"
                "此貨幣的銀行匯款資訊暫未能於線上顯示，請聯繫客服人員以完成付款。"
            )
            offline_payment_table = Table(
                [[
                    Paragraph(
                        "Remittance Details Unavailable｜匯款資訊暫缺",
                        styles['BodyTextCustomBold'],
                    )
                ], [
                    Paragraph(unavailable_html, styles['BodyTextCustom'])
                ]],
                colWidths=[174 * mm],
            )
            offline_payment_table.hAlign = 'LEFT'
            offline_payment_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff5f5')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5b3b3')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
        else:
            # ── Amount to wire is in the order's own currency ─────
            # total_due is CNY (base); total_due_foreign is the amount
            # in the buyer's chosen currency.
            if currency_code == "CNY":
                wire_amount = order.total_due
                wire_symbol = "¥"
                wire_is_integer = False
            else:
                wire_amount = order.total_due_foreign
                wire_symbol = CURRENCY_SYMBOL.get(currency_code, "")
                wire_is_integer = currency_code in INTEGER_CURRENCIES

            # ── Bank details, single-column layout ────────────────
            # <br/> between fields is required: without a separator the
            # f-strings concatenate into a single run-on line.
            bank_details_html = "<br/>".join([
                f"<b>Bank Name｜開戶銀行:</b> {escape_for_pdf(account['bank_name'])}",
                f"<b>Account Name｜開戶名稱:</b> {escape_for_pdf(account['account_name'])}",
                f"<b>Account Number｜銀行帳號:</b> {escape_for_pdf(account['account_number'])}",
                f"<b>Swift Code｜國際代碼:</b> {escape_for_pdf(account['swift'])}",
                *([f"<b>Bank Address｜銀行地址:</b> {escape_for_pdf(account['bank_address'])}"]
                  if account.get('bank_address') else []),
                "",
                f"<b>Total Due ({currency_code})｜應付總額:</b> "
                f"{format_currency(wire_amount, wire_symbol, is_integer=wire_is_integer)}",
                "",
                f"<i>*Important: Please include your order number "
                f"{order.order_number} in the transfer memo.</i>",
                f"<i>*重要提示：請務必在匯款備註/附言中填寫您的訂單號碼 "
                f"{order.order_number}。</i>",
            ])

            bank_title_para = Paragraph(
                "Remittance Bank Details｜銀行轉帳帳號資訊",
                styles['BodyTextCustomBold'],
            )
            bank_text_block = Paragraph(bank_details_html, styles['BodyTextCustom'])

            offline_payment_table = Table(
                [[bank_title_para], [bank_text_block]],
                colWidths=[174 * mm],
            )
            offline_payment_table.hAlign = 'LEFT'
            offline_payment_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7f5f3')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))        

    # (g) Footer
    footer_text = Paragraph(
        "If you have any further enquiries, please do not hesitate to contact us at admin@xindeng.com. "\
        "若您有任何疑問，請隨時透過郵件聯絡我們：admin@xindeng.com<br/>",
        styles["FooterBold"]
    )
    current_year = timezone.now().year
    footer_html = (
        f"© {current_year} "
        "<font name='SanskritFont' size='10'>Hṛdayadīpa (हृदयदीप)｜</font> "
        "心燈 All Rights Reserved."
    )
    footer_mixed_style = ParagraphStyle(
        "MixedStyle",
        fontName="NotoSansTC-Regular",
        fontSize=10,
        leading=20,
    )
    footer_html_p = Paragraph(footer_html, footer_mixed_style)

    # Append all compiled components sequentially over to ReportLab structural array pipelines

    elements.extend([
        header_table, Spacer(1, 5*mm),
        title_table, Spacer(1, 5*mm),
        Paragraph(p1, styles['BodyTextCustom']), Spacer(1, 2*mm),
        Paragraph(p2, styles['BodyTextCustom']), Spacer(1, 2*mm),
        Paragraph(p3, styles['BodyTextCustom']), Spacer(1, 6*mm),
        Paragraph("Customer Information｜客戶訊息", styles['SectionHeading']),
        name_table, contact_table, Spacer(1, 6*mm),
        Paragraph("Payment Parameters｜支付參數", styles['SectionHeading']),
        payment_1_table, payment_2_table, Spacer(1, 6*mm),
    ])

    if order.state_province_region != "Digital":
        elements.append(
            KeepTogether(
                [Paragraph("Shipping Manifest｜物流詳情", styles['SectionHeading'])]
                + shipping_manifest_elements
            )
        )
        elements.append(Spacer(1, 10*mm))
    else:
        elements.append(PageBreak())
    
    # Resume pushing the remainder of your item rows and ledgers
    elements.extend([
        KeepTogether([
            Paragraph("Ordered Items｜訂購明細", styles['SectionHeading']),
            p_table,
        ]),
        Spacer(1, 6*mm),
        KeepTogether([
            Paragraph("Financial Summary｜財務總結", styles['SectionHeading']),
            s_table,
        ]),
    ])

    # 🌟 SURGICAL INJECTION: Mount the offline banking block conditionally right below calculations!
    if is_bank_transfer and offline_payment_table:
        elements.extend([
            Spacer(1, 6*mm),
            offline_payment_table
        ])

    elements.extend([
        Spacer(1, 8*mm),
        footer_text, Spacer(1, 5*mm),
        footer_html_p
    ])

    doc.build(elements)
    buffer.seek(0)
    return buffer


def format_accounting_currency(value, symbol, is_integer=False):
    """
    Formats decimal values with thousands separators, explicit currency symbols, 
    and wraps negative figures inside parentheses.
    Example: 100.00 -> ¥ 100.00 | -100.00 -> ¥ (100.00)
    """
    if value is None:
        value = 0.00
    
    val_decimal = Decimal(str(value))
    is_negative = val_decimal < 0
    abs_value = abs(val_decimal)
    
    if is_integer:
        formatted_number = intcomma(f"{abs_value:.0f}")
    else:
        formatted_number = intcomma(f"{abs_value:.2f}")
        
    if is_negative:
        return f"{symbol} ({formatted_number})"

    print(f"{symbol} {formatted_number}")
    return f"{symbol} {formatted_number}"

    # return value


def fmt(val, integer=False):
    """Formats numeric entities cleanly depending on decimal rules."""
    if integer:
        return "{:.0f}".format(float(val)) if val is not None else "0"
    return "{:.2f}".format(float(val)) if val is not None else "0.00"


def evaluate_checkout_offer_eligibility(request, cart):
    """
    Enforces identical validation logic as apply_offer during the final payment execution phase.
    Returns (is_valid, error_title, error_text)
    """
    # 1. Pull the active offer data from the user's session cache
    offer_session = request.session.get("offer_applied", {})
    offer_code = offer_session.get("offer_code")
    
    # If no offer was selected/applied, bypass validation checks safely
    if not offer_code:
        return True, None, None

    user = request.user
    code = offer_code.strip().upper()
    perk = None

    # 2. Re-run Polymorphic Lookup Pipeline Track
    if user and user.is_authenticated:
        try:
            user_perk = UserPerk.objects.select_related('perk').get(user=user, unique_code=code)
            perk = user_perk.perk
        except UserPerk.DoesNotExist:
            perk = None

    if not perk:
        perk = Perk.objects.filter(code=code, is_active=True).first()

    if not perk:
        return False, "Invalid Code | 優惠碼失效", "The promo code attached to this session is no longer valid.<br>套用的優惠碼已失效，請重新調整。"

    # 3. Evaluate eligibility conditions via the core evaluation module
    status = PerkEvaluator.get_eligibility_status(user, perk)
    
    if status != "VALID":
        # Clear out the stale session parameters immediately to prevent checkout lock traps
        request.session["offer_applied"] = {"offer_code": "", "discount_amount": "0.00", "discount_amount_foreign": "0.00"}
        request.session.modified = True
        
        # Map bilingual warnings matching your handle_perk_status rules
        if status == "OUT_OF_STOCK":
            return False, "Limit Reached | 優惠名額已滿", "All available offers have been claimed.<br>此優惠名額已滿，感謝您的支持。"
        elif status == "ALREADY_USED":
            return False, "Already Redeemed | 此優惠碼已使用", "This promo code has already been used.<br>您已使用過此優惠碼。"
        elif status in ["EXPIRED", "THIS_BIRTHDAY_PERK_EXPIRED", "NEW_MEMBER_PERK_EXPIRED"]:
            return False, "Offer Expired | 優惠已過期", "Sorry, this offer has expired.<br>抱歉！您套用的優惠碼已過期。"
        else:
            return False, "Eligibility Error | 條件不符", "You are no longer eligible for this offer.<br>您不符合此優惠之使用條件。"

    # 4. Enforce strict Minimum Spend Threshold check (Excluding Voucher Items)
    cart_base_total = Decimal(str(cart.get_cart_total_ex_voucher()).replace(",", ""))
    perk_min_spending = Decimal(str(perk.safe_min_spending).replace(",", ""))
    
    if cart_base_total < perk_min_spending:
        request.session["offer_applied"] = {"offer_code": "", "discount_amount": "0.00", "discount_amount_foreign": "0.00"}
        request.session.modified = True
        return False, "Minimum Spend Not Met | 未達最低消費金額", f"This offer requires a minimum spend of CNY {perk.safe_min_spending:.2f} (excluding voucher items).<br>此優惠需消費滿 {perk.safe_min_spending:.2f} 元方可使用。"

    return True, None, None


@transaction.atomic
def mark_off_perk_at_checkout(user, session_code_string):
    """
    Atomically verifies eligibility one final time, locks the target perk rows, 
    increments usage counters safely, and marks user membership instances as used.
    """
    if not session_code_string:
        return None

    code_clean = session_code_string.strip().upper()
    perk = None
    user_perk_instance = None

    # 1. Row-level Lock Match Track (Polymorphic Validation Layer)
    if user and user.is_authenticated:
        try:
            # Lock the personal assignment code immediately
            user_perk_instance = UserPerk.objects.select_for_update().get(
                user=user, 
                unique_code=code_clean, 
                is_used=False
            )
            perk = Perk.objects.select_for_update().get(pk=user_perk_instance.perk.pk)
        except UserPerk.DoesNotExist:
            user_perk_instance = None

    if not perk:
        # Fall back to checking global registry configurations under strict lock
        perk = Perk.objects.select_for_update().filter(code=code_clean, is_active=True).first()

    if not perk:
        raise ValidationError("This offer code is no longer available.｜優惠碼不存在或已失效。")

    # 2. Final Second Re-Evaluation Pass
    status = PerkEvaluator.get_eligibility_status(user, perk)
    if status != "VALID":
        raise ValidationError(f"Offer validation conditions failed: {status}.｜條件不符，無法套用此優惠。")

    # 3. Increment Global Counter using row-locked atomic assignments
    success = perk.increment_usage()
    if not success:
        raise ValidationError("Sorry, this limited offer just ran out!｜抱歉，此優惠名額剛剛已滿！")

    # 4. Mark User Membership instances as settled
    if user_perk_instance:
        user_perk_instance.is_used = True
        user_perk_instance.used_at = timezone.now()
        # user_perk_instance.save(update_fields=['is_used', 'used_at'])
        user_perk_instance.save()
    elif user and user.is_authenticated:
        # Fallback tracking if they used a global code name string directly
        # Marks the first eligible matching instance found
        up = UserPerk.objects.select_for_update().filter(user=user, perk=perk, is_used=False, used_at__isnull=True).first()
        if up:
            up.is_used = True
            up.used_at = timezone.now()
            # up.save(update_fields=['is_used', 'used_at'])
            up.save()
            
    return perk


@transaction.atomic
def reverse_perk_usage_at_cancellation(order_instance):
    """
    Atomically rolls back coupon usage counts and restores individual customer 
    Perk vouchers if a bank transfer hold expires or is aborted.
    """
    # Look at your Order model parameters: we store the string snapshot in order.payment or proforma reference
    # Assuming your Order model captures the applied coupon code as a plain text string field
    # (e.g., if order.coupon_code or proforma_invoice.offer_code was stored during views.py)
    
    # Let's extract the clean coupon string via your ProformaInvoice or Order snapshots:
    offer_code_string = getattr(order_instance, 'coupon_code', None)
    if not offer_code_string:
        # Fallback tracking lookup: parse from your settings or related ProformaInvoice table
        # from store.models import ProformaInvoice
        proforma = ProformaInvoice.objects.filter(proforma_order_number=order_instance.order_number).first()
        offer_code_string = proforma.offer_code if proforma else None

    if not offer_code_string:
        return f"No coupon code associated with Order {order_instance.order_number}. Rollback skipped."

    code_clean = offer_code_string.strip().upper()
    user = order_instance.user

    # 1. Row-lock and decrement the Global Perk counter
    perk = Perk.objects.select_for_update().filter(code=code_clean).first()
    if not perk and user:
        # Check if they used a unique personal UserPerk alphanumeric tracking code identifier
        user_perk = UserPerk.objects.filter(user=user, unique_code=code_clean).first()
        if user_perk:
            perk = Perk.objects.select_for_update().get(pk=user_perk.perk.pk)

    if perk:
        # Surgically subtract 1 from the global counter, preventing it from slipping below 0
        if perk.uses_count > 0:
            perk.uses_count = F('uses_count') - 1
            perk.save(update_fields=['uses_count'])

    # 2. Row-lock and Restore the User's personal allocation eligibility
    if user and user.is_authenticated and perk:
        # Check if they checked out using their unique specific code first
        up = UserPerk.objects.select_for_update().filter(
            user=user, 
            perk=perk, 
            is_used=True
        ).order_by('-used_at').first()  # Grabs the most recently consumed instance row
        
        if up:
            up.is_used = False
            up.used_at = None
            up.save(update_fields=['is_used', 'used_at'])
            return f"Successfully restored personal voucher code {code_clean} for user {user.email}."

    return f"Successfully decremented global counter for code {code_clean}."


def execute_atomic_voucher_deduction(user, session_input_amount):
    """
    Locks and drains user cash voucher profiles oldest-to-newest inside a transaction block.
    Returns the usage metrics mapping list necessary for OrderVoucherUsage creation loops.
    """
    if not session_input_amount or Decimal(str(session_input_amount)) <= 0:
        return []

    target_deduction = Decimal(str(session_input_amount).replace(",", ""))
    
    # Row-lock available claimed vouchers using select_for_update()
    vouchers = CustomerVoucher.objects.select_for_update().filter(
        owner=user, 
        is_claimed=True, 
        is_used=False, 
        balance__gt=0
    ).order_by('created_date')
    
    remaining_to_deduct = target_deduction
    usage_records = []

    for voucher in vouchers:
        if remaining_to_deduct <= 0:
            break
            
        deduction = min(voucher.balance, remaining_to_deduct)
        voucher.balance -= deduction
        
        # 💡 CLEANUP: Clear out active session locks upon final balance deduction
        voucher.is_locked = False
        voucher.locked_at = None
        voucher.locked_by_session = None
        
        if voucher.balance <= 0:
            voucher.is_used = True
            voucher.used_date = timezone.now()
            
        voucher.save(update_fields=['balance', 'is_used', 'used_date', 'is_locked', 'locked_at', 'locked_by_session'])
        
        usage_records.append({
            'voucher_instance': voucher,
            'amount': deduction
        })
        remaining_to_deduct -= deduction
    
    if remaining_to_deduct > 0:
        raise ValueError("交易校驗失敗｜Voucher balance tracking drift caught during deduction execution.")
        
    return usage_records  # 🌟 Net Fix: Correctly returns the list matrix for your views to iterate over!


# @@@@@@ PAYPAL @@@@@@ #
def get_paypal_items(cart_items, foreign_currency_code, locked_rate, cart_total_foreign):
    """
    Transforms active cart elements into modern PayPal SDK Item representations.
    Tracks structural subtotal rows dynamically inside precise Decimal layers.
    """
    items_list = []
    amount_total_foreign = Decimal('0.00')
    is_int = foreign_currency_code in INTEGER_CURRENCIES
    
    exponent = Decimal('1') if is_int else Decimal('0.01')
    rate_decimal = Decimal(str(locked_rate))

    for cart_item in cart_items:
        fmt_category = "PHYSICAL_GOODS"
        if cart_item.product_variation.product.category.product_format == "e-product":
            fmt_category = "DIGITAL_GOODS"
        elif cart_item.product_variation.product.category.product_format == "donation":
            fmt_category = "DONATION"

        # Apply direct row-level quantization to prevent floating point drifts
        base_price = Decimal(str(cart_item.product_variation.price))
        unit_price_foreign = (base_price * rate_decimal).quantize(exponent, rounding=ROUND_HALF_UP)
        
        amount_total_foreign += unit_price_foreign * Decimal(cart_item.quantity)

        item = Item( 
            name=str(cart_item.product_variation.product.product_name)[:127],
            unit_amount=Money(currency_code=foreign_currency_code, value=fmt(unit_price_foreign, integer=is_int)),
            quantity=str(cart_item.quantity),
            sku=str(cart_item.product_variation.get_sku()),
            category=fmt_category
        )
        items_list.append(item)
    
    # Calculate exact remainder adjustment using balanced decimal vectors
    target_subtotal = Decimal(str(cart_total_foreign))
    rounding_adjustment = target_subtotal - amount_total_foreign

    return {
        "items_list": items_list,
        "amount_total_foreign": amount_total_foreign,
        "rounding_adjustment": rounding_adjustment
    }





# (1) page-setting
# A4, padding: vertical 2rem, horizontal 3rem

# (2) Top Line (same as display: flex, lined up horizontally, same as "justify-content: start")
# - logo (1.5cm * 1.5cm), left corner
# - gap of 1rem
# - Shop Name Text : "心燈｜Hṛdayadīpa (हृदयदीप)"

# * vertical alignment: same as "align-items: center"
# * font size: 1.5rem
# * font weight: bold
# * line height: 1.5
# * text: f"訂單確認｜Order Confirmation &nbsp;&nbsp; {order.order_number}"
# * text font-size will be 2rem
# * font style for the part of {order.order_number} above will be same as:
# font-family: "Libre Barcode 128", system-ui;
# font-weight: 400;
# font-style: normal;

# (3) Greeting
# text = f"您好{username}！｜Hello {username}!"
# font-weight: 700;
# font-size: 1.2rem;

# (4) Paragraph 1
# text = f"感謝您在本店購物！您的訂單號碼是<strong>{order.order_number}</strong>。<br/>
# Thank you for shopping with us! Your order number is <strong>{order.order_number}</strong>."

# (5) Paragraph 2
# text = "我們會在您的實體產品包裹發出時通知您。<br/>
# We will notify you when your physical product(s) parcel(s) is/are dispatched"

# (6) Paragraph 3
# text = "您的電子產品將透過另一封電子郵件發送給您。<br/>
# 如果您收不到郵件，請及時聯繫我們。<br/>
# 如果您已在我們這裡註冊，您也可以透過您的會員控制面板獲取您所購買的電子產品。<br/>
# 會員登入鏈接：https://xxxx.com/login<br/>
# Your e-product(s) will be sent to you via another email.<br/>
# Please notify us if you have issue receiving the email.<br/>
# If you have registered with us, you can also retrieve your e-product(s) via your member dashboard.<br/>
# Member login link: https://xxxx.com/login"

# (4) ~ (6)
# * font-size: 1rem
# * font-weight: regular (300?)
# * gap between paragraphs: 1 line (1rem?)

# (7) Sections (Title & Details in Table, each line includes label and underline)
# <div class="order_item_row" style="margin: 2rem 0;">
    # <div class="section_title" style="margin-top: 3rem;">
    #     α 客戶訊息｜Customer Details
    # </div>
    # <table class="details-table mb-5" style="margin-left: 0.15rem;">
    #     {% if user != None %}
    #         <tr>
    #             <td>
    #                 <div class="label-xs">名｜first name</div>
    #                 <div class="details-text-size"><strong>{{ user.first_name }}</strong></div>
    #             </td>
    #             <td>
    #                 <div class="label-xs">姓｜last name</div>
    #                 <div class="details-text-size"><strong>{{ user.last_name }}</strong></div>
    #             </td>
    #             <td>
    #                 <div class="label-xs">用戶名｜username</div>
    #                 <div class="details-text-size"><strong>{{ user.username }}</strong></div>
    #             </td>
    #         </tr>
    #     {% else %}
    #         <tr>
    #             <td>
    #                 <div class="label-xs">名字｜name</div>
    #                 <div class="px-1 font-normal details-text-size">訪客用戶｜Guest User</div>
    #             </td>
    #         </tr>
    #     {% endif %}
    # </table>
    # <table class="details-table mb-5" style="margin-left: 0.15rem;">
    #     <tr>
    #         <td>
    #             <div class="label-xs">電郵｜email</div>
    #             <div class="details-text-size"><strong>{{ order.email }}</strong></div>
    #         </td>
    #         <td>
    #             <div class="label-xs">電話｜phone</div>
    #             <div class="details-text-size"><strong>{{ user.mobile_area }}&nbsp;{{ user.mobile_number }}</strong></div>
    #         </td>
    #     </tr>
    # </table>
# </div>

# .order_item_row {break-inside: avoid;}
# .section_title {font-size: 1.1rem; font-weight: 600; margin: 1rem 0;}
# .details-table { width: 100%; border-spacing: 1.5rem 0; margin-left: -1.5rem; }
# .details-table td { border-bottom: 1px solid #ccc; padding: 0.25rem; width: 33%; vertical-align: bottom; }
# .mb-5 {margin-bottom: 1.25rem}
# .label-xs { font-size: 0.75rem; color: #666; }
# .details-text-size {font-size: 0.95rem;}
# .px-1 {padding-left: 0.25rem; padding-right: 0.25rem;}
# .font-normal {--tw-font-weight: 400; font-weight: 400;}
# .details-text-size {font-size: 0.95rem;}

# (8) Product List (dynamic generation) & Price Summary
# * container with background color of #e8e7e7
# * padding: 1.5rem

# * A: Top Table (product list)
# * Table Heading: [col1: blank, col2-col3: "商品｜Product", col4: "價格｜Price", col5: "數量｜Qty", col6: "小計｜Sub-Total" ]
# * border-bottom: 2px solid #6864611a;
# * Table Rows (dynamically generated: for product in order_products:...loop):
# * col1: counter
# * col2: product image (order_product.image.url)
# * col3: product name (order_product.product_variation (__str__())
# * col4: product price
# * col5: product quantity
# * col6: product subtotal (product price * quantity)
# * border-bottom: 1px solid #eee;

# * divider between top and bottom tables: divider {
#     display: flex;
#     height: calc(0.25rem * 4);
#     flex-direction: row;
#     align-items: center;
#     align-self: stretch;
#     white-space: nowrap;
#     margin: 0.5rem 0;
#     --divider-color: #68646054;
# }

# * B: Bottom Table (price summary)
# * width: 100%
# * Table Heading: [col1: blank, col2: CNY, col3: {payment.currency}]
# * Col3 exists only if payment.currency is not CNY. 
# * Table Rows:
# * row1: ["商品小計｜Products", {order.product_total}, optional: {product_total_foreign_currency}]
# * row2: ["運費｜Shipping", {order.shipping}, optional: {shipping_foreign_currency}]
# * row3: ["優惠｜Discount", {order.discount}, optional: {discount_foreign_currency}]
# * row4: ["稅&通關费用｜Tax & Duty", {order.tax}, optional: {tax_foreign_currency}]
# * row5: ["禮品券｜Voucher", {order.voucher}, optional: {voucher_foreign_currency}]
# * row6: ["總收款金額｜Total Received", {order.total_due}, optional: {total_due_foreign_currency}]
# * row6 font: font-weight: 600
# * col1: text-alignt: left, col2 & col3: text-align: right

# (9) Footer
# * paragraph1: "若您有任何疑問，請隨時透過 admin@xindeng.com 聯絡我們，或造訪我們的聯絡頁面：https://xindeng.com/contact。<br/>
#   If you have any further enquiries, please do not hesitate to contact us at admin@xindeng.com or visit our contact page: https://xindeng.com/contact."
# * font-size: 0.8rem
# * font-weight: 300
# * text-align: justified
# * line-height: 1.5
# * margin-top: 2rem
# * paragraph2: "© 2024 心燈｜Hṛdayadīpa (हृदयदीप) All Rights Reserved."
# * text-align: center