from django.core.cache import cache
from accounts.data import DEFAULT_EXCHANGE_RATE_VS_CNY, INTERNAL_CURRENCY_ADJUSTMENT, CURRENCY_SYMBOL, INTEGER_CURRENCIES
from decimal import Decimal, ROUND_HALF_UP
from .models import Order, OrderProduct
from carts.models import ProformaInvoice
import io
import os
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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# paypal
from paypalserversdk.models.item import Item
from paypalserversdk.models.money import Money

# from reportlab.lib.styles import ParagraphStyle
# from reportlab.lib.enums import TA_LEFT
# from reportlab.lib import colors



def get_current_rate(base_currency_code="CNY", target_currency_code="HKD"):
    """
    Retrieves the rate from Redis cache. 
    If cache is empty, returns a fallback or triggers a manual fetch.
    """
    try:
        all_rates = cache.get('exchange_rates')
        if all_rates:
            if all_rates[base_currency_code] is not None:
                usd_base_currency = all_rates.get(base_currency_code)
            else:
                usd_base_currency = all_rates.get("CNH")
            usd_target_currency = all_rates.get(target_currency_code)
            target_base_exchange_rate = (usd_target_currency / usd_base_currency) * INTERNAL_CURRENCY_ADJUSTMENT
            target_base_exchange_rate = Decimal(str(target_base_exchange_rate).replace(",", "")).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            
            return float(target_base_exchange_rate)
    except:
    # Fallback: You can manually call the task or return a default value
        fallback_rate = DEFAULT_EXCHANGE_RATE_VS_CNY[target_currency_code] * INTERNAL_CURRENCY_ADJUSTMENT
        fallback_rate = Decimal(str(fallback_rate).replace(",", "")).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
        
        return float(fallback_rate)


