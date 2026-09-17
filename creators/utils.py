# creators/utils.py
import opencc
import hashlib
import random
from django.utils import timezone
import io
from decimal import Decimal

# reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from orders.utils import get_pdf_styles, register_multilingual_fonts

import os
from django.conf import settings
from xml.sax.saxutils import escape


# Font registry — maps ReportLab font name → file path
# Adjust paths to match your static/fonts directory
FONT_FALLBACK_CHAIN = [
    ('NotoSansSC-Regular', 'NotoSansSC-Regular.ttf'),
    ('NotoSansSC-Bold',    'NotoSansSC-Bold.ttf'),
    ('DejaVuSans',         'DejaVuSans-Regular.ttf'),
    ('DejaVuSans-Bold',    'DejaVuSans-Bold.ttf'),
    ('SanskritFont',       'TiroDevanagariSanskrit-Regular.ttf'),
]

def _register_fallback_fonts():
    """Register all fonts in the fallback chain (idempotent)."""
    font_dir = os.path.join(settings.BASE_DIR, 'static/fonts')

    registered = set()

    for name, filename in FONT_FALLBACK_CHAIN:
        path = os.path.join(font_dir, filename)
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                registered.add(name)
            except Exception:
                # Already registered — harmless
                pass

    # Register font families so <font name="..."> resolves correctly
    # Each family maps: regular, bold, italic, boldItalic
    # If a variant doesn't exist, reuse the regular (harmless fallback)
    families = [
        ('NotoSansSC', 'NotoSansSC-Regular', 'NotoSansSC-Bold', 'NotoSansSC-Regular', 'NotoSansSC-Bold'),
        ('DejaVuSans', 'DejaVuSans', 'DejaVuSans-Bold', 'DejaVuSans', 'DejaVuSans-Bold'),
        ('SanskritFont', 'SanskritFont', 'SanskritFont', 'SanskritFont', 'SanskritFont'),
    ]

    for family_name, regular, bold, italic, bold_italic in families:
        try:
            pdfmetrics.registerFontFamily(
                family_name,
                normal=regular,
                bold=bold,
                italic=italic,
                boldItalic=bold_italic,
            )
        except Exception:
            pass  # Already registered or font not present


def apply_font_fallback(text, primary_font='NotoSansSC-Regular'):
    """
    Wrap runs of characters in explicit <font> tags so they render with the
    correct font regardless of the Paragraph's default style font.
    Groups consecutive characters sharing the same font into a single tag.
    """
    if not text:
        return ''

    # Build font → supported char codes (once per call)
    font_codes = {}
    for name, _ in FONT_FALLBACK_CHAIN:
        try:
            font = pdfmetrics.getFont(name)
            font_codes[name] = set(font.face.charWidths.keys())
        except Exception:
            continue

    def _font_for(ch):
        code = ord(ch)
        for name, _ in FONT_FALLBACK_CHAIN:
            if name in font_codes and code in font_codes[name]:
                return name
        return None

    output = []
    current_font = None
    current_buffer = []

    for char in text:
        chosen = _font_for(char)

        if chosen != current_font:
            # Flush previous chunk
            if current_buffer:
                chunk = ''.join(current_buffer)
                if current_font is None:
                    output.append(chunk)
                else:
                    output.append(f'<font name="{current_font}">{chunk}</font>')
                current_buffer = []

            current_font = chosen

        current_buffer.append(char)

    # Flush last chunk
    if current_buffer:
        chunk = ''.join(current_buffer)
        if current_font is None:
            output.append(chunk)
        else:
            output.append(f'<font name="{current_font}">{chunk}</font>')

    return ''.join(output)


def _get_application_pdf_styles():
    """Local styles for the artisan application PDF, using SC fonts."""
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_LEFT

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'AppHeader', fontName='NotoSansSC-Bold', fontSize=15, leading=20,
        textColor=colors.HexColor('#1f1f1f')
    ))
    styles.add(ParagraphStyle(
        'AppTitle', fontName='NotoSansSC-Bold', fontSize=20, leading=26,
        textColor=colors.HexColor('#1f1f1f')
    ))
    styles.add(ParagraphStyle(
        'AppLabel', fontName='NotoSansSC-Regular', fontSize=8,
        textColor=colors.HexColor('#666666'), spaceAfter=1
    ))
    styles.add(ParagraphStyle(
        'AppBody', fontName='NotoSansSC-Regular', fontSize=10, leading=15, spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'AppSection', fontName='NotoSansSC-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#686461'),
        spaceBefore=10, spaceAfter=6, alignment=TA_LEFT
    ))
    return styles


