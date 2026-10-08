# creators/utils.py
"""
Artisan-side utilities: blog sanitisation, search variants, deterministic
shuffle, and the artisan application PDF generator.

PDF machinery (font registration, escaping, fallback chain) has moved to
`core.pdf_utils`. This module only contains the domain-specific layout of
the application PDF.
"""

import hashlib
import random
import io

import opencc
from bs4 import BeautifulSoup
import nh3
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

from core.pdf_utils import (
    ensure_fonts_registered,
    safe_paragraph,
    wrap_font,
)



# ── Tags we allow in artisan-authored blog content ─────────────
ALLOWED_TAGS = {
    "p", "br", "hr",
    "h1", "h2", "h3", "h4",
    "strong", "b", "em", "i", "u", "s", "sub", "sup",
    "code", "pre",
    "a",
    "ul", "ol", "li",
    "blockquote",
    "img", "figure", "figcaption",
    "table", "thead", "tbody", "tr", "th", "td",
    "div", "span", "section",
}


# ── Attributes we allow, per tag ('*' = all tags) ─────────────
ALLOWED_ATTRS = {
    "*": {"class"},
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height"},
}

# ── Classes artisans may use (the curated escape hatch) ───────
APPROVED_CLASSES = {
    "text-center", "text-right",
    "pull-quote", "artisan-note", "artisan-highlight",
    "drop-cap", "muted", "caption",
}


def clean_blog_body(html: str) -> str:
    """
    Sanitize artisan-authored HTML for safe storage and rendering.

    Two stages:
      1. nh3 strips disallowed tags/attributes/schemes.
      2. Approved-class filter removes any class not on APPROVED_CLASSES,
         so the front-end only ever receives classes we control and ship.
    """
    if not html:
        return html

    # Stage 1 — structural + attribute sanitization
    cleaned = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        url_schemes={"http", "https", "mailto"},
        link_rel="noopener noreferrer",
    )

    # Stage 2 — class allow-list enforcement
    soup = BeautifulSoup(cleaned, "html.parser")
    for el in soup.find_all(class_=True):
        keep = [c for c in el.get("class", []) if c in APPROVED_CLASSES]
        if keep:
            el["class"] = keep
        else:
            del el["class"]

    # Stage 3 — remove dead anchors (no href), keep their text
    for a in soup.find_all("a"):
        if not a.get("href"):
            a.unwrap()

    return str(soup)


def _get_application_pdf_styles():
    """
    Local styles for the artisan application PDF.

    NOTE: base fontName is NotoSansSC-Bold / NotoSansSC-Regular, matching
    the current visual output. A follow-up commit will flip these to the
    TC family once a side-by-side comparison has been approved.
    """
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
        'AppBody', fontName='NotoSansSC-Regular', fontSize=10, leading=15,
        spaceAfter=10
    ))
    styles.add(ParagraphStyle(
        'AppSection', fontName='NotoSansSC-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#686461'),
        spaceBefore=10, spaceAfter=6, alignment=TA_LEFT
    ))
    return styles


def generate_application_pdf(app_data):
    ensure_fonts_registered()

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
    # Mixed-font literal: DejaVu for the Latin transliteration, Sanskrit
    # for the Devanagari, TC for the Chinese. All constant strings.
    header_html = (
        wrap_font("Hṛdayadīpa", "DejaVuSans", 14)
        + " "
        + wrap_font("(हृदयदीप)", "SanskritFont", 14)
        + "｜心燈"
    )
    elements.append(Paragraph(header_html, styles['AppHeader']))
    elements.append(Spacer(1, 2 * mm))

    elements.append(Paragraph("匠人申請書 | Artisan Application", styles['AppTitle']))
    elements.append(Spacer(1, 1 * mm))
    elements.append(safe_paragraph(
        f"提交時間：{app_data.get('submitted_at', '—')}",
        styles['AppLabel'],
        fallback="—",
        apply_fallback=False,
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(
        width="100%", thickness=0.5, color=colors.HexColor("#cccccc")
    ))
    elements.append(Spacer(1, 6 * mm))

    # ── Helper: build a two-column info row ────
    def info_row(label, value):
        return [
            Paragraph(label, styles['AppLabel']),
            safe_paragraph(value, styles['AppBody'], fallback="—"),
        ]

    # ── Identity ────────────────────────────────
    identity_data = [
        info_row("公開展示名稱 | Display Name", app_data.get('display_name')),
        info_row("真實姓名 | Full Name",        app_data.get('full_name')),
        info_row("電郵 | Email",                app_data.get('email')),
        info_row("電話 | Phone",                app_data.get('phone')),
        info_row("微信 | WeChat",               app_data.get('wechat')),
    ]
    identity_table = Table(identity_data, colWidths=[50 * mm, 120 * mm])
    identity_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.HexColor('#eeeeee')),
    ]))
    elements.append(Paragraph(
        "聯絡與身份 | Contact & Identity", styles['AppSection']
    ))
    elements.append(identity_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Location ────────────────────────────────
    location_data = [
        info_row("省份 | Province", app_data.get('province')),
        info_row("城市 | City",     app_data.get('city')),
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
    elements.append(Paragraph(
        "工藝類型 | Craft Discipline(s)", styles['AppSection']
    ))
    elements.append(safe_paragraph(craft_str, styles['AppBody'], fallback="—"))
    elements.append(Spacer(1, 6 * mm))

    # ── Portfolio ───────────────────────────────
    if app_data.get('portfolio_url'):
        elements.append(Paragraph(
            "作品集 | Portfolio URL", styles['AppSection']
        ))
        elements.append(safe_paragraph(
            app_data['portfolio_url'], styles['AppBody'], fallback="—"
        ))
        elements.append(Spacer(1, 6 * mm))

    # ── Bio ─────────────────────────────────────
    elements.append(Paragraph("自我簡介 | Short Bio", styles['AppSection']))
    elements.append(safe_paragraph(
        app_data.get('short_bio', '—'), styles['AppBody'], fallback="—"
    ))
    elements.append(Spacer(1, 6 * mm))

    # ── Reason ──────────────────────────────────
    elements.append(Paragraph(
        "加入原因 | Reason for Joining", styles['AppSection']
    ))
    elements.append(safe_paragraph(
        app_data.get('reason_for_joining', '—'), styles['AppBody'], fallback="—"
    ))

    # ── Footer ──────────────────────────────────
    elements.append(Spacer(1, 12 * mm))
    elements.append(HRFlowable(
        width="100%", thickness=0.5, color=colors.HexColor("#cccccc")
    ))
    elements.append(Spacer(1, 3 * mm))
    footer_html = (
        "此申請經由 "
        + wrap_font("Hṛdayadīpa", "DejaVuSans")
        + "｜心燈 匠人計劃生成。"
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
