# store/tests/test_artisan_vault_upload_view.py
"""
View-level tests for the artisan vault upload endpoint.

Covers:
  * Auth / ownership / digital-only gates
  * Direct upload happy path (file on disk, sha256 computed, row fields)
  * Validation failures (oversize, bad extension, content mismatch)
  * External link happy path
  * Supersession of an existing PENDING upload

Located under core/tests/ to match pytest.ini's testpaths.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    """Redirect XINDENG_VAULT_ROOT to a fresh per-test directory."""
    vault = tmp_path / "private_digital_vault"
    vault.mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def artisan_chain(db, django_user_model):
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="vault_artisan",
        email="artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Vault Artisan",
        slug="vault-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Digital Goods",
        slug="digital-goods",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",   # ← change to "Draft"
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
    }


# ──────────────────────────────────────────────────────────────────
# Byte factories
# ──────────────────────────────────────────────────────────────────

def _pdf_bytes() -> bytes:
    return b"%PDF-1.4\n% fake pdf for tests\n%%EOF\n"


def _zip_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("readme.txt", b"hello")
    return buf.getvalue()


def _not_pdf_bytes() -> bytes:
    return b"<html><body>Nope, not a PDF.</body></html>"


# ──────────────────────────────────────────────────────────────────
# URL helper
# ──────────────────────────────────────────────────────────────────

def _url(product, variation):
    return reverse(
        "a_dashboard_product_variation_upload_vault",
        args=[product.pk, variation.pk],
    )


# ──────────────────────────────────────────────────────────────────
# Auth and ownership gates
# ──────────────────────────────────────────────────────────────────

class TestGates:

    def test_unauthenticated_get_redirects_to_login(self, client, artisan_chain):
        chain = artisan_chain
        response = client.get(_url(chain["product"], chain["variation"]))
        assert response.status_code in (301, 302)
        assert "/accounts/login/" in response["Location"]

    def test_unauthenticated_post_redirects_to_login(self, client, artisan_chain):
        chain = artisan_chain
        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT"},
        )
        assert response.status_code in (301, 302)

    def test_other_artisan_gets_404(self, client, artisan_chain, django_user_model):
        from creators.models import CreatorProfile

        chain = artisan_chain
        other = django_user_model.objects.create_user(
            username="other",
            email="other@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        CreatorProfile.objects.create(
            user=other,
            display_name="Other",
            slug="other",
            is_verified=True,
        )
        client.force_login(other)
        response = client.get(_url(chain["product"], chain["variation"]))
        assert response.status_code == 404

    def test_non_digital_product_gets_404(self, client, artisan_chain, django_user_model):
        from category.models import Category
        from store.models import Product, ProductVariation

        chain = artisan_chain
        physical_cat = Category.objects.create(
            category_name="Physical Goods",
            slug="physical-goods",
            product_format="physical",
        )
        physical_product = Product.objects.create(
            product_name="Painting",
            category=physical_cat,
            creator=chain["profile"],
            is_digital=False,
            is_physical=True,
            is_active=True,
            status="Published",
        )
        physical_variation = ProductVariation.objects.create(
            product=physical_product,
            price=Decimal("10.00"),
            stock=5,
            is_available=True,
        )
        client.force_login(chain["user"])
        response = client.get(_url(physical_product, physical_variation))
        assert response.status_code == 404


# ──────────────────────────────────────────────────────────────────
# Direct upload — happy path and validation
# ──────────────────────────────────────────────────────────────────

class TestDirectUpload:

    def test_direct_upload_creates_row_and_file(self, client, artisan_chain, vault_root):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])

        pdf = _pdf_bytes()
        expected_sha = hashlib.sha256(pdf).hexdigest()
        uploaded = SimpleUploadedFile(
            "ebook.pdf", pdf, content_type="application/pdf",
        )

        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": uploaded},
        )
        assert response.status_code == 200
        assert response["HX-Retarget"] == "#variation-cards-container"

        upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert upload.storage_kind == "LOCAL"
        assert upload.status == "DRAFT"
        assert upload.original_filename == "ebook.pdf"
        assert upload.file_size == len(pdf)
        assert upload.checksum == expected_sha
        assert upload.staged_filename.endswith(".pdf")

        staged_path = vault_root / "_pending" / upload.staged_filename
        assert staged_path.is_file()
        assert staged_path.read_bytes() == pdf

    def test_direct_upload_rejects_oversize_file(
        self, client, artisan_chain, vault_root, settings,
    ):
        chain = artisan_chain
        client.force_login(chain["user"])

        # Shrink the cap so we don't have to build a 15 MB payload.
        settings.XINDENG_VAULT_MAX_BYTES = 64
        big_pdf = b"%PDF-1.4\n" + b"x" * 200 + b"\n%%EOF\n"
        uploaded = SimpleUploadedFile(
            "big.pdf", big_pdf, content_type="application/pdf",
        )

        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": uploaded},
        )
        assert response.status_code == 200  # form re-render with errors
        assert b"limit" in response.content.lower() or b"\xe4\xb8\x8a\xe9\x99\x90" in response.content

        # No row was created.
        from store.models import ArtisanVaultUpload
        assert not ArtisanVaultUpload.objects.filter(
            variation=chain["variation"]
        ).exists()

    def test_direct_upload_rejects_disallowed_extension(
        self, client, artisan_chain, vault_root,
    ):
        chain = artisan_chain
        client.force_login(chain["user"])

        uploaded = SimpleUploadedFile(
            "photo.png", b"\x89PNG\r\n\x1a\nfake", content_type="image/png",
        )
        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": uploaded},
        )
        assert response.status_code == 200
        from store.models import ArtisanVaultUpload
        assert not ArtisanVaultUpload.objects.filter(
            variation=chain["variation"]
        ).exists()

    def test_direct_upload_rejects_content_extension_mismatch(
        self, client, artisan_chain, vault_root,
    ):
        chain = artisan_chain
        client.force_login(chain["user"])

        # Extension says .pdf, bytes say HTML. Sniff returns None.
        uploaded = SimpleUploadedFile(
            "sneaky.pdf", _not_pdf_bytes(), content_type="application/pdf",
        )
        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": uploaded},
        )
        assert response.status_code == 200
        from store.models import ArtisanVaultUpload
        assert not ArtisanVaultUpload.objects.filter(
            variation=chain["variation"]
        ).exists()


# ──────────────────────────────────────────────────────────────────
# External upload
# ──────────────────────────────────────────────────────────────────

class TestExternalUpload:
    def test_external_upload_creates_draft_row(self, client, artisan_chain, vault_root):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])

        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={
                "upload_type": "EXTERNAL",
                "external_url": "https://drive.google.com/file/d/abc123/view",
                "checksum": "deadbeef",
            },
        )
        assert response.status_code == 200
        assert response["HX-Retarget"] == "#variation-cards-container"

        upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert upload.storage_kind == "EXTERNAL_PENDING"
        assert upload.status == "DRAFT"
        assert upload.staged_filename == ""
        assert upload.external_url.startswith("https://drive.google.com/")
        assert upload.checksum == "deadbeef"
        # No file written to disk.
        assert not any((vault_root / "_pending").glob("*")) if (vault_root / "_pending").exists() else True

    def test_external_upload_requires_url(self, client, artisan_chain, vault_root):
        chain = artisan_chain
        client.force_login(chain["user"])

        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "EXTERNAL", "external_url": ""},
        )
        assert response.status_code == 200
        from store.models import ArtisanVaultUpload
        assert not ArtisanVaultUpload.objects.filter(
            variation=chain["variation"]
        ).exists()


# ──────────────────────────────────────────────────────────────────
# Supersession
# ──────────────────────────────────────────────────────────────────

class TestSupersession:

    def test_supersede_deletes_old_staged_file_and_creates_new(
        self, client, artisan_chain, vault_root,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])

        # First upload.
        first = SimpleUploadedFile(
            "v1.pdf", _pdf_bytes(), content_type="application/pdf",
        )
        client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": first},
        )
        old_upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        old_staged = vault_root / "_pending" / old_upload.staged_filename
        assert old_staged.is_file()

        # Second upload.
        second = SimpleUploadedFile(
            "v2.pdf", _pdf_bytes() + b"\n% v2\n", content_type="application/pdf",
        )
        response = client.post(
            _url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": second},
        )
        assert response.status_code == 200

        # Old row is SUPERSEDED, its file is gone, and exactly one DRAFT remains.
        old_upload.refresh_from_db()
        assert old_upload.status == "SUPERSEDED"
        assert not old_staged.exists()

        draft = ArtisanVaultUpload.objects.filter(
            variation=chain["variation"], status="DRAFT",
        )
        assert draft.count() == 1
        new_upload = draft.first()
        assert new_upload.original_filename == "v2.pdf"
        assert (vault_root / "_pending" / new_upload.staged_filename).is_file()