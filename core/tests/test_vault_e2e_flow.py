# core/tests/test_vault_e2e_flow.py
"""
End-to-end integration test for the private digital vault pipeline.

Proves the whole chain in one place:
    artisan stages an upload
    -> admin approves it (file moves into vault root, variation points at it)
    -> customer purchases the variation
    -> admin confirms payment (a DigitalDownloadToken is issued)
    -> secure_file_download_gate serves the exact bytes
    -> OrderProduct.is_claimed flips to True
    -> self-service cancellation is now blocked

Located under core/tests/ to match pytest.ini's testpaths.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

@pytest.fixture
def vault_root(tmp_path, settings):
    vault = tmp_path / "private_digital_vault"
    (vault / "_pending").mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


@pytest.fixture
def superuser(db, django_user_model):
    user = django_user_model.objects.create_user(
        username="e2e_superu",
        email="e2e-superu@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    user.is_superadmin = True
    user.is_staff = True
    user.save(update_fields=["is_superadmin", "is_staff"])
    return user


@pytest.fixture
def customer(db, django_user_model):
    return django_user_model.objects.create_user(
        username="e2e_customer",
        email="e2e-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def guest_buyer_account(db, django_user_model):
    """
    The account the guest eventually authenticates as to download.

    A guest order has Order.user=None. The person who placed it may
    register — or may already have an account — under the same email
    they used at checkout. That account is the identity the gate
    matches against token.email. Distinct from the order itself, which
    has no user at all.
    """
    return django_user_model.objects.create_user(
        username="e2e_guest_buyer",
        email="guest-buyer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_chain(db, django_user_model, vault_root):
    """Artisan + digital product + one variation + a staged PDF on disk."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import (
        Product, ProductVariation, ArtisanVaultUpload,
    )

    user = django_user_model.objects.create_user(
        username="e2e_artisan",
        email="e2e-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="E2E Artisan",
        slug="e2e-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="E2E Digital",
        slug="e2e-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="E2E Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_voucher=False,
        is_active=True,
        status="Published",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )

    staged_name = "e2e-book.pdf"
    pdf_bytes = b"%PDF-1.4\n% e2e vault test\n%%EOF\n"
    staged_path = vault_root / "_pending" / staged_name
    staged_path.write_bytes(pdf_bytes)

    upload = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        storage_kind="LOCAL",
        status="PENDING",
        staged_filename=staged_name,
        original_filename="ebook.pdf",
        file_size=len(pdf_bytes),
        checksum="deadbeef" * 8,
    )

    return {
        "artisan_user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
        "upload": upload,
        "staged_name": staged_name,
        "staged_path": staged_path,
        "pdf_bytes": pdf_bytes,
    }


def _make_admin_request(user):
    """
    Build a RequestFactory request with session + messages middleware
    attached so the admin action's messages.success/error calls work.
    """
    request = RequestFactory().get("/")
    SessionMiddleware(lambda r: None).process_request(request)
    request.session.save()
    MessageMiddleware(lambda r: None).process_request(request)
    request.user = user
    return request


def _read_file_response(response) -> bytes:
    if response.streaming:
        return b"".join(response.streaming_content)
    return response.content


# ------------------------------------------------------------------
# The chain
# ------------------------------------------------------------------

class TestVaultEndToEnd:

    def test_full_chain_upload_approve_buy_download_claim_block(
        self,
        client,
        superuser,
        customer,
        artisan_chain,
        vault_root,
    ):
        from store.models import DigitalDownloadToken
        from orders.models import Order, OrderProduct
        from orders.admin import confirm_bank_payment_admin_action

        chain = artisan_chain
        variation = chain["variation"]
        pdf_bytes = chain["pdf_bytes"]
        staged_name = chain["staged_name"]
        staged_path = chain["staged_path"]

        # -- Step 1: sanity -- staged file exists, vault is empty.
        assert staged_path.is_file()
        assert not (vault_root / staged_name).exists()
        assert not variation.digital_file_path

        # -- Step 2: admin approves the upload.
        client.force_login(superuser)
        approve_url = reverse(
            "review_vault_upload_approve", args=[chain["upload"].id],
        )
        response = client.post(approve_url)
        assert response.status_code in (301, 302)

        variation.refresh_from_db()
        assert variation.digital_file_path == staged_name
        assert (vault_root / staged_name).is_file()
        assert not staged_path.exists()

        # -- Step 3: customer places an order (hold pending).
        order = Order.objects.create(
            user=customer,
            order_number="E2E-VAULT-0001",
            email=customer.email,
            is_ordered=False,
            order_status="Hold_Pending",
            total_due=Decimal("10.00"),
            product_total=Decimal("10.00"),
        )
        order_product = OrderProduct.objects.create(
            order=order,
            user=customer,
            product=chain["product"],
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=False,
        )

        # -- Step 4: admin confirms bank payment, which issues a token.
        # Invoking the admin action directly keeps the test hermetic. The
        # email dispatches queued via transaction.on_commit are dropped when
        # the test's outer atomic exits, so no broker is needed.
        request = _make_admin_request(superuser)
        confirm_bank_payment_admin_action(
            None,
            request,
            Order.objects.filter(id=order.id),
        )

        order.refresh_from_db()
        order_product.refresh_from_db()
        assert order.is_ordered is True
        assert order.payment is not None
        assert order_product.ordered is True

        token = DigitalDownloadToken.objects.get(order_product=order_product)
        assert token.user == customer
        assert token.is_active is True
        assert token.is_revoked_or_expired is False

        # -- Step 5: customer downloads the file via the gate.
        client.force_login(customer)
        gate_url = reverse("secure_file_download_gate", args=[token.id])
        response = client.get(gate_url)

        assert response.status_code == 200
        assert _read_file_response(response) == pdf_bytes

        # -- Step 6: gate flipped the claim flag.
        order_product.refresh_from_db()
        assert order_product.is_claimed is True
        assert order_product.claim_timestamp is not None

        # -- Step 7: cancellation is now blocked.
        eligible, fee, msg = order.evaluate_cancellation_details()
        assert eligible is False
        assert "claimed" in msg.lower()
        assert order.can_be_cancelled_online is False


