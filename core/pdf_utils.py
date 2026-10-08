# core/pdf_utils.py
"""
Shared helpers for ReportLab PDF generation.

Centralises four things that were previously duplicated (and inconsistently
applied) across `orders/utils.py` and `creators/utils.py`:

1. Font registration — one place, idempotent, tolerant of missing files.
2. Font fallback — per-character wrapping so mixed CJK/Latin/Sanskrit text
   renders correctly regardless of the Paragraph's default font.
3. XML escaping — user-supplied strings never reach ReportLab's mini-parser
   unescaped.
4. File / Decimal / currency helpers — so the PDF paths never crash on a
   missing image, a None value, or a stray comma.

Order of operations is load-bearing: escape FIRST, then apply font fallback.
`apply_font_fallback` emits `<font name="...">` tags that ReportLab
interprets as markup; if escape runs after, those tags get escaped to
`&lt;font...&gt;` and font switching silently breaks.

NOTE on fallback chain order (SC-first):
    The current `creators/utils.py` chain puts NotoSansSC-Regular first.
    This module preserves that ordering so the creators-side migration is
    a true refactor — no visible change to application PDFs. A separate
    commit will flip the chain to TC-first alongside the stylesheet change,
    once a side-by-side comparison has been made.
"""

from __future__ import annotations

import logging
import os
from decimal import Decimal, InvalidOperation
from typing import Optional
from xml.sax.saxutils import escape as _xml_escape

from django.conf import settings
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph
from reportlab.lib import fonts as rl_fonts

from core.image_utils import robust_exists

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# Font registry — single source of truth
# ─────────────────────────────────────────────────────────────────

# (registered_name, filename).
#
# Naming convention:
#   - "NotoSansTC-Regular" / "NotoSansTC-Bold" — capital suffix, matches
#     the source filename for traceability.
#   - "DejaVuSans" (bare) for the normal face; "DejaVuSans-Bold" for bold.
#     The bare name is what existing <font name="DejaVuSans"> literals
#     already reference, and the family registration resolves bold via
#     the same lookup.
FONT_REGISTRY: list[tuple[str, str]] = [
    ("NotoSansTC-Regular", "NotoSansTC-Regular.ttf"),
    ("NotoSansSC-Regular", "NotoSansSC-Regular.ttf"),
    ("NotoSansTC-Bold",    "NotoSansTC-Bold.ttf"),
    ("NotoSansSC-Bold",    "NotoSansSC-Bold.ttf"),
    ("DejaVuSans",         "DejaVuSans-Regular.ttf"),
    ("DejaVuSans-Bold",    "DejaVuSans-Bold.ttf"),
    ("SanskritFont",       "TiroDevanagariSanskrit-Regular.ttf"),
    ("Barcode128",         "LibreBarcode128-Regular.ttf"),
]

# The subset used by apply_font_fallback, in preference order.
#
# SC-first preserves the current creators/utils.py behaviour. A follow-up
# commit will flip to TC-first. Bold faces are deliberately excluded: bold
# is selected via the Paragraph style's fontName, and running each char
# through a bold face here would double-wrap runs in edge cases.
FONT_FALLBACK_CHAIN: list[str] = [
    "NotoSansSC-Regular",
    "NotoSansTC-Regular",
    "DejaVuSans",
    "SanskritFont",
]

# Family registrations so <font name="DejaVuSans"> resolves to the right
# weight. Each tuple: (family_name, normal, bold, italic, bold_italic).
_FONT_FAMILIES: list[tuple[str, str, str, str, str]] = [
    ("NotoSansTC", "NotoSansTC-Regular", "NotoSansTC-Bold",
                    "NotoSansTC-Regular", "NotoSansTC-Bold"),
    ("NotoSansSC", "NotoSansSC-Regular", "NotoSansSC-Bold",
                    "NotoSansSC-Regular", "NotoSansSC-Bold"),
    ("DejaVuSans", "DejaVuSans", "DejaVuSans-Bold",
                    "DejaVuSans", "DejaVuSans-Bold"),
    ("SanskritFont", "SanskritFont", "SanskritFont",
                      "SanskritFont", "SanskritFont"),
]


def _font_dir() -> str:
    """Source-dir location of static fonts. Works in dev and prod because
    `static/` is git-tracked and shipped alongside the code."""
    return os.path.join(str(settings.BASE_DIR), "static", "fonts")


def resolve_static_font(filename: str) -> Optional[str]:
    """Return the absolute path to a font file, or None if missing.
    Uses robust_exists() to handle macOS NFD vs Linux NFC filename drift."""
    path = os.path.join(_font_dir(), filename)
    return path if robust_exists(path) else None


