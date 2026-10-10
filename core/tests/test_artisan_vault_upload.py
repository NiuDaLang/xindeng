# core/tests/test_artisan_vault_upload.py
"""
Model-level tests for ArtisanVaultUpload.

Covers the constraint invariants and status transitions that the rest
of the vault pipeline depends on. No view or admin wiring yet.

Located under core/tests/ to match pytest.ini's testpaths, alongside
the rest of the vault tests. Move to store/tests/ in a future session.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_chain(db, django_user_model):
    """
    Returns a callable that builds a fresh
    (artisan, product, variation) triple each call.

    A fresh product per call avoids unique-slug collisions on Category
    and Product when tests run in sequence.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    _counter = {"n": 0}

    def _make():
        _counter["n"] += 1
        n = _counter["n"]

        user = django_user_model.objects.create_user(
            username=f"artisan{n}",
            email=f"artisan{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        creator = CreatorProfile.objects.create(
            user=user,
            display_name=f"Artisan {n}",
            slug=f"artisan-{n}",
            is_verified=True,
        )

        category = Category.objects.create(
            category_name=f"Digital {n}",
            slug=f"digital-{n}",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name=f"Ebook {n}",
            category=category,
            creator=creator,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
        )
        return {"artisan": creator, "product": product, "variation": variation}

    return _make


# ──────────────────────────────────────────────────────────────────
# Defaults
# ──────────────────────────────────────────────────────────────────

class TestDefaults:

    def test_new_upload_defaults_to_pending_and_local(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="ebook.pdf",
            staged_filename="abc-123.pdf",
            file_size=1024,
        )

        assert upload.status == "PENDING"
        assert upload.storage_kind == "LOCAL"
        assert upload.submitted_at is not None
        assert upload.reviewed_at is None
        assert upload.reviewed_by is None
        assert upload.review_note == ""

    def test_uuid_primary_key_is_assigned(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
        )
        assert upload.id is not None
        assert len(str(upload.id)) == 36  # standard UUID4 string length


# ──────────────────────────────────────────────────────────────────
# Partial unique constraint — only one PENDING per variation
# ──────────────────────────────────────────────────────────────────

class TestPendingConstraint:

    def test_second_pending_upload_for_same_variation_is_blocked(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="first.pdf",
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ArtisanVaultUpload.objects.create(
                    artisan=chain["artisan"],
                    product=chain["product"],
                    variation=chain["variation"],
                    original_filename="second.pdf",
                )

    def test_approved_upload_then_new_pending_is_allowed(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        first = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="first.pdf",
        )
        first.status = "APPROVED"
        first.save(update_fields=["status"])

        # No unique violation — first is no longer PENDING.
        second = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="second.pdf",
        )
        assert second.status == "PENDING"

    def test_rejected_upload_then_new_pending_is_allowed(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        first = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="first.pdf",
        )
        first.status = "REJECTED"
        first.review_note = "Wrong file."
        first.save(update_fields=["status", "review_note"])

        second = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="second.pdf",
        )
        assert second.status == "PENDING"

    def test_multiple_superseded_uploads_are_allowed(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()

        a = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="first.pdf",
        )
        # Flip a to SUPERSEDED so we can create b. Only one PENDING is
        # allowed per variation, so the view layer must always supersede
        # the previous row before inserting a new one.
        a.status = "SUPERSEDED"
        a.review_note = "Superseded by newer upload."
        a.save(update_fields=["status", "review_note"])

        b = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="second.pdf",
        )
        b.status = "SUPERSEDED"
        b.review_note = "Superseded by newer upload."
        b.save(update_fields=["status", "review_note"])

        c = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="third.pdf",
        )

        assert c.status == "PENDING"
        assert ArtisanVaultUpload.objects.filter(
            variation=chain["variation"], status="SUPERSEDED"
        ).count() == 2
        assert ArtisanVaultUpload.objects.filter(
            variation=chain["variation"], status="PENDING"
        ).count() == 1

    def test_pending_for_different_variations_is_allowed(self, vault_chain):
        from store.models import ArtisanVaultUpload

        # Two chains means two distinct variations.
        chain_a = vault_chain()
        chain_b = vault_chain()

        ArtisanVaultUpload.objects.create(
            artisan=chain_a["artisan"],
            product=chain_a["product"],
            variation=chain_a["variation"],
            original_filename="a.pdf",
        )
        ArtisanVaultUpload.objects.create(
            artisan=chain_b["artisan"],
            product=chain_b["product"],
            variation=chain_b["variation"],
            original_filename="b.pdf",
        )
        # If we get here without IntegrityError, the constraint is
        # correctly scoped to (variation, status=PENDING).
        assert ArtisanVaultUpload.objects.filter(status="PENDING").count() == 2


# ──────────────────────────────────────────────────────────────────
# __str__ fallback chain
# ──────────────────────────────────────────────────────────────────

class TestStr:

    def test_str_uses_original_filename_when_present(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="the-book.pdf",
            staged_filename="abc.pdf",
        )
        assert "the-book.pdf" in str(upload)

    def test_str_falls_back_to_staged_filename(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            original_filename="",
            staged_filename="abc.pdf",
        )
        assert "abc.pdf" in str(upload)

    def test_str_falls_back_to_uuid_slug_when_both_blank(self, vault_chain):
        from store.models import ArtisanVaultUpload

        chain = vault_chain()
        upload = ArtisanVaultUpload.objects.create(
            artisan=chain["artisan"],
            product=chain["product"],
            variation=chain["variation"],
            storage_kind="EXTERNAL_PENDING",
            external_url="https://example.com/x.pdf",
        )
        # No filenames at all — should still print something stable.
        assert str(upload.id)[:8] in str(upload)

