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

