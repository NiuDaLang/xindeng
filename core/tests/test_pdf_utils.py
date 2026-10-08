# core/tests/test_pdf_utils.py
"""Tests for core.pdf_utils. No ReportLab rendering — every assertion is
against pure-Python output (strings, Decimals, resolved paths)."""

from decimal import Decimal

import pytest
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, Paragraph

from core import pdf_utils


@pytest.fixture(scope="module")
def style():
    return ParagraphStyle("test", fontName="Helvetica", fontSize=10)


@pytest.fixture(scope="session", autouse=True)
def _ensure_fonts_registered():
    """Register fonts once for the whole test session so apply_font_fallback
    and safe_paragraph can find the TTF faces."""
    pdf_utils.ensure_fonts_registered()


@pytest.fixture(scope="session", autouse=True)
def _ensure_fonts():
    pdf_utils.ensure_fonts_registered()
    

# ─────────────────────────────────────────────────────────────────
# escape_for_pdf
# ─────────────────────────────────────────────────────────────────

class TestEscapeForPdf:
    def test_none_returns_empty(self):
        assert pdf_utils.escape_for_pdf(None) == ""

    def test_empty_string(self):
        assert pdf_utils.escape_for_pdf("") == ""

    def test_plain_text_unchanged(self):
        assert pdf_utils.escape_for_pdf("hello") == "hello"

    def test_lt_escaped(self):
        assert pdf_utils.escape_for_pdf("a<b") == "a&lt;b"

    def test_gt_escaped(self):
        assert pdf_utils.escape_for_pdf("a>b") == "a&gt;b"

    def test_ampersand_escaped(self):
        assert pdf_utils.escape_for_pdf("a&b") == "a&amp;b"

    def test_all_three_in_one(self):
        assert pdf_utils.escape_for_pdf("<a & b>") == "&lt;a &amp; b&gt;"

    def test_non_string_coerced(self):
        assert pdf_utils.escape_for_pdf(123) == "123"

    def test_does_not_escape_quotes(self):
        # xml.sax.saxutils.escape only handles <, >, & by default.
        assert pdf_utils.escape_for_pdf('say "hi"') == 'say "hi"'


# ─────────────────────────────────────────────────────────────────
# safe_decimal
# ─────────────────────────────────────────────────────────────────

class TestSafeDecimal:
    def test_none_returns_default(self):
        assert pdf_utils.safe_decimal(None) == Decimal("0")

    def test_empty_string_returns_default(self):
        assert pdf_utils.safe_decimal("") == Decimal("0")

    def test_decimal_passthrough(self):
        assert pdf_utils.safe_decimal(Decimal("10.50")) == Decimal("10.50")

    def test_int(self):
        assert pdf_utils.safe_decimal(42) == Decimal("42")

    def test_float_via_str(self):
        assert pdf_utils.safe_decimal(1.5) == Decimal("1.5")

    def test_string_with_commas(self):
        assert pdf_utils.safe_decimal("1,234.56") == Decimal("1234.56")

    def test_unparseable_returns_default(self):
        assert pdf_utils.safe_decimal("N/A") == Decimal("0")

    def test_custom_default(self):
        assert pdf_utils.safe_decimal(None, default=Decimal("9.99")) == Decimal("9.99")

    def test_negative(self):
        assert pdf_utils.safe_decimal("-10.00") == Decimal("-10.00")


# ─────────────────────────────────────────────────────────────────
# format_currency
# ─────────────────────────────────────────────────────────────────