class TestVaultEndToEndGuest:
    """
    Guest variant of TestVaultEndToEnd. Same vault chain — artisan
    stages -> admin approves -> buyer purchases -> admin confirms ->
    gate serves -> claim flips -> cancellation blocked — but with
    Order.user=None throughout, and the download identity coming from
    the token's email snapshot rather than a user FK.

    This is the test that would have caught the pre-#7.5 bug: a guest
    purchase of an instant-digital product raised IntegrityError inside
    confirm_bank_payment_admin_action's transaction.atomic, and the
    action's broad except swallowed it. Even once the token could be
    created, the old gate's get_object_or_404(..., user=request.user)
    lookup made guest tokens unreachable.

    It exercises three things that were changed separately:
      * 0039/0040 backfill and nullability (implicitly — the token is
        created with user=None)
      * issue_download_token writing the email snapshot
      * the gate's email-match fallback
    against the same path a real guest purchase takes.
    """

    def test_guest_chain_upload_approve_buy_download_claim_block(
        self,
        client,
        superuser,
        guest_buyer_account,
        artisan_chain,
        vault_root,
    ):
        from store.models import DigitalDownloadToken
        from orders.models import Order, OrderProduct
        from orders.admin import confirm_bank_payment_admin_action

        chain = artisan_chain
        variation = chain["variation"]
        pdf_bytes = chain["pdf_bytes"]
        staged_name = chain["staged_name"]
        staged_path = chain["staged_path"]

        # -- Step 1: sanity -- staged file exists, vault is empty.
        assert staged_path.is_file()
        assert not (vault_root / staged_name).exists()
        assert not variation.digital_file_path

        # -- Step 2: admin approves the upload.
        client.force_login(superuser)
        approve_url = reverse(
            "review_vault_upload_approve", args=[chain["upload"].id],
        )
        response = client.post(approve_url)
        assert response.status_code in (301, 302)

        variation.refresh_from_db()
        assert variation.digital_file_path == staged_name
        assert (vault_root / staged_name).is_file()
        assert not staged_path.exists()

        # -- Step 3: guest places an order (hold pending). Order.user is
        # None; the email is the only buyer identity on the row.
        order = Order.objects.create(
            user=None,
            order_number="E2E-VAULT-GUEST-0001",
            email="guest-buyer@example.com",
            is_ordered=False,
            order_status="Hold_Pending",
            total_due=Decimal("10.00"),
            product_total=Decimal("10.00"),
        )
        order_product = OrderProduct.objects.create(
            order=order,
            user=None,
            product=chain["product"],
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=False,
        )

        # -- Step 4: admin confirms bank payment, which issues a token.
        # Before #7.5 this raised IntegrityError inside the atomic block
        # and the action's broad except swallowed it, leaving the
        # operator with no visible signal.
        request = _make_admin_request(superuser)
        confirm_bank_payment_admin_action(
            None,
            request,
            Order.objects.filter(id=order.id),
        )

        order.refresh_from_db()
        order_product.refresh_from_db()
        assert order.is_ordered is True
        assert order.payment is not None
        assert order_product.ordered is True

        token = DigitalDownloadToken.objects.get(order_product=order_product)
        # The two fields that make the guest path possible.
        assert token.user_id is None
        assert token.email == "guest-buyer@example.com"
        assert token.is_active is True
        assert token.is_revoked_or_expired is False

        # -- Step 5: the guest authenticates under a matching email and
        # downloads via the gate. The gate has no user FK to match
        # against, so it falls back to comparing token.email with
        # request.user.email (case-insensitively).
        client.force_login(guest_buyer_account)
        gate_url = reverse("secure_file_download_gate", args=[token.id])
        response = client.get(gate_url)

        assert response.status_code == 200
        assert _read_file_response(response) == pdf_bytes

        # -- Step 6: gate flipped the claim flag, same contract as the
        # member path.
        order_product.refresh_from_db()
        assert order_product.is_claimed is True
        assert order_product.claim_timestamp is not None

        # -- Step 7: cancellation is blocked. evaluate_cancellation_details
        # does not look at Order.user, so the guest path reaches the same
        # "claimed" refusal as the member path.
        eligible, fee, msg = order.evaluate_cancellation_details()
        assert eligible is False
        assert "claimed" in msg.lower()
        assert order.can_be_cancelled_online is False