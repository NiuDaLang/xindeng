# store/tests/test_vault_upload_location.py
"""
Tests for the Category.vault_subfolder routing added to
review_vault_upload_approve.

Covers:
  * INSTANT approval routes into category.vault_subfolder when set,
    and into the vault root when blank.
  * CUSTOM approval routes into category.vault_subfolder when set,
    writing the pointer on the OrderProduct (not the variation).
  * A category.vault_subfolder that escapes the vault root (e.g.
    ".." or an absolute path) is refused before any file moves.
  * A category.vault_subfolder that does not exist is auto-created
    on first approval (mkdir parents=True exists=True).
  * The previous pointer's file is retired under
    _retired/<previous_pointer>, preserving the subfolder prefix for
    routed files.

The ebooks/law_of_one.pdf historical file is not touched by these
tests; its pointer lives outside the approve path and the current
suite already covers "the gate serves whatever pointer is in the
DB" in test_secure_file_download_gate.py.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from django.urls import reverse

from tests._fakes import make_superuser


# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root(tmp_path, settings):
    vault = tmp_path / "private_digital_vault"
    (vault / "_pending").mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def superuser(db):
    return make_superuser(username="route_su", email="route-su@example.com")


@pytest.fixture
def make_chain(db, django_user_model, vault_root):
    """
    Builds an artisan + category + product + variation + a PENDING
    ArtisanVaultUpload whose staged file is on disk.

    Accepts an optional category_subfolder kwarg that flows into the
    category's vault_subfolder, and an optional custom=True flag to
    build an order-product-scoped chain.
    """
    _counter = {"n": 0}

    def _make(*, category_subfolder: str = "", custom: bool = False):
        _counter["n"] += 1
        n = _counter["n"]

        from category.models import Category
        from creators.models import CreatorProfile
        from store.models import (
            Product, ProductVariation, ArtisanVaultUpload,
        )

        artisan_user = django_user_model.objects.create_user(
            username=f"route_artisan_{n}",
            email=f"route-artisan-{n}@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        profile = CreatorProfile.objects.create(
            user=artisan_user,
            display_name=f"Route Artisan {n}",
            slug=f"route-artisan-{n}",
            is_verified=True,
        )
        category = Category.objects.create(
            category_name=f"Route Cat {n}",
            slug=f"route-cat-{n}",
            product_format="e-product",
            vault_subfolder=category_subfolder,
        )
        product = Product.objects.create(
            product_name=f"Route Ebook {n}",
            category=category,
            creator=profile,
            is_digital=True,
            digital_fulfillment_type="CUSTOM" if custom else "INSTANT",
            is_physical=False,
            is_active=True,
            status="Pending",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
        )

        staged_name = f"route-{n}.pdf"
        staged_path = vault_root / "_pending" / staged_name
        staged_path.write_bytes(b"%PDF-1.4\n% routed test\n%%EOF\n")

        order_product = None
        if custom:
            from orders.models import Order, OrderProduct
            customer = django_user_model.objects.create_user(
                username=f"route_customer_{n}",
                email=f"route-customer-{n}@example.com",
                receive_newsletter=False,
                password="x",
                is_active=True,
            )
            order = Order.objects.create(
                user=customer,
                order_number=f"ROUTE-{n:04d}",
                email=customer.email,
                is_ordered=True,
                order_status="Processing",
                product_total=Decimal("10.00"),
                total_due=Decimal("10.00"),
            )
            order_product = OrderProduct.objects.create(
                order=order,
                user=customer,
                product=product,
                product_variation=variation,
                product_price=Decimal("10.00"),
                quantity=1,
                ordered=True,
                fulfilled_by=profile,
            )

        upload = ArtisanVaultUpload.objects.create(
            artisan=profile,
            product=product,
            variation=variation,
            order_product=order_product,
            storage_kind="LOCAL",
            status="PENDING",
            staged_filename=staged_name,
            original_filename=f"ebook-{n}.pdf",
            file_size=staged_path.stat().st_size,
            checksum="deadbeef" * 8,
        )

        return {
            "profile": profile,
            "category": category,
            "product": product,
            "variation": variation,
            "order_product": order_product,
            "upload": upload,
            "staged_name": staged_name,
            "staged_path": staged_path,
        }

    return _make


def _approve_url(upload):
    return reverse("review_vault_upload_approve", args=[upload.id])


# ──────────────────────────────────────────────────────────────────
# INSTANT routing
# ──────────────────────────────────────────────────────────────────

class TestInstantRouting:

    def test_approves_into_subfolder_when_set(
        self, client, superuser, make_chain, vault_root,
    ):
        chain = make_chain(category_subfolder="epaintings")
        client.force_login(superuser)
        response = client.post(_approve_url(chain["upload"]))
        assert response.status_code in (301, 302)

        # File moved into the subfolder, not the root.
        assert not chain["staged_path"].exists()
        new_path = vault_root / "epaintings" / chain["staged_name"]
        assert new_path.is_file()
        assert not (vault_root / chain["staged_name"]).exists()

        # Pointer carries the prefix.
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path == (
            f"epaintings/{chain['staged_name']}"
        )

    def test_approves_into_root_when_subfolder_blank(
        self, client, superuser, make_chain, vault_root,
    ):
        chain = make_chain(category_subfolder="")
        client.force_login(superuser)
        response = client.post(_approve_url(chain["upload"]))
        assert response.status_code in (301, 302)

        assert not chain["staged_path"].exists()
        assert (vault_root / chain["staged_name"]).is_file()
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path == chain["staged_name"]

    def test_approves_into_existing_ebooks_folder(
        self, client, superuser, make_chain, vault_root,
    ):
        """Second subfolder — proves the routing is generic, not epaintings-specific."""
        chain = make_chain(category_subfolder="ebooks")
        client.force_login(superuser)
        client.post(_approve_url(chain["upload"]))

        assert (vault_root / "ebooks" / chain["staged_name"]).is_file()
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path == (
            f"ebooks/{chain['staged_name']}"
        )

    def test_creates_subfolder_on_first_approval(
        self, client, superuser, make_chain, vault_root,
    ):
        """
        The target subfolder does not exist before approval. The
        approve path must create it (mkdir parents=True exists=True
        already in the code); this is the "auto-create on first
        approved file" behaviour.
        """
        chain = make_chain(category_subfolder="brandnew")
        assert not (vault_root / "brandnew").exists()

        client.force_login(superuser)
        client.post(_approve_url(chain["upload"]))

        assert (vault_root / "brandnew").is_dir()
        assert (vault_root / "brandnew" / chain["staged_name"]).is_file()


# ──────────────────────────────────────────────────────────────────
# CUSTOM routing
# ──────────────────────────────────────────────────────────────────

class TestCustomRouting:

    def test_custom_approval_routes_into_subfolder_and_writes_op_pointer(
        self, client, superuser, make_chain, vault_root,
    ):
        chain = make_chain(category_subfolder="epaintings", custom=True)
        client.force_login(superuser)
        client.post(_approve_url(chain["upload"]))

        new_path = vault_root / "epaintings" / chain["staged_name"]
        assert new_path.is_file()
        assert not (vault_root / chain["staged_name"]).exists()

        # Pointer on the order product, prefixed.
        chain["order_product"].refresh_from_db()
        assert chain["order_product"].digital_file_path == (
            f"epaintings/{chain['staged_name']}"
        )

        # Variation pointer untouched (CUSTOM is order-scoped).
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path is None


# ──────────────────────────────────────────────────────────────────
# Containment — a hostile vault_subfolder is refused
# ──────────────────────────────────────────────────────────────────

class TestContainmentGuard:

    @pytest.mark.parametrize("hostile", [
        "../escape",
        "../../escape",
        "/etc",
    ])
    def test_hostile_subfolder_is_refused(
        self, client, superuser, make_chain, vault_root, hostile,
    ):
        chain = make_chain(category_subfolder=hostile)
        client.force_login(superuser)
        response = client.post(_approve_url(chain["upload"]))
        assert response.status_code in (301, 302)

        # File untouched: still staged, not moved anywhere.
        assert chain["staged_path"].is_file()
        chain["upload"].refresh_from_db()
        assert chain["upload"].status == "PENDING"
        chain["variation"].refresh_from_db()
        assert not chain["variation"].digital_file_path


# ──────────────────────────────────────────────────────────────────
# Retired file preserves the subfolder prefix
# ──────────────────────────────────────────────────────────────────

class TestRetirementWithSubfolder:

    def test_retired_file_lands_under_retired_subfolder(
        self, client, superuser, make_chain, vault_root,
    ):
        """
        Simulate an already-live previous file in the subfolder.
        Approve a new upload in the same category; the old file must
        land at _retired/epaintings/<old-name>, preserving the
        subfolder prefix. A future audit or cleanup pass can then
        tell which category the retired file came from.
        """
        chain = make_chain(category_subfolder="epaintings")

        old_name = "old-version.pdf"
        old_dir = vault_root / "epaintings"
        old_dir.mkdir(parents=True, exist_ok=True)
        old_path = old_dir / old_name
        old_path.write_bytes(b"%PDF-1.4\n% old\n%%EOF\n")

        chain["variation"].digital_file_path = f"epaintings/{old_name}"
        chain["variation"].save(update_fields=["digital_file_path"])

        client.force_login(superuser)
        client.post(_approve_url(chain["upload"]))

        # Old file retired under the subfolder-preserving path.
        assert not old_path.exists()
        retired = vault_root / "_retired" / "epaintings" / old_name
        assert retired.is_file()

        # New file is the live one.
        chain["variation"].refresh_from_db()
        assert chain["variation"].digital_file_path == (
            f"epaintings/{chain['staged_name']}"
        )