class TestFormatCurrency:
    def test_positive_two_digit(self):
        assert pdf_utils.format_currency("100", "¥") == "¥ 100.00"

    def test_positive_with_thousands(self):
        assert pdf_utils.format_currency("1234567.89", "¥") == "¥ 1,234,567.89"

    def test_negative_wrapped_in_parens(self):
        assert pdf_utils.format_currency("-100", "¥") == "¥ (100.00)"

    def test_negative_with_thousands(self):
        assert pdf_utils.format_currency("-1234.56", "¥") == "¥ (1,234.56)"

    def test_zero(self):
        assert pdf_utils.format_currency(0, "¥") == "¥ 0.00"

    def test_none_becomes_zero(self):
        assert pdf_utils.format_currency(None, "¥") == "¥ 0.00"

    def test_integer_currency_no_decimals(self):
        assert pdf_utils.format_currency("1000", "¥", is_integer=True) == "¥ 1,000"

    def test_integer_currency_rounds(self):
        assert pdf_utils.format_currency("999.5", "¥", is_integer=True) == "¥ 1,000"

    def test_integer_currency_negative(self):
        assert pdf_utils.format_currency("-500", "¥", is_integer=True) == "¥ (500)"

    def test_foreign_symbol(self):
        assert pdf_utils.format_currency("100", "HK$") == "HK$ 100.00"


# ─────────────────────────────────────────────────────────────────
# resolve_static_font
# ─────────────────────────────────────────────────────────────────

class TestResolveStaticFont:
    def test_known_font_resolves(self, settings):
        path = pdf_utils.resolve_static_font("NotoSansTC-Regular.ttf")
        assert path is not None
        assert path.endswith("NotoSansTC-Regular.ttf")

    def test_unknown_font_returns_none(self):
        assert pdf_utils.resolve_static_font("does-not-exist.ttf") is None

    def test_path_is_absolute(self):
        path = pdf_utils.resolve_static_font("NotoSansTC-Regular.ttf")
        assert path is not None
        assert path.startswith("/") or ":" in path  # unix or windows


# ─────────────────────────────────────────────────────────────────
# register_font_safely
# ─────────────────────────────────────────────────────────────────

class TestRegisterFontSafely:
    def test_missing_file_returns_false(self):
        assert pdf_utils.register_font_safely("TestMissing", "nope.ttf") is False

    def test_registers_known_font(self):
        ok = pdf_utils.register_font_safely(
            "TestTC", "NotoSansTC-Regular.ttf"
        )
        assert ok is True


# ─────────────────────────────────────────────────────────────────
# apply_font_fallback
# ─────────────────────────────────────────────────────────────────

class TestApplyFontFallback:
    def test_empty_string(self):
        assert pdf_utils.apply_font_fallback("") == ""

    def test_none(self):
        assert pdf_utils.apply_font_fallback(None) == ""

    def test_legacy_behaviour_no_base_font(self):
        # With no base_font, everything gets wrapped as before.
        out = pdf_utils.apply_font_fallback("hello")
        assert out.count("<font") == out.count("</font>")
        assert out.count("<font") >= 1

    def test_base_font_containing_ascii_leaves_ascii_unwrapped(self):
        # NotoSansTC-Bold contains ASCII. When it is the base font,
        # ASCII content must NOT be wrapped in <font> tags.
        out = pdf_utils.apply_font_fallback(
            "hello", base_font="NotoSansTC-Bold"
        )
        assert "<font" not in out
        assert "hello" in out

    def test_base_font_leaves_chars_it_cannot_render_wrapped(self):
        # Sanskrit is not in NotoSansTC-Bold. That character must be
        # wrapped in a font that can render it.
        out = pdf_utils.apply_font_fallback(
            "Aह", base_font="NotoSansTC-Bold"
        )
        # 'A' unwrapped, 'ह' inside a <font> tag.
        assert "<font" in out
        assert out.count("<font") == 1

    def test_does_not_escape_angles(self):
        out = pdf_utils.apply_font_fallback("<")
        assert out.count("<font") == out.count("</font>")

    def test_runs_are_grouped(self):
        out = pdf_utils.apply_font_fallback("abc")
        assert out.count("<font") <= 2

    def test_chain_is_sc_first(self):
        assert pdf_utils.FONT_FALLBACK_CHAIN[0] == "NotoSansSC-Regular"
        assert pdf_utils.FONT_FALLBACK_CHAIN[1] == "NotoSansTC-Regular"

    def test_bold_base_prefers_bold_fallback(self):
        # Simplified Chinese not in TC-Bold, but in SC-Bold. When the base
        # font is bold, the fallback must also be bold, not regular.
        # Use a known Simplified character: 测 (U+6D4B)
        out = pdf_utils.apply_font_fallback("测", base_font="NotoSansTC-Bold")
        # Should be wrapped in a bold variant.
        assert 'name="NotoSansSC-Bold"' in out or 'name="NotoSansTC-Bold"' in out

    def test_regular_base_prefers_regular_fallback(self):
        # When the base font is regular, the fallback should also be regular.
        out = pdf_utils.apply_font_fallback("测", base_font="NotoSansTC-Regular")
        # Should be wrapped in a regular variant.
        assert 'name="NotoSansSC-Regular"' in out or 'name="NotoSansTC-Regular"' in out


