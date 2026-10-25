# category/tests/test_vault_subfolder.py
"""
Tests for Category.vault_subfolder.

The field itself is a plain CharField. The tests below pin:

  * the default ("" = root), so a category created without an
    explicit subfolder does not accidentally route files somewhere
    unexpected;
  * the two backfilled categories (epainting, ebooks), so a future
    migration that forgets one is caught;
  * that every other category stays at the default (""), so the
    backfill stays narrow.

The routing behaviour — that review_vault_upload_approve writes
into vault_subfolder when set — is covered in the store-side test
file that ships with the routing commit. This file pins only the
model and the data migration.
"""
from __future__ import annotations

import pytest


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def make_category(db):
    from category.models import Category

    _counter = {"n": 0}

    def _make(slug: str | None = None, *, vault_subfolder: str | None = None):
        _counter["n"] += 1
        n = _counter["n"]
        kwargs = {
            "category_name": f"Test Cat {n}",
            "slug": slug if slug is not None else f"test-cat-{n}",
            "product_format": "e-product",
        }
        if vault_subfolder is not None:
            kwargs["vault_subfolder"] = vault_subfolder
        return Category.objects.create(**kwargs)

    return _make


# ──────────────────────────────────────────────────────────────────
# Field default
# ──────────────────────────────────────────────────────────────────

class TestFieldDefault:

    def test_new_category_defaults_to_empty_string(self, make_category):
        c = make_category()
        assert c.vault_subfolder == ""

    def test_explicit_subfolder_round_trips(self, make_category):
        c = make_category(vault_subfolder="edesign")
        c.refresh_from_db()
        assert c.vault_subfolder == "edesign"


# ──────────────────────────────────────────────────────────────────
# Backfilled categories — pinned so the migration cannot silently
# forget one in a future refactor
# ──────────────────────────────────────────────────────────────────

class TestBackfill:

    def test_epainting_category_maps_to_epaintings(self, db):
        from category.models import Category
        c = Category.objects.filter(slug="epainting").first()
        if c is None:
            pytest.skip(
                "epainting category not present in this test DB; "
                "the migration backfill is asserted in the source tree."
            )
        assert c.vault_subfolder == "epaintings"

    def test_ebooks_category_maps_to_ebooks(self, db):
        from category.models import Category
        c = Category.objects.filter(slug="ebooks").first()
        if c is None:
            pytest.skip(
                "ebooks category not present in this test DB; "
                "the migration backfill is asserted in the source tree."
            )
        assert c.vault_subfolder == "ebooks"

    def test_other_categories_stay_at_default(self, db):
        """
        Any category that is not 'epainting' or 'ebooks' must have
        vault_subfolder == "". This catches a backfill that widened
        beyond the two intended slugs.
        """
        from category.models import Category
        offenders = list(
            Category.objects
            .exclude(slug__in=["epainting", "ebooks"])
            .exclude(vault_subfolder="")
            .values_list("slug", "vault_subfolder")
        )
        assert offenders == [], (
            f"Categories beyond the two intended backfills have a "
            f"vault_subfolder set: {offenders}"
        )