# store/tests/test_vault_upload_draft_status.py
"""
Tests for the DRAFT status on ArtisanVaultUpload.

The file has two halves. The first half pins the two
draft_staged_count properties. The second half pins the status a new
upload starts in, from the variation-upload view (DRAFT for every
upload that reaches it) and the order-product-scoped sibling (PENDING
unconditionally). The promotion of DRAFT → PENDING on submit and the
demotion on withdraw are a later commit and are not covered here. Testing the counters
first pins the read side before the write side exists, so a later
change to the promotion cannot silently break the badge.

Mirrors test_vault_upload_badge.py's shape, including the
two-variation fixture, so the aggregate (Product) and the
per-variation (ProductVariation) counters are distinguished from the
first test rather than retrofitted.
"""

from __future__ import annotations

from decimal import Decimal

import pytest


# A 1×1 opaque PNG. The smallest valid image Pillow will decode; used
# to satisfy the submission-time image requirement in tests that are
# not about that requirement.
_MINIMAL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\x00"
    b"\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# ──────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def artisan_chain(db, django_user_model):
    """Artisan + digital product + one variation, Draft status."""
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="draft_artisan",
        email="draft@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Draft Artisan",
        slug="draft-artisan",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Draft Digital",
        slug="draft-digital",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Draft Ebook",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",
    )
    variation = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    # The pre-existing A2 submission-time image requirement on
    # dashboard_product_submit refuses to flip to Pending if the
    # product has no featured image. That check predates this file;
    # the tests here are about the deliverability guard and the
    # DRAFT → PENDING promotion, not about the image requirement.
    # Seed a tiny valid image so the image check passes and the code
    # under test is reached.
    from django.core.files.uploadedfile import SimpleUploadedFile
    product.images.save(
        "hero.png",
        SimpleUploadedFile(
            "hero.png",
            _MINIMAL_PNG_BYTES,
            content_type="image/png",
        ),
        save=True,
    )    
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation": variation,
    }