# ─────────────────────────────────────────────────────────────────
# wrap_font
# ─────────────────────────────────────────────────────────────────

class TestWrapFont:
    def test_no_size(self):
        assert pdf_utils.wrap_font("x", "DejaVuSans") == \
            '<font name="DejaVuSans">x</font>'

    def test_with_size(self):
        assert pdf_utils.wrap_font("x", "DejaVuSans", 14) == \
            '<font name="DejaVuSans" size="14">x</font>'

    def test_empty_text(self):
        assert pdf_utils.wrap_font("", "SanskritFont") == \
            '<font name="SanskritFont"></font>'

    def test_unicode_text(self):
        out = pdf_utils.wrap_font("हृदयदीप", "SanskritFont", 14)
        assert "हृदयदीप" in out
        assert '<font name="SanskritFont" size="14">' in out


# ─────────────────────────────────────────────────────────────────
# inspect Paragraph.text
# ─────────────────────────────────────────────────────────────────

class TestSafeParagraph:
    def test_none_renders_fallback(self, style):
        p = pdf_utils.safe_paragraph(None, style)
        # Paragraph stores text in .text; the fallback is what should be there.
        assert "&nbsp;" in p.text

    def test_empty_renders_fallback(self, style):
        p = pdf_utils.safe_paragraph("", style, fallback="—")
        assert "—" in p.text

    def test_lt_escaped(self, style):
        p = pdf_utils.safe_paragraph("a<b", style, apply_fallback=False)
        assert "&lt;" in p.text
        assert "<b>" not in p.text  # the literal <b> tag must not survive

    def test_bold_wraps_escaped_content(self, style):
        p = pdf_utils.safe_paragraph("Hello", style, bold=True, apply_fallback=False)
        assert "<b>Hello</b>" in p.text

    def test_bold_wraps_after_escaping(self, style):
        # A `<` in the value must be escaped, but the enclosing <b> must survive.
        p = pdf_utils.safe_paragraph("a<b", style, bold=True, apply_fallback=False)
        assert p.text.startswith("<b>")
        assert p.text.endswith("</b>")
        assert "&lt;" in p.text

    def test_bold_after_font_fallback(self, style):
        # The <b> wrapper must be outside the <font> tags, not inside.
        p = pdf_utils.safe_paragraph("Hello", style, bold=True)
        # Both should appear, <b> first.
        assert p.text.startswith("<b>")

    def test_newlines_become_br(self, style):
        p = pdf_utils.safe_paragraph("line1\nline2", style, apply_fallback=False)
        assert "<br/>" in p.text

    def test_bold_style_is_not_overridden_by_fallback(self, style):
        # The paragraph style "test" uses Helvetica, which has no CJK.
        # A CJK character must be wrapped in a fallback; an ASCII char must not.
        # The key check: the ASCII run must not be wrapped in a *regular* face,
        # because that would override whatever bold the style supplies.
        bold_style = ParagraphStyle(
            "testbold", fontName="NotoSansTC-Bold", fontSize=10
        )
        p = pdf_utils.safe_paragraph("hello", bold_style)
        # No <font> wrapping for ASCII when the base font supports it.
        assert "<font" not in p.text