def register_font_safely(name: str, filename: str) -> bool:
    """Register a single TTF under `name`. Returns True on success
    (including the already-registered case), False if the file is
    missing or registration raised."""
    path = resolve_static_font(filename)
    if not path:
        logger.warning("pdf_utils: font file missing, skipping: %s", filename)
        return False
    try:
        pdfmetrics.registerFont(TTFont(name, path))
        return True
    except Exception as exc:
        # Common case: already registered. TTFont also raises on corrupt files.
        logger.debug("pdf_utils: registerFont(%s) skipped: %s", name, exc)
        return False


def _register_ps2tt_aliases() -> None:
    """
    Populate ReportLab's ps2tt map with our custom TTF names.

    ReportLab's ps2tt(name) decomposes a PostScript font name into
    (family, bold, italic). Its lookup table is populated only for the
    standard Type1 fonts by default. Custom TTF fonts — even after
    registerFontFamily() — are absent, and Paragraph(text, style) raises
    'Can't map determine family/bold/italic for <name>' when the style's
    fontName is a custom font.

    We add a lowercase entry per registered font:
      - "Foo-Bold"     → ("Foo", 1, 0)
      - "Foo-Regular"  → ("Foo", 0, 0)
      - "Foo" (bare)   → ("Foo", 0, 0)

    setdefault() is used so we never override ReportLab's own entries.
    """
    for name, _ in FONT_REGISTRY:
        key = name.lower()
        if name.endswith("-Bold"):
            rl_fonts._ps2tt_map.setdefault(key, (name[:-5], 1, 0))
        elif name.endswith("-Regular"):
            rl_fonts._ps2tt_map.setdefault(key, (name[:-8], 0, 0))
        else:
            rl_fonts._ps2tt_map.setdefault(key, (name, 0, 0))

    # Also register the family names themselves. This lets a style using
    # fontName="NotoSansTC" resolve, and lets the family-based <b> tag
    # find the bold face for a paragraph.
    for family in ("NotoSansTC", "NotoSansSC", "DejaVuSans", "SanskritFont"):
        rl_fonts._ps2tt_map.setdefault(family.lower(), (family, 0, 0))


# Module-level registration flag so we only do the work once per process.
_FONTS_REGISTERED = False