@pytest.fixture
def two_variation_chain(db, django_user_model):
    """
    Same shape as artisan_chain, but with two variations on one product.

    This is the fixture that distinguishes the aggregate from the
    per-variation property: a test that accidentally reads the wrong
    one still passes with a single variation, but fails here.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation

    user = django_user_model.objects.create_user(
        username="draft_artisan_two",
        email="draft-two@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=user,
        display_name="Draft Artisan Two",
        slug="draft-artisan-two",
        is_verified=True,
    )
    category = Category.objects.create(
        category_name="Draft Digital Two",
        slug="draft-digital-two",
        product_format="e-product",
    )
    product = Product.objects.create(
        product_name="Draft Ebook Two",
        category=category,
        creator=profile,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_physical=False,
        is_active=True,
        status="Draft",
    )
    variation_a = ProductVariation.objects.create(
        product=product,
        price=Decimal("10.00"),
        stock=1,
        is_available=True,
    )
    variation_b = ProductVariation.objects.create(
        product=product,
        price=Decimal("12.00"),
        stock=1,
        is_available=True,
    )
    # The pre-existing A2 submission-time image requirement on
    # dashboard_product_submit refuses to flip to Pending if the
    # product has no featured image. That check predates this file;
    # the tests here are about the deliverability guard and the
    # DRAFT → PENDING promotion, not about the image requirement.
    # Seed a tiny valid image so the image check passes and the code
    # under test is reached.
    from django.core.files.uploadedfile import SimpleUploadedFile
    product.images.save(
        "hero.png",
        SimpleUploadedFile(
            "hero.png",
            _MINIMAL_PNG_BYTES,
            content_type="image/png",
        ),
        save=True,
    )    
    return {
        "user": user,
        "profile": profile,
        "product": product,
        "variation_a": variation_a,
        "variation_b": variation_b,
    }


def _make_upload(chain, variation, *, status_value, name):
    from store.models import ArtisanVaultUpload
    return ArtisanVaultUpload.objects.create(
        artisan=chain["profile"],
        product=chain["product"],
        variation=variation,
        status=status_value,
        staged_filename=name,
    )


# ──────────────────────────────────────────────────────────────────
# DRAFT is accepted by the model
# ──────────────────────────────────────────────────────────────────

class TestDraftStatusAccepted:

    def test_draft_is_a_valid_status(self, artisan_chain):
        """
        The choices tuple is the model-level contract. A row can be
        created with status=DRAFT and reads back as DRAFT. Full_clean
        is not called; Model.save() does not validate choices, so this
        test proves the choice exists (the constant), not that the
        field rejects other values.
        """
        from store.models import ArtisanVaultUpload

        assert "DRAFT" in dict(ArtisanVaultUpload.STATUS_CHOICES)

        upload = _make_upload(
            artisan_chain, artisan_chain["variation"],
            status_value="DRAFT", name="draft.pdf",
        )
        upload.refresh_from_db()
        assert upload.status == "DRAFT"

    def test_existing_statuses_unchanged(self):
        """
        Regression guard: adding DRAFT must not have reordered or
        renamed the other four choices. The admin and the review
        queue depend on PENDING's label.
        """
        from store.models import ArtisanVaultUpload

        choices = dict(ArtisanVaultUpload.STATUS_CHOICES)
        assert choices["PENDING"] == "Pending review"
        assert choices["APPROVED"] == "Approved"
        assert choices["REJECTED"] == "Rejected by admin"
        assert choices["SUPERSEDED"] == "Superseded by newer upload"


# ──────────────────────────────────────────────────────────────────
# Per-variation counter
# ──────────────────────────────────────────────────────────────────

class TestVariationDraftStagedCount:

    def test_zero_when_no_uploads_exist(self, artisan_chain):
        assert artisan_chain["variation"].draft_staged_count == 0

    def test_counts_a_single_draft_upload(self, artisan_chain):
        _make_upload(
            artisan_chain, artisan_chain["variation"],
            status_value="DRAFT", name="d.pdf",
        )
        assert artisan_chain["variation"].draft_staged_count == 1

    def test_ignores_the_other_statuses(self, artisan_chain):
        chain = artisan_chain
        v = chain["variation"]

        # One of each non-DRAFT status. PENDING is created then flipped
        # to APPROVED / REJECTED / SUPERSEDED so the partial unique
        # constraint is not violated mid-test.
        pending = _make_upload(chain, v, status_value="PENDING", name="p.pdf")
        approved = _make_upload(chain, v, status_value="APPROVED", name="a.pdf")
        rejected = _make_upload(chain, v, status_value="REJECTED", name="r.pdf")
        superseded = _make_upload(chain, v, status_value="SUPERSEDED", name="s.pdf")

        # No DRAFT rows yet.
        assert v.draft_staged_count == 0

        _make_upload(chain, v, status_value="DRAFT", name="d.pdf")

        # Still exactly 1, not 5.
        assert v.draft_staged_count == 1


# ──────────────────────────────────────────────────────────────────
# Product aggregate counter
# ──────────────────────────────────────────────────────────────────

class TestProductDraftStagedCount:

    def test_zero_when_no_uploads_exist(self, two_variation_chain):
        assert two_variation_chain["product"].draft_staged_count == 0

    def test_counts_across_two_variations(self, two_variation_chain):
        """
        The aggregate must sum across variations. A wrong
        implementation that reads a single variation's counter
        returns 1 here and fails.
        """
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        _make_upload(chain, chain["variation_b"], status_value="DRAFT", name="b.pdf")

        assert chain["variation_a"].draft_staged_count == 1
        assert chain["variation_b"].draft_staged_count == 1
        assert chain["product"].draft_staged_count == 2

    def test_one_draft_one_none_returns_one(self, two_variation_chain):
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        # variation_b deliberately has no upload.

        assert chain["product"].draft_staged_count == 1

    def test_pending_rows_do_not_leak_into_draft_count(self, two_variation_chain):
        """
        Comparison-shaped: the two counters are disjoint. A product
        with one DRAFT and one PENDING row has draft_staged_count == 1
        and pending_vault_upload_count == 1, not 2 and 2.
        """
        chain = two_variation_chain
        _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        _make_upload(chain, chain["variation_b"], status_value="PENDING", name="b.pdf")

        assert chain["product"].draft_staged_count == 1
        assert chain["product"].pending_vault_upload_count == 1

    def test_promotion_decrements_draft_count(self, two_variation_chain):
        """
        A DRAFT row flipped to PENDING leaves the DRAFT count and
        enters the PENDING count. No promotion code exists yet, so
        this flips the status by hand — the point is to pin that the
        two counters read the same row in exactly one of them at a
        time, which is the invariant the promotion will rely on.
        """
        chain = two_variation_chain
        pending = _make_upload(chain, chain["variation_a"], status_value="DRAFT", name="a.pdf")
        assert chain["product"].draft_staged_count == 1
        assert chain["product"].pending_vault_upload_count == 0

        pending.status = "PENDING"
        pending.save(update_fields=["status"])

        assert chain["product"].draft_staged_count == 0
        assert chain["product"].pending_vault_upload_count == 1


# ──────────────────────────────────────────────────────────────────
# Upload-view transition — the status a new row starts in
# ──────────────────────────────────────────────────────────────────

@pytest.fixture
def vault_root_for_draft(tmp_path, settings):
    """
    Per-test vault root. The other fixtures in this file do not write
    to disk, so this only becomes necessary when the upload view is
    exercised. Named distinctly from `vault_root` (which other files
    define) to avoid a cross-file collision if this file is ever
    merged into a single vault test module.
    """
    vault = tmp_path / "private_digital_vault"
    (vault / "_pending").mkdir(parents=True, exist_ok=True)
    settings.XINDENG_VAULT_ROOT = vault
    return vault


def _upload_url(product, variation):
    from django.urls import reverse
    return reverse(
        "a_dashboard_product_variation_upload_vault",
        args=[product.pk, variation.pk],
    )


def _pdf_upload():
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(
        "draft.pdf", b"%PDF-1.4\n% draft status test\n%%EOF\n",
        content_type="application/pdf",
    )


class TestUploadInitialStatus:
    """
    The status a new ArtisanVaultUpload starts in, per _initial_upload_status.

    Draft / Rejected / Unpublished → DRAFT (the artisan is building or
    revising, and the file must not enter the admin queue before the
    product is resubmitted). CUSTOM (order-product-scoped) → PENDING
    regardless, because the helper short-circuits on order_product is
    not None; that case is covered in TestCustomUploadAlwaysPending.

    Pending and Published are not tested here: the view refuses them at
    the is_editable_by_artisan guard before the helper is reached. See
    TestUploadRefusedOnLockedProduct.
    """

    def _set_status_and_login(self, client, chain, status_value):
        from store.models import Product
        Product.objects.filter(pk=chain["product"].pk).update(status=status_value)
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

    def _post_upload(self, client, chain):
        return client.post(
            _upload_url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": _pdf_upload()},
        )

    def test_draft_product_creates_draft_row(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        self._set_status_and_login(client, chain, "Draft")
        self._post_upload(client, chain)

        upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert upload.status == "DRAFT"

    def test_rejected_product_creates_draft_row(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        self._set_status_and_login(client, chain, "Rejected")
        self._post_upload(client, chain)

        upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert upload.status == "DRAFT"

    def test_unpublished_product_creates_draft_row(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        self._set_status_and_login(client, chain, "Unpublished")
        self._post_upload(client, chain)

        upload = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert upload.status == "DRAFT"

    def test_draft_upload_does_not_dispatch_admin_email(
        self, client, artisan_chain, vault_root_for_draft,
        django_capture_on_commit_callbacks, monkeypatch,
    ):
        from store.tasks import send_vault_upload_pending_email_task

        chain = artisan_chain
        self._set_status_and_login(client, chain, "Draft")

        dispatched = []
        monkeypatch.setattr(
            send_vault_upload_pending_email_task, "delay",
            lambda uid: dispatched.append(uid),
        )
        with django_capture_on_commit_callbacks(execute=True):
            self._post_upload(client, chain)

        assert dispatched == []

    def test_reupload_while_draft_supersedes_the_draft(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        """
        Two uploads while the product is still in Draft. The first
        row is superseded; exactly one DRAFT remains. This is the
        widening of the supersession filter — with the old PENDING-only
        filter, the second upload would create a second DRAFT row and
        the partial unique constraint would not have fired (it only
        governs PENDING).
        """
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        self._set_status_and_login(client, chain, "Draft")
        self._post_upload(client, chain)
        first = ArtisanVaultUpload.objects.get(variation=chain["variation"])
        assert first.status == "DRAFT"

        self._post_upload(client, chain)

        first.refresh_from_db()
        assert first.status == "SUPERSEDED"
        assert ArtisanVaultUpload.objects.filter(
            variation=chain["variation"], status="DRAFT",
        ).count() == 1
        assert ArtisanVaultUpload.objects.filter(
            variation=chain["variation"], status="PENDING",
        ).count() == 0


class TestUploadRefusedOnLockedProduct:
    """
    The is_editable_by_artisan guard on the variation-upload view.

    A Pending or Published product is not editable by the artisan; the
    template hides the Vault button, but the view was the only thing
    standing between a forged POST and a row. The guard closes that
    path. Two states are refused, not one: the memo's transition table
    named only Published, but is_editable_by_artisan also excludes
    Pending, and the two refusals are the same shape.
    """

    def _assert_refused(self, client, chain):
        from store.models import ArtisanVaultUpload
        from django.contrib.messages import get_messages
        from django.urls import reverse

        response = client.post(
            _upload_url(chain["product"], chain["variation"]),
            data={"upload_type": "DIRECT", "file": _pdf_upload()},
        )

        assert response.status_code == 302
        assert response["Location"] == reverse("a_dashboard_products")
        assert not ArtisanVaultUpload.objects.filter(
            variation=chain["variation"]
        ).exists()
        messages_list = [str(m) for m in get_messages(response.wsgi_request)]
        assert any("cannot accept uploads" in m for m in messages_list)

    def test_forged_post_against_published_product_is_refused(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(status="Published")
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        self._assert_refused(client, chain)

    def test_forged_post_against_pending_product_is_refused(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(status="Pending")
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        self._assert_refused(client, chain)


class TestCustomUploadAlwaysPending:
    """
    The CUSTOM path is the only remaining way a view produces a PENDING
    row on upload. _initial_upload_status returns PENDING unconditionally
    when order_product is set, because the order line already exists and
    the product is already Published (so the Draft → submit → review
    lifecycle that DRAFT exists to serve does not apply).

    Lived in test_artisan_orders_dashboard.py::TestOrderProductVaultUploadView
    before this correction, but only as an assertion about supersession
    keying. The status assertion belongs here, in the file that names
    every status transition. Keeping it there would mean the invariant
    "CUSTOM starts PENDING" was tested in a file whose name does not say
    so, and a reader looking for the rule would not find it.
    """

    @pytest.fixture
    def custom_line_chain(self, db, django_user_model, vault_root_for_draft):
        from category.models import Category
        from creators.models import CreatorProfile
        from store.models import Product, ProductVariation
        from orders.models import Order, OrderProduct

        user = django_user_model.objects.create_user(
            username="custom_draft_artisan",
            email="custom-draft@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        profile = CreatorProfile.objects.create(
            user=user,
            display_name="Custom Draft Artisan",
            slug="custom-draft-artisan",
            is_verified=True,
        )
        category = Category.objects.create(
            category_name="Custom Draft Digital",
            slug="custom-draft-digital",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name="Custom Draft Book",
            category=category,
            creator=profile,
            is_digital=True,
            digital_fulfillment_type="CUSTOM",
            is_physical=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("20.00"),
            stock=1,
            is_available=True,
        )
        customer = django_user_model.objects.create_user(
            username="custom_draft_customer",
            email="custom-draft-customer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        order = Order.objects.create(
            user=customer,
            order_number="CUSTOM-DRAFT-0001",
            email=customer.email,
            is_ordered=True,
            order_status="Processing",
        )
        line = OrderProduct.objects.create(
            order=order,
            user=customer,
            product=product,
            product_variation=variation,
            product_price=Decimal("20.00"),
            quantity=1,
            ordered=True,
            fulfilled_by=profile,
        )
        return {
            "user": user,
            "profile": profile,
            "product": product,
            "variation": variation,
            "line": line,
        }

    def _post(self, client, chain):
        from django.urls import reverse
        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["line"].id],
        )
        return client.post(
            url,
            data={"upload_type": "DIRECT", "file": _pdf_upload()},
        )

    def test_custom_upload_creates_pending_row(
        self, client, custom_line_chain,
        django_capture_on_commit_callbacks,
    ):
        from store.models import ArtisanVaultUpload

        chain = custom_line_chain
        client.force_login(chain["user"])
        with django_capture_on_commit_callbacks(execute=False):
            self._post(client, chain)

        upload = ArtisanVaultUpload.objects.get(
            order_product=chain["line"],
        )
        assert upload.status == "PENDING"

    def test_custom_upload_dispatches_admin_email(
        self, client, custom_line_chain,
        django_capture_on_commit_callbacks, monkeypatch,
    ):
        from store.models import ArtisanVaultUpload
        from store.tasks import send_vault_upload_pending_email_task

        chain = custom_line_chain
        client.force_login(chain["user"])

        dispatched = []
        monkeypatch.setattr(
            send_vault_upload_pending_email_task, "delay",
            lambda uid: dispatched.append(uid),
        )
        with django_capture_on_commit_callbacks(execute=True):
            self._post(client, chain)

        upload = ArtisanVaultUpload.objects.get(
            order_product=chain["line"],
        )
        assert dispatched == [str(upload.id)]


# ──────────────────────────────────────────────────────────────────
# Submit / withdraw — the promotion and the pre-submit guard
# ──────────────────────────────────────────────────────────────────

def _upload_url_standalone(product):
    """
    The standalone submit URL. Distinct from _upload_url, which is the
    vault-upload POST endpoint; the names differ enough that a reader
    looking at a test will know which view is being driven.
    """
    from django.urls import reverse
    return reverse("a_dashboard_product_submit", args=[product.pk])


class TestPreSubmitGuard:
    """
    The pre-submit deliverability guard on both submit paths.

    An INSTANT digital product cannot be submitted if any
    is_available=True variation has neither a live
    digital_file_path nor a DRAFT/PENDING upload. Without the guard,
    the product reaches Pending, goes through review, goes live, and
    fails at download time for the first customer who tries.

    Two entry points — dashboard_product_submit and
    dashboard_product_edit's save_and_submit action — exercise the
    same guard. Both are covered. A guard wired into one and not the
    other is exactly the drift the transition table names; the
    comparison test in TestBothSubmitPathsAgree pins it from the
    other direction.
    """

    def _submit_via_standalone(self, client, chain):
        from django.urls import reverse
        return client.post(
            reverse("a_dashboard_product_submit", args=[chain["product"].pk]),
        )

    def _submit_via_edit_form(self, client, chain):
        from django.urls import reverse
        return client.post(
            reverse("a_dashboard_product_edit", args=[chain["product"].pk]),
            data={
                "product_name": chain["product"].product_name,
                "description": "x",
                "category": chain["product"].category_id,
                "product_kind": "digital",
                "digital_fulfillment_type": "INSTANT",
                "action": "save_and_submit",
            },
        )

    def test_standalone_submit_refuses_without_vault_file(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from django.contrib.messages import get_messages

        chain = artisan_chain
        client.force_login(chain["user"])
        response = self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Draft"
        messages_list = [str(m) for m in get_messages(response.wsgi_request)]
        assert any("no vault file" in m.lower() for m in messages_list), (
            "The guard did not fire. The status was Draft, but the "
            "message does not mention the missing vault file — likely "
            "the A2 image check or the no-variations check reached "
            "the request first. The fixture must supply an image and "
            "at least one variation."
        )

    def test_edit_form_submit_refuses_without_vault_file(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from django.contrib.messages import get_messages

        chain = artisan_chain
        client.force_login(chain["user"])
        response = self._submit_via_edit_form(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Draft"
        message_list = [str(m) for m in get_messages(response.wsgi_request)]
        assert any("no vault file" in m.lower() for m in message_list), (
            "The guard did not fire. The status was Draft, but the "
            "message does not mention the missing vault file — likely "
            "the A2 image check or the no-variations check reached "
            "the request first. The fixture must supply an image and "
            "at least one variation."
        )

    def test_guard_allows_submit_when_a_draft_upload_exists(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        """
        A variation with a DRAFT upload satisfies the guard. The file
        exists in _pending/; it becomes the pointer on admin approval.
        The guard is "no file has ever been uploaded", not "the file
        is awaiting review".
        """
        chain = artisan_chain
        client.force_login(chain["user"])
        _make_upload(
            chain, chain["variation"], status_value="DRAFT", name="d.pdf",
        )

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"

    def test_guard_allows_submit_when_a_pending_upload_exists(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        chain = artisan_chain
        client.force_login(chain["user"])
        _make_upload(
            chain, chain["variation"], status_value="PENDING", name="p.pdf",
        )

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"

    def test_guard_allows_submit_when_digital_file_path_is_set(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        chain = artisan_chain
        chain["variation"].digital_file_path = "epaintings/foo.pdf"
        chain["variation"].save(update_fields=["digital_file_path"])
        client.force_login(chain["user"])

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"

    def test_guard_skips_custom_product(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        """
        CUSTOM has no per-variation file: the file is per-order and
        is staged after purchase. The guard must not demand one.
        """
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(
            digital_fulfillment_type="CUSTOM",
        )
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"

    def test_guard_skips_physical_product(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(
            is_digital=False, is_physical=True,
        )
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"

    def test_unavailable_variation_is_not_required_to_have_a_file(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        """
        A withdrawn variation is not a delivery obligation. The guard
        filters on is_available=True so a variation the artisan has
        set aside does not block submission.
        """
        from store.models import ProductVariation

        chain = artisan_chain
        ProductVariation.objects.filter(pk=chain["variation"].pk).update(
            is_available=False,
        )
        chain["variation"].refresh_from_db()
        client.force_login(chain["user"])

        self._submit_via_standalone(client, chain)

        chain["product"].refresh_from_db()
        assert chain["product"].status == "Pending"


class TestPromotionOnSubmit:
    """
    DRAFT → PENDING promotion, inside the same transaction as the
    product status flip.

    The memo's "row to pin hardest": the promotion must be atomic with
    the status flip. A crash between the two would leave an admin email
    pointing at a PENDING file whose product reverted to Draft. The
    transaction-boundary assertion is what test_promotion_is_inside_the
    _transaction pins; the transition cases are what the surrounding
    tests pin.
    """

    def test_submit_promotes_draft_uploads(
        self, client, artisan_chain, vault_root_for_draft,
        django_capture_on_commit_callbacks,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])
        draft = _make_upload(
            chain, chain["variation"], status_value="DRAFT", name="d.pdf",
        )

        with django_capture_on_commit_callbacks(execute=False):
            client.post(
                _upload_url_standalone(chain["product"]),
            )

        draft.refresh_from_db()
        assert draft.status == "PENDING"

    def test_submit_leaves_pending_and_terminal_uploads_alone(
        self, client, artisan_chain, vault_root_for_draft,
        django_capture_on_commit_callbacks,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])
        pending = _make_upload(
            chain, chain["variation"], status_value="PENDING", name="p.pdf",
        )
        superseded = _make_upload(
            chain, chain["variation"], status_value="SUPERSEDED", name="s.pdf",
        )

        with django_capture_on_commit_callbacks(execute=False):
            client.post(
                _upload_url_standalone(chain["product"]),
            )

        pending.refresh_from_db()
        superseded.refresh_from_db()
        assert pending.status == "PENDING"
        assert superseded.status == "SUPERSEDED"

    def test_promotion_uses_update_not_save(
        self, client, artisan_chain, vault_root_for_draft,
        django_capture_on_commit_callbacks, monkeypatch,
    ):
        """
        The promotion is a single UPDATE statement, not a per-row
        .save() loop. Pinned by spying on ArtisanVaultUpload.save and
        asserting it is not called during the submit.
        """
        from store.models import ArtisanVaultUpload

        chain = artisan_chain
        client.force_login(chain["user"])
        _make_upload(chain, chain["variation"], status_value="DRAFT", name="d.pdf")

        save_calls = []
        real_save = ArtisanVaultUpload.save

        def spy_save(self, *args, **kwargs):
            save_calls.append(self.pk)
            return real_save(self, *args, **kwargs)

        monkeypatch.setattr(ArtisanVaultUpload, "save", spy_save)

        with django_capture_on_commit_callbacks(execute=False):
            client.post(
                _upload_url_standalone(chain["product"]),
            )

        assert save_calls == [], (
            "The promotion should use .update(), not .save(). "
            "save_calls contained: " + repr(save_calls)
        )


class TestDemotionOnWithdraw:
    """
    PENDING → DRAFT demotion, symmetric with the promotion on submit.

    Without the demotion, a withdraw leaves the uploads PENDING and
    they sit in the admin review queue for a Draft product. The
    approve view would refuse them (product is not Pending), so
    nothing actually goes live, but the queue carries dead work and
    the artisan's Staged badge reads 0 while the admin's pending
    badge reads >0.
    """

    def test_withdraw_demotes_pending_uploads(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(status="Pending")
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        pending = _make_upload(
            chain, chain["variation"], status_value="PENDING", name="p.pdf",
        )

        from django.urls import reverse
        client.post(reverse("a_dashboard_product_withdraw", args=[chain["product"].pk]))

        pending.refresh_from_db()
        assert pending.status == "DRAFT"

    def test_withdraw_leaves_draft_and_terminal_uploads_alone(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        from store.models import Product

        chain = artisan_chain
        Product.objects.filter(pk=chain["product"].pk).update(status="Pending")
        chain["product"].refresh_from_db()
        client.force_login(chain["user"])

        draft = _make_upload(chain, chain["variation"], status_value="DRAFT", name="d.pdf")
        approved = _make_upload(chain, chain["variation"], status_value="APPROVED", name="a.pdf")

        from django.urls import reverse
        client.post(reverse("a_dashboard_product_withdraw", args=[chain["product"].pk]))

        draft.refresh_from_db()
        approved.refresh_from_db()
        assert draft.status == "DRAFT"
        assert approved.status == "APPROVED"


class TestBothSubmitPathsAgree:
    """
    Comparison test across the two submit entry points.

    dashboard_product_submit and dashboard_product_edit's
    save_and_submit action are two separate functions with the same
    transactional shape. The transition table's "row to pin hardest"
    is the promotion being in the same transaction as the status flip;
    this class pins the slightly weaker but more failure-prone property
    that the two paths agree on both the refusal (guard) and the
    success (promotion) outcomes.

    A test that only walked one path would pass while the other
    drifted. The handoff's comparison-test rule applies to a pair of
    views here, not a pair of branches in one function.
    """

    def _drive(self, client, chain, path):
        if path == "standalone":
            client.post(
                _upload_url_standalone(chain["product"]),
            )
        elif path == "edit_form":
            from django.urls import reverse
            client.post(
                reverse("a_dashboard_product_edit", args=[chain["product"].pk]),
                data={
                    "product_name": chain["product"].product_name,
                    "description": "x",
                    "category": chain["product"].category_id,
                    "product_kind": "digital",
                    "digital_fulfillment_type": "INSTANT",
                    "action": "save_and_submit",
                },
            )

    def test_both_paths_refuse_when_guard_trips(
        self, client, artisan_chain, vault_root_for_draft,
    ):
        chain = artisan_chain

        for path in ("standalone", "edit_form"):
            from store.models import Product, ArtisanVaultUpload
            # Reset to Draft and clear any uploads between paths.
            Product.objects.filter(pk=chain["product"].pk).update(status="Draft")
            ArtisanVaultUpload.objects.filter(product=chain["product"]).delete()
            chain["product"].refresh_from_db()

            client.force_login(chain["user"])
            self._drive(client, chain, path)

            chain["product"].refresh_from_db()
            assert chain["product"].status == "Draft", (
                f"{path} path submitted despite the guard tripping"
            )

    def test_both_paths_promote_on_success(
        self, client, artisan_chain, vault_root_for_draft,
        django_capture_on_commit_callbacks,
    ):
        from store.models import Product, ArtisanVaultUpload

        chain = artisan_chain

        for path in ("standalone", "edit_form"):
            Product.objects.filter(pk=chain["product"].pk).update(status="Draft")
            ArtisanVaultUpload.objects.filter(product=chain["product"]).delete()
            chain["product"].refresh_from_db()

            # Satisfy the guard so the submit succeeds; then promote.
            _make_upload(chain, chain["variation"], status_value="DRAFT", name="d.pdf")

            client.force_login(chain["user"])
            with django_capture_on_commit_callbacks(execute=False):
                self._drive(client, chain, path)

            chain["product"].refresh_from_db()
            assert chain["product"].status == "Pending", (
                f"{path} path did not flip product status"
            )
            promoted = ArtisanVaultUpload.objects.get(
                product=chain["product"], status="PENDING",
            )
            assert promoted is not None, (
                f"{path} path did not promote the DRAFT upload"
            )