def generate_application_pdf(app_data):
    register_multilingual_fonts()
    _register_fallback_fonts()

    buffer = io.BytesIO()
    styles = _get_application_pdf_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=f"Artisan Application - {app_data['display_name']}",
        author="Hṛdayadīpa｜心燈",
        topMargin=15 * mm, bottomMargin=15 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    elements = []

    # ── Header ─────────────────────────────────
    header_html = (
        "<font name='DejaVuSans' size='14'>Hṛdayadīpa</font> "
        "<font name='SanskritFont' size='14'>(हृदयदीप)</font>｜心燈"
    )
    elements.append(Paragraph(header_html, styles['AppHeader']))
    elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph("匠人申請書 | Artisan Application", styles['AppTitle']))
    elements.append(Spacer(1, 1 * mm))
    elements.append(Paragraph(
        f"提交時間：{app_data.get('submitted_at', '—')}",
        styles['AppLabel']
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 6 * mm))

    # ── Helper: escapes AND applies font fallback ─
    def info_row(label, value):
        """Build a table row with the value safely escaped and font-tagged."""
        if value:
            styled = apply_font_fallback(escape(str(value)))
        else:
            styled = '—'
        return [
            Paragraph(label, styles['AppLabel']),
            Paragraph(styled, styles['AppBody']),
        ]

    # ── Identity ────────────────────────────────
    identity_data = [
        info_row("公開展示名稱 | Display Name", app_data.get('display_name')),
        info_row("真實姓名 | Full Name", app_data.get('full_name')),
        info_row("電郵 | Email", app_data.get('email')),
        info_row("電話 | Phone", app_data.get('phone')),
        info_row("微信 | WeChat", app_data.get('wechat')),
    ]
    identity_table = Table(identity_data, colWidths=[50 * mm, 120 * mm])
    identity_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.HexColor('#eeeeee')),
    ]))
    elements.append(Paragraph("聯絡與身份 | Contact & Identity", styles['AppSection']))
    elements.append(identity_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Location ────────────────────────────────
    location_data = [
        info_row("省份 | Province", app_data.get('province')),
        info_row("城市 | City", app_data.get('city')),
    ]
    location_table = Table(location_data, colWidths=[50 * mm, 120 * mm])
    location_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(Paragraph("所在地 | Location", styles['AppSection']))
    elements.append(location_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Craft ───────────────────────────────────
    craft_str = "、".join(app_data.get('craft_types', [])) or "—"
    elements.append(Paragraph("工藝類型 | Craft Discipline(s)", styles['AppSection']))
    elements.append(Paragraph(
        apply_font_fallback(escape(craft_str)),
        styles['AppBody']
    ))
    elements.append(Spacer(1, 6 * mm))

    # ── Portfolio ───────────────────────────────
    if app_data.get('portfolio_url'):
        safe_url = apply_font_fallback(escape(app_data['portfolio_url']))
        elements.append(Paragraph("作品集 | Portfolio URL", styles['AppSection']))
        elements.append(Paragraph(safe_url, styles['AppBody']))
        elements.append(Spacer(1, 6 * mm))

    # ── Bio ─────────────────────────────────────
    safe_bio = apply_font_fallback(escape(app_data.get('short_bio', '—'))).replace('\n', '<br/>')
    elements.append(Paragraph("自我簡介 | Short Bio", styles['AppSection']))
    elements.append(Paragraph(safe_bio, styles['AppBody']))
    elements.append(Spacer(1, 6 * mm))

    # ── Reason ──────────────────────────────────
    safe_reason = apply_font_fallback(escape(app_data.get('reason_for_joining', '—'))).replace('\n', '<br/>')
    elements.append(Paragraph("加入原因 | Reason for Joining", styles['AppSection']))
    elements.append(Paragraph(safe_reason, styles['AppBody']))

    # ── Footer ──────────────────────────────────
    elements.append(Spacer(1, 12 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc")))
    elements.append(Spacer(1, 3 * mm))
    footer_html = (
        "此申請經由 "
        "<font name='DejaVuSans'>Hṛdayadīpa</font>"
        "｜心燈 匠人計劃生成。"
    )
    elements.append(Paragraph(footer_html, styles['AppLabel']))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def get_search_variants(keyword):
    """
    Returns a list of equivalent search strings:
    - the original
    - simplified-to-traditional conversion
    - traditional-to-simplified conversion
    Deduplicated and stripped.
    """
    if not keyword:
        return []

    s2t = opencc.OpenCC('s2t.json')  # Simplified → Traditional
    t2s = opencc.OpenCC('t2s.json')  # Traditional → Simplified

    variants = {keyword.strip()}
    try:
        variants.add(s2t.convert(keyword))
    except Exception:
        pass
    try:
        variants.add(t2s.convert(keyword))
    except Exception:
        pass

    return [v for v in variants if v]


def stable_shuffle_queryset(queryset, seed_extra=''):
    """
    Returns a list of model instances from the queryset, deterministically
    shuffled for the current day.

    - Same input + same day → same order across every page load.
    - New day → new order.

    Use this for gallery shuffling that should rotate daily but stay
    consistent throughout a single day (so pagination, refreshes, and
    shares all see the same layout).
    """
    today = timezone.now().strftime('%Y%m%d')
    seed_str = f"{today}:{seed_extra}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)

    items = list(queryset)
    rnd = random.Random(seed)
    rnd.shuffle(items)
    return items