def register_multilingual_fonts():
    font_dir = os.path.join(settings.BASE_DIR, 'static/fonts')
    
    # 1. Main Font: Chinese + English
    pdfmetrics.registerFont(TTFont('NotoSansTC-regular', os.path.join(font_dir, 'NotoSansTC-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTC-bold', os.path.join(font_dir, 'NotoSansTC-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTC-light', os.path.join(font_dir, 'NotoSansTC-Light.ttf')))
    pdfmetrics.registerFont(TTFont('NotoSansTC-thin', os.path.join(font_dir, 'NotoSansTC-Thin.ttf')))
    
    # 2. Sanskrit Font: Devanagari + IAST Diacritics (Hṛdayadīpa)
    # Tiro Devanagari is excellent for Sanskrit
    pdfmetrics.registerFont(TTFont('SanskritFont', os.path.join(font_dir, 'TiroDevanagariSanskrit-Regular.ttf')))

    # 3. Dejavu Sans: Symbols
    pdfmetrics.registerFont(TTFont('DejaVuSans-regular', os.path.join(font_dir, 'DejaVuSans-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('DejaVuSans-bold', os.path.join(font_dir, 'DejaVuSans-Bold.ttf')))

    # 4, Barcode
    pdfmetrics.registerFont(TTFont('Barcode128', os.path.join(font_dir, 'LibreBarcode128-Regular.ttf')))


def get_pdf_styles():
    styles = getSampleStyleSheet()
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')

    # register various fonts
    register_multilingual_fonts()

    styles.add(ParagraphStyle(
        name='ShopName', fontName='NotoSansTC-bold', fontSize=16, leading=24
    ))
    # styles.add(ParagraphStyle(
    #     name='OrderTitle', fontName='NotoSansTC-bold', fontSize=22, leading=30
    # ))
    styles.add(ParagraphStyle(
        name='OrderTitle', fontName='NotoSansTC-Bold', fontSize=22, leading=26, spaceAfter=0, spaceBefore=0 # CRITICAL: Remove extra space
    ))

    # styles.add(ParagraphStyle(
    #     name='Barcode', fontName='Barcode128', fontSize=32, leading=32
    # ))
    styles.add(ParagraphStyle(
        name='Barcode', fontName='Barcode128', fontSize=32, leading=32, spaceAfter=0, spaceBefore=0
    ))
    styles.add(ParagraphStyle(
        name='Greeting', fontName='NotoSansTC-bold', fontSize=13, leading=18, spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='BodyTextCustom', fontName='NotoSansTC-regular', fontSize=10, leading=15, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        name='ProductDescription', fontName='NotoSansTC-light', fontSize=10, leading=15, spaceAfter=5, 
        # wordWrap='LTR'
        # 'CJK' is best for Chinese/Japanese/Korean wrapping
        # OR use wordWrap='LTR' for standard Western text wrapping
    ))
    styles.add(ParagraphStyle(
        name='LabelXS', fontName='NotoSansTC-regular', fontSize=8, textColor=colors.HexColor('#666666'), spaceAfter=1.0,
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle', fontName='NotoSansTC-bold', fontSize=12, spaceBefore=20, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='FooterBold', fontName='NotoSansTC-bold', fontSize=10, spaceBefore=18, spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        name='SanskritTitle', fontName='SanskritFont', fontSize=16, leading=24
    ))
    styles.add(ParagraphStyle(name='AlignLeft', alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='AlignCenter', fontName='NotoSansTC-light', alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='AlignRight', alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='AlignJustify',alignment=TA_JUSTIFY))

    styles.add(ParagraphStyle(
        name='SectionHeading', 
        fontName='NotoSansTC-bold', 
        fontSize=11, 
        leading=14, 
        textColor=colors.HexColor('#686461'), 
        spaceBefore=10, 
        spaceAfter=6, 
        alignment=TA_LEFT
    ))

    return styles


def get_header_element(styles):
    shop_name_html = (
        "<font name='SanskritFont' size='15'>Hṛdayadīpa (हृदयदीप)</font>｜"
        "心燈"
    )
    mixed_style = ParagraphStyle(
        "MixedStyle",
        fontName="NotoSansTC-bold",
        fontSize=16,
        leading=20,
    )
    return Paragraph(shop_name_html, mixed_style)


def foreign_currency_formatter(number, currency):
    currency_symbol = CURRENCY_SYMBOL[currency]

    if currency in INTEGER_CURRENCIES:
        return f"{currency_symbol}{Decimal(str(number).replace(",", "")):,.0f}"
    else:
        return f"{currency_symbol}{Decimal(str(number).replace(",", "")):,.2f}"


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
    logo_path = os.path.join(settings.STATIC_ROOT, 'images/miscellaneous/logo_square.png')
    logo = Image(logo_path, 15*mm, 15*mm) if os.path.exists(logo_path) else "[Logo]"
    shop_paragraph = get_header_element(styles) # Hṛdayadīpa (हृदयदीप)｜心燈

    header_table = Table([[logo, shop_paragraph]], colWidths=[15*mm, 130*mm])
    header_table.hAlign = 'LEFT'
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (0,0), 0),
    ]))

    # (b) Order Confirmation Title + Barcode
    title_data = [[
        Paragraph(f"Order Confirmation｜訂單確認", styles['OrderTitle']),
        Paragraph(order.order_number, styles['Barcode'])
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

    p1 = f"Thank you for shopping with us!<br/>感謝您在本店購物！"
    p2 = "We will notify you when your physical product(s) parcel is dispatched.<br/>我們會在您的實體產品包裹發出時通知您。"
    p3 = "Your e-product(s), if any, will be sent via another email.<br/>如果您有購買電子產品，我們將透過另一封電子郵件發送給您。"

    # (d) Order Details Section
    # *** Name ***
    if user:
        name_data = [[
            [Paragraph("First Name｜名", styles['LabelXS']), Paragraph(f"<b>{user.first_name if user.first_name else '&nbsp;'}</b>", styles['BodyTextCustom'])],
            [Paragraph("Last Name｜姓", styles['LabelXS']), Paragraph(f"<b>{user.last_name if user.last_name else '&nbsp;'}</b>", styles['BodyTextCustom'])],
            [Paragraph("Username｜用戶名", styles['LabelXS']), Paragraph(f"<b>{username if username else '&nbsp;'}</b>", styles['BodyTextCustom'])]
        ]]
        name_table = Table(name_data, colWidths=[58*mm, 58*mm, 58*mm])
    else:
        name_data = [[Paragraph("Guest User｜訪客用戶", styles["BodyTextCustom"]), "", ""]]
        name_table = Table(name_data, colWidths=[174*mm])
    name_table.hAlign = "LEFT"

    # *** contact ***
    contact_data = [[
        [Paragraph("Email｜電郵", styles['LabelXS']), Paragraph(f"<b>{order.email if order.email else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Phone｜電話", styles['LabelXS']), Paragraph(f"<b>{order.recipient_mobile_area if order.recipient_mobile_area else ''}&nbsp;{order.recipient_mobile_number}</b>", styles['BodyTextCustom'])]
    ]]
    contact_table = Table(contact_data, colWidths=[87*mm, 87*mm])
    contact_table.hAlign = "LEFT"

    # *** payment line_1 ***
    payment_1_data = [[
        [Paragraph("Payment Method｜支付方式", styles['LabelXS']), Paragraph(f"<b>{order.payment.payment_method if order.payment else 'Bank Transfer ｜ 銀行轉帳'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Transaction ID｜交易ID", styles['LabelXS']), Paragraph(f"<b>{order.payment.payment_id if order.payment else 'Pending Manual Hold ｜ 待核對'}</b>", styles['BodyTextCustom'])]        
    ]]
    payment_1_table = Table(payment_1_data, colWidths=[87*mm, 87*mm])
    payment_1_table.hAlign = "LEFT"

    # *** payment line_2 ***
    if order.payment:
        amount_to_format = order.payment.amount_paid
    else:
        # Fall back to your multi-currency names matching earlier ledger setups
        # If order doesn't store a currency name string, default safely to CNY or your cookies currency
        currency_code = getattr(order, 'currency', 'CNY') or 'CNY'
        amount_to_format = order.total_due

    # Execute string formatting matching your integer currency array constraints
    payment_amount = f"{Decimal(str(amount_to_format).replace(',', '')):,.0f}" if is_integer else f"{Decimal(str(amount_to_format).replace(',', '')):,.2f}"
    currency_symbol = CURRENCY_SYMBOL.get(currency_code, "")

    payment_2_data = [[
        [Paragraph("Payment Currency｜付款貨幣", styles['LabelXS']), Paragraph(f"<b>{currency_code if currency_code else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Payment Amount｜支付金額", styles['LabelXS']), Paragraph(f"<b>{currency_code} {currency_symbol}{payment_amount}</b>", styles['BodyTextCustom'])]    
    ]]
    payment_2_table = Table(payment_2_data, colWidths=[87*mm, 87*mm])
    payment_2_table.hAlign = "LEFT"

    # *** shipping info_1 ***
    shipping_1_data = [[
        [Paragraph("Recipient Last Name｜收件人 姓", styles['LabelXS']), Paragraph(f"<b>{order.recipient_first_name if order.recipient_first_name else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Recipient First Name｜收件人 名", styles['LabelXS']), Paragraph(f"<b>{order.recipient_last_name if order.recipient_last_name else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Recipient Phone｜收件人電話", styles['LabelXS']), Paragraph(f"<b>{order.recipient_mobile_area}&nbsp;{order.recipient_mobile_number}</b>" if order.recipient_mobile_area and order.recipient_mobile_number else "&nbsp;", styles['BodyTextCustom'])]
    ]]
    shipping_1_table = Table(shipping_1_data, colWidths=[58*mm, 58*mm, 58*mm])
    shipping_1_table.hAlign = "LEFT"
    
    # *** shipping info_2 ***
    street_address_data = f"{order.address_line_1}, {order.address_line_2}" if order.address_line_2 else f"{order.address_line_1}"
    shipping_2_data = [[
        [Paragraph("Street Address｜街道地址", styles['LabelXS']), Paragraph(f"<b>{street_address_data if order.address_line_1 else '&nbsp;'}</b>", styles['BodyTextCustom'])],
    ]]
    shipping_2_table = Table(shipping_2_data, colWidths=[174*mm])
    shipping_2_table.hAlign = "LEFT"

    # *** shipping info_3 ***
    shipping_3_data = [[
        [Paragraph("City｜城市", styles['LabelXS']), Paragraph(f"<b>{order.city if order.city else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("State/Province ｜ 州/省/縣", styles['LabelXS']), Paragraph(f"<b>{order.state_province_region if order.state_province_region else '&nbsp;'}</b>", styles['BodyTextCustom'])],
    ]]
    shipping_3_table = Table(shipping_3_data, colWidths=[87*mm, 87*mm])
    shipping_3_table.hAlign = "LEFT"

    # *** shipping info_4 ***
    raw_country = order.get_country_display() if hasattr(order, 'get_country_display') else ""
    name_part = raw_country[:-2].strip() if raw_country and " " in raw_country else raw_country

    shipping_4_data = [[
        [Paragraph("Country / Region｜國家/地區", styles['LabelXS']), Paragraph(f"<b>{name_part if order.country else '&nbsp;'}</b>", styles['BodyTextCustom'])],
        [Paragraph("Post Code｜郵編", styles['LabelXS']), Paragraph(f"<b>{order.postal_code if order.postal_code else '&nbsp;'}</b>", styles['BodyTextCustom'])],
    ]]
    shipping_4_table = Table(shipping_4_data, colWidths=[87*mm, 87*mm])
    shipping_4_table.hAlign = "LEFT"

    # *** shipping info_5 ***
    shipping_5_data = [[
        [Paragraph("Delivery Note｜配送備注", styles['LabelXS']), Paragraph(f"<b>{order.delivery_note if order.delivery_note else '&nbsp;'}</b>", styles['BodyTextCustom'])],
    ]]
    shipping_5_table = Table(shipping_5_data, colWidths=[174*mm])
    shipping_5_table.hAlign = "LEFT"

    # *** shipping info_6 ***
    send_invoice = "Yes, include invoice with delivery. ｜ 是，將帳單一起配送。" if order.do_not_send_invoice == False \
                    else "No, do NOT include invoice with delivery.｜不，不要將帳單一起配送。"

    shipping_6_data = [[
        [Paragraph("Include invoice?｜附上帳單?", styles['LabelXS']), Paragraph(f"<b>{send_invoice}</b>", styles['BodyTextCustom'])],
    ]]
    shipping_6_table = Table(shipping_6_data, colWidths=[174*mm])
    shipping_6_table.hAlign = "LEFT"

    # details tables style formatting
    detail_tables = [name_table, contact_table, payment_1_table, payment_2_table, shipping_1_table, shipping_2_table, shipping_3_table, shipping_4_table, shipping_5_table, shipping_6_table]
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
        img_path = item.product_variation.images.path if item.product_variation and item.product_variation.images else ""
        p_img = Image(img_path, width=15*mm, height=12*mm) if img_path and os.path.exists(img_path) else ""
        product_name_flowable = Paragraph(str(item.product_variation), styles['ProductDescription'])
        product_data.append([
            idx, 
            p_img, 
            product_name_flowable,
            f"CNY ¥ {Decimal(str(item.product_price).replace(',', '')):,.2f}", 
            Paragraph(str(item.quantity), styles["AlignCenter"]), 
            f"CNY ¥ {Decimal(str(item.get_subtotal()).replace(',', '')):,.2f}"
        ])

    p_table = Table(product_data, colWidths=[8*mm, 20*mm, 60*mm, 32*mm, 22*mm, 32*mm])
    p_table.hAlign = "LEFT"
    p_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#e8e7e7")),
        ("FONTNAME", (0,0), (-1,0), "NotoSansTC-bold"),
        ("FONTNAME", (0,1), (-1,-1), "NotoSansTC-regular"),
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
    cny_prod = Decimal(str(order.product_total).replace(",", ""))
    cny_ship = Decimal(str(order.shipping_cost).replace(",", ""))
    cny_disc = Decimal(str(order.discount).replace(",", ""))
    cny_tax = Decimal(str(order.tax).replace(",", ""))
    cny_vouch = Decimal(str(order.voucher_applied).replace(",", ""))
    cny_due = Decimal(str(order.total_due).replace(",", ""))

    if currency_code != "CNY":
        fx_currency = currency_code
        fx_ship = Decimal(str(order.shipping_cost_foreign).replace(",", ""))
        fx_disc = Decimal(str(order.discount_foreign).replace(",", ""))
        fx_tax = Decimal(str(order.tax_foreign).replace(",", ""))
        fx_vouch = Decimal(str(order.voucher_applied_foreign).replace(",", ""))
        fx_due = Decimal(str(order.total_due_foreign).replace(",", ""))
        fx_subtotal = fx_due + fx_disc + fx_vouch - fx_tax - fx_ship

        summary_data = [
            ["", "CNY", f"{fx_currency}"],
            ["Products｜商品小計", f"¥ {intcomma(f'{cny_prod:.2f}')}", foreign_currency_formatter(fx_subtotal, fx_currency)],
            ["Shipping｜運費費率", f"¥ {intcomma(f'{cny_ship:.2f}')}", foreign_currency_formatter(fx_ship, fx_currency)],
        ]

        if cny_disc > 0:
            summary_data.append(["Discount (Less)｜優惠折抵 (扣減)", f"¥ ({intcomma(f'{cny_disc:.2f}')})", foreign_currency_formatter(fx_disc, fx_currency)])
        if cny_tax > 0:
            summary_data.append(["Tax & Duty｜代繳稅金", f"¥ {intcomma(f'{cny_tax:.2f}')}", foreign_currency_formatter(fx_tax, fx_currency)])
        if cny_vouch > 0:
            summary_data.append(["Voucher (Less)｜禮品卡折抵 (扣減)", f"¥ ({intcomma(f'{cny_vouch:.2f}')})", foreign_currency_formatter(fx_vouch, fx_currency)])
            
        summary_data.append(["Total Received｜總計應收", f"¥ {intcomma(f'{cny_due:.2f}')}", foreign_currency_formatter(fx_due, fx_currency)])
        s_table = Table(summary_data, colWidths=[70*mm, 52*mm, 52*mm])

    else:
        # Fallback simplified presentation column matrix layout for local currency checkouts
        summary_data = [
            ["", "CNY"],
            ["Products｜商品小計", f"¥ {intcomma(f'{cny_prod:.2f}')}"],
            ["Shipping｜運費費率", f"¥ {intcomma(f'{cny_ship:.2f}')}"]
        ]
        if cny_disc > 0:
            summary_data.append(["Discount (Less)｜優惠折抵 (扣減)", f"¥ ({intcomma(f'{cny_disc:.2f}')})"])
        if cny_tax > 0:
            summary_data.append(["Tax & Duty｜代繳稅金", f"¥ {intcomma(f'{cny_tax:.2f}')}"])
        if cny_vouch > 0:
            summary_data.append(["Voucher (Less)｜禮品卡折抵 (扣減)", f"¥ ({intcomma(f'{cny_vouch:.2f}')})"])
            
        summary_data.append(["Total Received｜總計應收", f"¥ {intcomma(f'{cny_due:.2f}')}"])
        s_table = Table(summary_data, colWidths=[100*mm, 74*mm])

    # Apply global summary layout aesthetics
    s_table.hAlign = 'LEFT'
    s_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'NotoSansTC-regular'),
        ('FONTNAME', (0,-1), (-1,-1), 'NotoSansTC-bold'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.lightgrey),
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.HexColor("#686461")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))

    # 🌟 NEW INJECTED SUBSECTION: OFFLINE REMITTANCE & MOBILE QR CODES (CONDITIONAL)
    is_bank_transfer = (proforma_invoice.payment_method == "BANK_TRANSFER")
    offline_payment_table = None
    if is_bank_transfer:
        bank_title_para = Paragraph("🏦 Remittance Bank Details｜銀行轉帳帳號資訊", styles['BodyTextCustom'])
        qr_title_para = Paragraph("📱 Mobile App Payment Directory｜行動支付搜尋明細", styles['BodyTextCustom'])
        bank_details_html = (
            f"Bank Name｜開戶銀行: Bank of China (Mainland)"
            f"Account Name｜開戶名稱: Xindeng Corporate Entity Ltd."
            f"Account Number｜銀行帳號: 6217 0000 0000 0000 000"
            f"Swift Code｜國際代碼: BKCHCNBJXXX"
            f"Total Due (CNY)｜應付總額: ¥ {order.total_due}"
            f"*Important: Please include your order number {order.order_number} in the transfer memo."
            f"*重要提示：請務必在匯款備註/附言中填寫您的訂單號碼 {order.order_number}。"
        )
        bank_text_block = Paragraph(bank_details_html, styles['BodyTextCustom'])
        mobile_details_html = (
            f"Alipay ID｜支付寶帳號: alipay@xindeng.art"
            f"Real Name｜實名認證: 心燈藝術 (Xindeng Art)"
            f"WeChat ID｜微信支付: wechat_xindeng"
            f"Real Name｜實名認證: 上海心燈文化傳播有限公司"
            f"*Tip: Scan the QR code or search using the Account IDs listed above."
            f"*提示：可直接掃描右側二維碼，或在App中搜尋上述帳號完成轉帳。")
        mobile_text_block = Paragraph(mobile_details_html, styles['BodyTextCustom'])
        
    # 🌟 EXTRACT AND SCALE YOUR STATIC ROOT QR GRAPHIC BINARY SAFELY
    qr_code_path = os.path.join(settings.STATIC_ROOT, 'images', 'miscellaneous', 'QR_codes.png')
    if os.path.exists(qr_code_path):
        qr_graphic_element = Image(qr_code_path, 40*mm, 26*mm)
        qr_graphic_element.hAlign = 'CENTER'
    
    # else:
    #     qr_graphic_element = Paragraph("[Payment QR Code Graphic Missing]", styles['LabelXS'])
    #     payment_instructions_matrix = [
    #         [bank_title_para, qr_title_para],
    #         [
    #             bank_text_block, 
    #             [
    #                 qr_graphic_element, 
    #                 Spacer(1, 1*mm), 
    #                 mobile_text_block
    #             ]
    #         ]
    #     ]
    #     offline_payment_table = Table(payment_instructions_matrix, colWidths=[87*mm, 87*mm])
    #     offline_payment_table.hAlign = 'LEFT'
    #     offline_payment_table.setStyle(TableStyle([
    #         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    #         ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7f5f3')),
    #         ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    #         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#e5e5e5')),
    #         ('TOPPADDING', (0, 0), (-1, -1), 8),
    #         ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    #         ('LEFTPADDING', (0, 0), (-1, -1), 10),
    #         ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    #     ]))

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
        fontName="NotoSansTC-regular",
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
        Paragraph("Shipping Manifest｜物流詳情", styles['SectionHeading']),
        shipping_1_table, shipping_2_table, shipping_3_table, shipping_4_table, shipping_5_table, shipping_6_table, Spacer(1, 10*mm),
        Paragraph("Ordered Items｜訂購明細", styles['SectionHeading']),
        p_table, Spacer(1, 6*mm),
        Paragraph("Financial Summary｜財務總結", styles['SectionHeading']),
        s_table,
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
        raise ValidationError("This offer code is no longer available. ｜ 優惠碼不存在或已失效。")

    # 2. Final Second Re-Evaluation Pass
    status = PerkEvaluator.get_eligibility_status(user, perk)
    if status != "VALID":
        raise ValidationError(f"Offer validation conditions failed: {status}. ｜ 條件不符，無法套用此優惠。")

    # 3. Increment Global Counter using row-locked atomic assignments
    success = perk.increment_usage()
    if not success:
        raise ValidationError("Sorry, this limited offer just ran out! ｜ 抱歉，此優惠名額剛剛已滿！")

    # 4. Mark User Membership instances as settled
    if user_perk_instance:
        user_perk_instance.is_used = True
        user_perk_instance.used_at = timezone.now()
        user_perk_instance.save(update_fields=['is_used', 'used_at'])
    elif user and user.is_authenticated:
        # Fallback tracking if they used a global code name string directly
        # Marks the first eligible matching instance found
        up = UserPerk.objects.select_for_update().filter(user=user, perk=perk, is_used=False).first()
        if up:
            up.is_used = True
            up.used_at = timezone.now()
            up.save(update_fields=['is_used', 'used_at'])

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
    vouchers = (
        CustomerVoucher.objects.select_for_update()
        .filter(owner=user, is_claimed=True, is_used=False, balance__gt=0)
        .order_by('created_date')  # Strict FIFO execution tracking anchor
    )
    
    total_available_balance = sum(v.balance for v in vouchers)
    if target_deduction > total_available_balance:
        raise ValueError(f"餘額不足 ｜ Insufficient voucher balance. Available: CNY {total_available_balance:.2f}")

    remaining_to_deduct = target_deduction
    usage_records = [] 

    for voucher in vouchers:
        if remaining_to_deduct <= 0:
            break

        deduction = min(voucher.balance, remaining_to_deduct)
        voucher.balance -= deduction
               
        if voucher.balance <= 0:
            voucher.is_used = True
            voucher.used_date = timezone.now()
        
        voucher.save(update_fields=['balance', 'is_used', 'used_date'])
        
        usage_records.append({
            'voucher_instance': voucher,
            'amount': deduction
        })
        remaining_to_deduct -= deduction

    if remaining_to_deduct > 0:
        raise ValueError("交易校驗失敗 ｜ Voucher balance tracking drift caught during deduction execution.")
        
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