def ensure_fonts_registered() -> None:
    """Idempotent. Safe to call on every PDF generation."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    for name, filename in FONT_REGISTRY:
        register_font_safely(name, filename)

    registered_names = set(pdfmetrics.getRegisteredFontNames())
    for family, normal, bold, italic, bold_italic in _FONT_FAMILIES:
        if normal not in registered_names:
            continue
        try:
            pdfmetrics.registerFontFamily(
                family,
                normal=normal,
                bold=bold if bold in registered_names else normal,
                italic=italic if italic in registered_names else normal,
                boldItalic=bold_italic if bold_italic in registered_names else normal,
            )
        except Exception as exc:
            logger.debug("pdf_utils: registerFontFamily(%s) skipped: %s", family, exc)

    _register_ps2tt_aliases()

    # Invalidate the char-widths cache — if any code path ran before
    # registration completed (import-time side effects, tests, shell),
    # the cache may hold stale empty sets.
    _CHAR_WIDTHS_CACHE.clear()

    _FONTS_REGISTERED = True


# ─────────────────────────────────────────────────────────────────
# Font fallback — per-character <font> wrapping
# ─────────────────────────────────────────────────────────────────

# Cache of name -> set(codepoints). Populated on first use; fonts are
# process-global, so no invalidation is needed.
_CHAR_WIDTHS_CACHE: dict[str, set[int]] = {}


def _char_codes_for(name: str) -> set[int]:
    cached = _CHAR_WIDTHS_CACHE.get(name)
    if cached is not None:
        return cached
    try:
        font = pdfmetrics.getFont(name)
        codes = set(font.face.charWidths.keys())
    except Exception:
        # Font not registered yet — do NOT cache the empty set, or the
        # process will be stuck with it. The next call, after
        # ensure_fonts_registered(), will try again.
        return set()
    _CHAR_WIDTHS_CACHE[name] = codes
    return codes

def apply_font_fallback(text: str, base_font: Optional[str] = None) -> str:
    """
    Wrap runs of characters in <font name="..."> tags so mixed CJK / Latin /
    Sanskrit strings render with the correct face regardless of the
    Paragraph style's default font.

    Characters that the `base_font` can render are left unwrapped — this
    preserves the paragraph style's weight (e.g. bold), because an inline
    <font> override would otherwise replace the style's bold face with the
    fallback's regular face.

    If `base_font` is None, every character is checked against the fallback
    chain (legacy behaviour).

    IMPORTANT: input must already be XML-escaped. Use `safe_paragraph()`
    which enforces the correct order.
    """
    if not text:
        return ""

    if base_font:
        base_codes = _char_codes_for(base_font)
        # Match the base font's weight when selecting fallbacks.
        # If the base is bold, prefer bold faces; if regular, prefer regular.
        is_bold = base_font.endswith("-Bold")
    else:
        base_codes = set()
        is_bold = False

    if is_bold:
        # Bold variants first, then regular variants as a last resort.
        effective_chain = [
            "NotoSansTC-Bold",
            "NotoSansSC-Bold",
            "DejaVuSans-Bold",
            "NotoSansTC-Regular",
            "NotoSansSC-Regular",
            "DejaVuSans",
            "SanskritFont",
        ]
    else:
        effective_chain = list(FONT_FALLBACK_CHAIN)

    font_codes = {name: _char_codes_for(name) for name in effective_chain}

    def font_for(ch: str) -> Optional[str]:
        code = ord(ch)
        if code in base_codes:
            return None
        for name in effective_chain:
            if code in font_codes[name]:
                return name
        return None

    output: list[str] = []
    current: Optional[str] = None
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        chunk = "".join(buffer)
        if current is None:
            output.append(chunk)
        else:
            output.append(f'<font name="{current}">{chunk}</font>')
        buffer.clear()

    for ch in text:
        chosen = font_for(ch)
        if chosen != current:
            flush()
            current = chosen
        buffer.append(ch)

    flush()
    return "".join(output)


def wrap_font(text: str, name: str, size: Optional[int] = None) -> str:
    """
    Wrap a literal string in a single <font> tag. Used for header/footer
    fragments that mix faces deliberately (e.g. the site name rendering in
    DejaVu + Sanskrit + Traditional Chinese).

    `text` is expected to already be literal markup, not user input. This
    helper is for constant strings in the PDF templates.
    """
    if size is None:
        return f'<font name="{name}">{text}</font>'
    return f'<font name="{name}" size="{size}">{text}</font>'


# ─────────────────────────────────────────────────────────────────
# Safe value builders
# ─────────────────────────────────────────────────────────────────

def escape_for_pdf(value) -> str:
    """XML-escape any user-supplied value. None becomes ''.
    The caller is responsible for supplying the display fallback
    (typically '&nbsp;') when the escaped result is empty."""
    if value is None:
        return ""
    return _xml_escape(str(value))


def safe_paragraph(value, style: ParagraphStyle, *, fallback: str = "&nbsp;",
                   bold: bool = False, apply_fallback: bool = True) -> Paragraph:
    """
    Build a Paragraph from a possibly user-supplied value.

    - `None` and empty strings render as `fallback`.
    - The value is XML-escaped, then (optionally) run through
      `apply_font_fallback` to select the correct CJK/Latin/Sanskrit face.
    - Multi-line strings are converted to `<br/>`.
    - `bold=True` wraps the whole run in `<b>...</b>`, resolved via the
      registered font family (so the bold face is picked correctly even
      when the value contains mixed scripts).
    """
    escaped = escape_for_pdf(value)
    if not escaped:
        return Paragraph(fallback, style)
    if apply_fallback:
        escaped = apply_font_fallback(escaped, base_font=style.fontName)
    escaped = escaped.replace("\n", "<br/>")
    if bold:
        escaped = f"<b>{escaped}</b>"
    return Paragraph(escaped, style)


def safe_image(path: Optional[str], width, height) -> Optional[Image]:
    """Return an Image flowable if the file exists, else None.
    Handles macOS NFD vs Linux NFC paths via robust_exists()."""
    if not path:
        return None
    if not robust_exists(path):
        logger.warning("pdf_utils: image file missing, skipping: %s", path)
        return None
    try:
        return Image(path, width=width, height=height)
    except Exception as exc:
        logger.warning("pdf_utils: Image(%s) failed: %s", path, exc)
        return None


def safe_decimal(value, default: Decimal = Decimal("0")) -> Decimal:
    """Parse any numeric-ish value into Decimal. Commas stripped.
    None, '', 'N/A', or anything unparseable → default.
    Never raises InvalidOperation to the caller."""
    if value is None or value == "":
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError, TypeError):
        return default


def format_currency(value, symbol: str, is_integer: bool = False) -> str:
    """
    Format a currency amount with thousands separators. Negative values
    are wrapped in parentheses (accounting convention):

        100.00   -> '¥ 100.00'
        -100.00  -> '¥ (100.00)'
        None     -> '¥ 0.00'

    Integer currencies (JPY, KRW, etc.) drop the decimal part.
    """
    d = safe_decimal(value)
    negative = d < 0
    abs_d = abs(d)
    if is_integer:
        number = f"{abs_d:,.0f}"
    else:
        number = f"{abs_d:,.2f}"
    if negative:
        return f"{symbol} ({number})"
    return f"{symbol} {number}"

