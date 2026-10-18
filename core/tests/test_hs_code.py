# core/tests/test_hs_code.py
"""
HS Code in ArtisanProductForm.

Background
----------
Product.hs_code exists on the model and is exposed in the admin under
"Tax & Customs｜稅務", but ArtisanProductForm.Meta.fields never
included it, so an artisan could not enter an HS code at all — only a
superadmin via /admin/. The 物流方案討論稿 §6.2 states that the
artisan should supply it at product publish time, or the platform
should classify it; the first half of that was impossible before this
commit.

Tests cover:
  * The form accepts a blank hs_code.
  * The form accepts a well-formed hs_code (9701, 9701.10, etc.).
  * The form rejects malformed hs_code values.
  * The value persists to Product.hs_code on save.
  * The artisan product-edit page renders the widget.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.fixture
def artisan_with_draft(db, django_user_model):
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product

    user = django_user_model.objects.create_user(
        username="hs_artisan",
        email="hs@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="HS Artisan",
        slug="hs-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="HS Physical",
        slug="hs-physical",
        product_format="physical",
    )
    product = Product.objects.create(
        product_name="HS Widget",
        slug="hs-widget",
        category=category,
        creator=profile,
        is_digital=False,
        is_physical=True,
        is_active=True,
        status="Draft",
    )
    return {"user": user, "profile": profile, "category": category, "product": product}


# ──────────────────────────────────────────────────────────────────
# Form-level
# ──────────────────────────────────────────────────────────────────

def _build_form(artisan, *, hs_code=None):
    from store.forms import ArtisanProductForm

    data = {
        "product_name": "Form Test Widget",
        "description": "x",
        "category": artisan["category"].id,
        "product_kind": "physical",
        "digital_fulfillment_type": "INSTANT",
    }
    if hs_code is not None:
        data["hs_code"] = hs_code
    return ArtisanProductForm(data, artisan=artisan["profile"])


class TestHsCodeFormValidation:

    def test_blank_hs_code_is_valid(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["hs_code"] == ""

    def test_missing_hs_code_is_valid(self, artisan_with_draft):
        """Omitting the field entirely should behave like a blank value."""
        form = _build_form(artisan_with_draft, hs_code=None)
        assert form.is_valid(), form.errors

    def test_chapter_only_code_is_valid(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="9701")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["hs_code"] == "9701"

    def test_heading_code_is_valid(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="9701.10")
        assert form.is_valid(), form.errors

    def test_subheading_code_is_valid(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="9701.10.00")
        assert form.is_valid(), form.errors

    def test_whitespace_is_stripped(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="  9701.10  ")
        assert form.is_valid(), form.errors
        assert form.cleaned_data["hs_code"] == "9701.10"

    @pytest.mark.parametrize("bad_value", [
        "9701a10",
        "9701/10",
        "9701 10",
        "abc",
        "-9701",
        "97.01.10.00.extra",
    ])
    def test_malformed_hs_code_is_rejected(self, artisan_with_draft, bad_value):
        form = _build_form(artisan_with_draft, hs_code=bad_value)
        assert not form.is_valid()
        assert "hs_code" in form.errors


# ──────────────────────────────────────────────────────────────────
# Persistence — form.save() writes the field
# ──────────────────────────────────────────────────────────────────

class TestHsCodePersistence:

    def test_hs_code_saved_to_product(self, artisan_with_draft):
        from store.models import Product

        form = _build_form(artisan_with_draft, hs_code="9701.10")
        assert form.is_valid(), form.errors
        product = form.save()
        product.refresh_from_db()
        assert product.hs_code == "9701.10"

    def test_blank_hs_code_saves_as_blank(self, artisan_with_draft):
        form = _build_form(artisan_with_draft, hs_code="")
        assert form.is_valid(), form.errors
        product = form.save()
        product.refresh_from_db()
        assert product.hs_code == ""


# ──────────────────────────────────────────────────────────────────
# Template — the field is actually rendered on the edit page
# ──────────────────────────────────────────────────────────────────

class TestHsCodeWidgetRendered:

    def test_edit_page_renders_hs_code_input(self, client, artisan_with_draft):
        """
        Template-level guard: the artisan edit page must render the
        hs_code widget. A view-side fix that adds the field to the
        form but forgets the template would otherwise pass the form
        tests above while remaining invisible to the artisan.
        """
        chain = artisan_with_draft
        client.force_login(chain["user"])
        url = reverse("a_dashboard_product_edit", kwargs={"pk": chain["product"].pk})
        response = client.get(url)
        assert response.status_code == 200

        body = response.content.decode()
        assert 'name="hs_code"' in body, (
            "hs_code input not rendered on the product edit page. "
            "Add {{ form.hs_code }} to _product_editor_panel.html."
        )