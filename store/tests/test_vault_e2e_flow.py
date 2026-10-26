# store/tests/test_vault_e2e_flow.py
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

The `superuser` fixture uses `make_superuser` (from tests/_fakes.py),
which sets both is_admin and is_superadmin. This file only strictly
needs is_superadmin — every admin-facing action here is guarded by
superuser_required, not by Django's ModelAdmin.has_view_permission.
But the fixture is shared across the three store vault test files
and the settlements aggregate tests for uniformity; if this file
ever gains a test that hits the admin changelist (e.g. testing
OrderAdmin.get_actions filtering), the fixture is already correct.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse

from tests._fakes import make_superuser


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
def superuser(db):
    return make_superuser(username="e2e_superu", email="e2e-superu@example.com")


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
        status="Pending",
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


# ------------------------------------------------------------------
# Supersession and claim-integrity edge cases
# ------------------------------------------------------------------

@pytest.fixture
def chain_with_supersession(db, django_user_model, vault_root):
    """
    Artisan + digital product + one variation, with a supersession
    already recorded in the staging area.

    v1 was staged first, then replaced by v2 before any admin review.
    The vault-side state at fixture teardown:

        v1: status=SUPERSEDED, staged file deleted from _pending/
        v2: status=PENDING,    staged file present in _pending/

    Neither file has been approved. variation.digital_file_path is
    empty. The fixture asserts these invariants inline so that a
    future change to the supersession view that silently leaves v1's
    file on disk cannot make this fixture's premise quietly untrue —
    the fixture would fail loudly at setup, not produce a confusing
    failure three assertions into the test body.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import (
        Product, ProductVariation, ArtisanVaultUpload,
    )

    user = django_user_model.objects.create_user(
        username="e2e_supersede_artisan",
        email="e2e-supersede-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="E2E Supersede Artisan",
        slug="e2e-supersede-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="E2E Supersede Digital",
        slug="e2e-supersede-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="E2E Supersede Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_voucher=False,
        is_active=True,
        status="Pending",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )

    # ── v1: staged, then superseded ─────────────────────────────
    v1_name = "supersede-v1.pdf"
    v1_bytes = b"%PDF-1.4\n% supersede v1\n%%EOF\n"
    v1_path = vault_root / "_pending" / v1_name

    v1 = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        storage_kind="LOCAL",
        status="SUPERSEDED",
        staged_filename=v1_name,
        original_filename="ebook-v1.pdf",
        file_size=len(v1_bytes),
        checksum="v1checksum".ljust(64, "0"),
        review_note="Superseded by a newer upload from the artisan.",
    )

    # ── v2: staged, pending, on disk ────────────────────────────
    v2_name = "supersede-v2.pdf"
    v2_bytes = b"%PDF-1.4\n% supersede v2\n%%EOF\n"
    v2_path = vault_root / "_pending" / v2_name
    v2_path.write_bytes(v2_bytes)

    v2 = ArtisanVaultUpload.objects.create(
        artisan=profile,
        product=product,
        variation=variation,
        storage_kind="LOCAL",
        status="PENDING",
        staged_filename=v2_name,
        original_filename="ebook-v2.pdf",
        file_size=len(v2_bytes),
        checksum="v2checksum".ljust(64, "0"),
    )

    # ── Fixture premise assertions ──────────────────────────────
    # If any of these fail, the supersession pipeline is not in the
    # state the rest of this test class assumes, and the failure
    # belongs here rather than three assertions into a test body.
    assert not v1_path.exists(), (
        "v1 staged file must have been deleted by the supersession flow"
    )
    assert v2_path.is_file(), (
        "v2 staged file must exist for the pending approval step"
    )
    assert not variation.digital_file_path, (
        "variation pointer must be empty before approval"
    )
    assert ArtisanVaultUpload.objects.filter(
        variation=variation, status="PENDING",
    ).count() == 1, "exactly one PENDING row per variation"

    return {
        "artisan_user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
        "v1": v1,
        "v2": v2,
        "v1_name": v1_name,
        "v2_name": v2_name,
        "v1_bytes": v1_bytes,
        "v2_bytes": v2_bytes,
        "v1_path": v1_path,
        "v2_path": v2_path,
    }


class TestVaultEndToEndSupersession:
    """
    The vault root is the delivery source. When an artisan supersedes
    an upload before review, the approved file is the *later* one, and
    the gate must serve that one — not the earlier, superseded file.

    This is the case the plain member/guest E2E cannot catch: with a
    single staged upload there is only one candidate, so any
    accidentally-loose pointer lookup still resolves to the right
    bytes.
    """

    def test_gate_serves_the_approved_file_not_the_superseded_one(
        self,
        client,
        superuser,
        customer,
        chain_with_supersession,
        vault_root,
    ):
        from store.models import DigitalDownloadToken
        from orders.models import Order, OrderProduct
        from orders.admin import confirm_bank_payment_admin_action

        chain = chain_with_supersession
        variation = chain["variation"]
        v2_name = chain["v2_name"]
        v2_bytes = chain["v2_bytes"]

        # -- Step 1: sanity, restated from the fixture for clarity --
        assert not chain["v1_path"].exists()
        assert chain["v2_path"].is_file()
        assert not variation.digital_file_path
        assert not (vault_root / v2_name).exists()

        # -- Step 2: admin approves the PENDING row (v2). --
        client.force_login(superuser)
        approve_url = reverse(
            "review_vault_upload_approve", args=[chain["v2"].id],
        )
        response = client.post(approve_url)
        assert response.status_code in (301, 302)

        variation.refresh_from_db()
        assert variation.digital_file_path == v2_name
        assert (vault_root / v2_name).is_file()
        assert not chain["v2_path"].exists()

        # v1 remains a historical record. Its row is still there and
        # still SUPERSEDED; nothing about approval of v2 revives it.
        chain["v1"].refresh_from_db()
        assert chain["v1"].status == "SUPERSEDED"

        # -- Step 3: customer places an order (hold pending). --
        order = Order.objects.create(
            user=customer,
            order_number="E2E-VAULT-SUPER-0001",
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

        # -- Step 4: admin confirms payment; token issued. --
        request = _make_admin_request(superuser)
        confirm_bank_payment_admin_action(
            None,
            request,
            Order.objects.filter(id=order.id),
        )

        order.refresh_from_db()
        order_product.refresh_from_db()
        assert order.is_ordered is True
        assert order_product.ordered is True

        token = DigitalDownloadToken.objects.get(order_product=order_product)
        assert token.user == customer
        assert token.is_revoked_or_expired is False

        # -- Step 5: the load-bearing assertion. --
        # The gate must stream v2's bytes, not v1's. v1's bytes are
        # distinguishable from v2's by a marker line, so a naive
        # implementation that resolved the *first* upload rather than
        # the variation's current pointer would fail here.
        client.force_login(customer)
        gate_url = reverse("secure_file_download_gate", args=[token.id])
        response = client.get(gate_url)

        assert response.status_code == 200
        body = _read_file_response(response)
        assert body == v2_bytes
        assert b"supersede v2" in body
        assert b"supersede v1" not in body

        # -- Step 6: claim flipped, cancellation blocked. --
        order_product.refresh_from_db()
        assert order_product.is_claimed is True
        assert order_product.claim_timestamp is not None

        eligible, fee, msg = order.evaluate_cancellation_details()
        assert eligible is False
        assert "claimed" in msg.lower()
        assert order.can_be_cancelled_online is False

    def test_failed_download_does_not_flip_is_claimed(
        self,
        client,
        superuser,
        customer,
        artisan_chain,
        vault_root,
    ):
        """
        A download that fails before any bytes are served must not
        flip OrderProduct.is_claimed.

        is_claimed gates the self-service cancellation window. If the
        gate flipped it on a 404 — before the customer had received
        anything — a customer could intentionally request a download
        of a file that isn't there, lock their own order, and then
        retain the (still-downloadable-in-principle) digital asset
        outside the cancellation rules. The gate must only claim on
        a successful serve.

        Uses the plain artisan_chain fixture (single upload, no
        supersession) so this test isolates the claim-on-404
        behaviour from the supersession path.
        """
        from store.models import DigitalDownloadToken
        from orders.models import Order, OrderProduct
        from orders.admin import confirm_bank_payment_admin_action

        chain = artisan_chain
        variation = chain["variation"]
        staged_name = chain["staged_name"]

        # -- Step 1: approve the upload as normal. --
        client.force_login(superuser)
        approve_url = reverse(
            "review_vault_upload_approve", args=[chain["upload"].id],
        )
        response = client.post(approve_url)
        assert response.status_code in (301, 302)

        variation.refresh_from_db()
        assert variation.digital_file_path == staged_name

        # -- Step 2: buy, confirm payment, token issued. --
        order = Order.objects.create(
            user=customer,
            order_number="E2E-VAULT-404-0001",
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

        request = _make_admin_request(superuser)
        confirm_bank_payment_admin_action(
            None,
            request,
            Order.objects.filter(id=order.id),
        )

        order.refresh_from_db()
        order_product.refresh_from_db()
        assert order.is_ordered is True
        token = DigitalDownloadToken.objects.get(order_product=order_product)
        assert token.user == customer
        assert order_product.is_claimed is False  # sanity

        # -- Step 3: simulate the file having gone missing in the
        # vault after approval but before the customer downloads. --
        # The approval moved the file into the vault root; delete it
        # there. The variation's pointer still names the (now-missing)
        # file, so the gate's containment check passes and its
        # is_file() check fails, raising Http404 before any
        # transaction.atomic() claim block is entered.
        vault_file = vault_root / staged_name
        assert vault_file.is_file()
        vault_file.unlink()
        assert not vault_file.exists()

        # -- Step 4: the customer requests the download. --
        client.force_login(customer)
        gate_url = reverse("secure_file_download_gate", args=[token.id])
        response = client.get(gate_url)

        assert response.status_code == 404

        # -- Step 5: the load-bearing assertion. --
        # Confirm the failure is the missing-file branch and not the
        # containment branch: the pointer still names a file *inside*
        # the vault root, so is_relative_to() passes and the
        # is_file() check is what raised. If a future change moved the
        # claim block above the is_file() check, the flag would flip
        # here even though the file was never served.
        assert variation.digital_file_path == staged_name
        assert staged_name in str(vault_file)  # still inside vault_root

        order_product.refresh_from_db()
        assert order_product.is_claimed is False
        assert order_product.claim_timestamp is None

        # -- Step 6: the cancellation window is still open. --
        # The customer received nothing, so the ordinary
        # unclaimed-digital eligibility rule applies. If the gate had
        # flipped is_claimed above, this assertion would fail with
        # the "claimed" message instead of returning eligible=True.
        eligible, fee, msg = order.evaluate_cancellation_details()
        assert eligible is True
        assert "claimed" not in msg.lower()
        assert order.can_be_cancelled_online is True

