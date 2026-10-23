# creators/tests/test_artisan_orders_dashboard.py
"""
Tests for the artisan Orders dashboard.

Two behaviour contracts are pinned here:

  1. Pending lines are bucketed by product type. Only physical lines
     are dispatchable from this dashboard; CUSTOM digital lines need a
     different fulfilment path (admin-mediated delivery), and INSTANT
     digital lines auto-fulfil at payment time so the artisan has no
     action at all.

  2. dashboard_dispatch_line rejects non-physical lines. Previously the
     view accepted any OrderProduct owned by the artisan and wrote a
     TrackingNumber — which meant an artisan could mark an INSTANT
     digital line as dispatched, flipping is_dispatched without the
     customer ever receiving a download token.

Plus a small structural guard: creators.views must not re-define
artisan_dashboard_context. The sidebar's counters come from
creators.context; a local duplicate would silently drift.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone


@pytest.fixture
def artisan_orders_setup(db, django_user_model):
    """
    One verified artisan, one customer, one Order with three
    OrderProduct lines attributed to the artisan:

      * physical          — dispatchable via tracking-number form
      * CUSTOM digital    — file produced by artisan, delivered via admin
      * INSTANT digital   — auto-fulfilled at payment; no artisan action

    Each line is deliberately is_dispatched=False, matching the shape
    that would result if a mixed-cart checkout settled and the artisan
    then opened their Orders tab.
    """
    from category.models import Category
    from creators.models import CreatorProfile
    from store.models import Product, ProductVariation
    from orders.models import Order, OrderProduct

    artisan_user = django_user_model.objects.create_user(
        username="artisan_ord",
        email="artisan-ord@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Orders Artisan",
        slug="orders-artisan",
        is_verified=True,
    )
    customer = django_user_model.objects.create_user(
        username="ord_customer",
        email="ord-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )

    cat_physical = Category.objects.create(
        category_name="Physical Cat",
        slug="physical-cat",
        product_format="physical",
    )
    cat_digital = Category.objects.create(
        category_name="Digital Cat",
        slug="digital-cat",
        product_format="e-product",
    )

    physical_product = Product.objects.create(
        product_name="Physical Item",
        category=cat_physical,
        creator=profile,
        is_physical=True,
        is_digital=False,
        is_active=True,
        status="Published",
    )
    physical_variation = ProductVariation.objects.create(
        product=physical_product,
        price=Decimal("10.00"),
        stock=10,
        is_available=True,
    )

    custom_product = Product.objects.create(
        product_name="Custom Digital",
        category=cat_digital,
        creator=profile,
        is_physical=False,
        is_digital=True,
        digital_fulfillment_type="CUSTOM",
        is_active=True,
        status="Published",
    )
    custom_variation = ProductVariation.objects.create(
        product=custom_product,
        price=Decimal("20.00"),
        stock=1,
        is_available=True,
    )

    instant_product = Product.objects.create(
        product_name="Instant Digital",
        category=cat_digital,
        creator=profile,
        is_physical=False,
        is_digital=True,
        digital_fulfillment_type="INSTANT",
        is_active=True,
        status="Published",
    )
    instant_variation = ProductVariation.objects.create(
        product=instant_product,
        price=Decimal("30.00"),
        stock=1,
        is_available=True,
    )

    order = Order.objects.create(
        user=customer,
        order_number="ORD-ARTISAN-0001",
        email=customer.email,
        is_ordered=True,
        order_status="Processing",
    )

    physical_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=physical_product,
        product_variation=physical_variation,
        product_price=Decimal("10.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )
    custom_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=custom_product,
        product_variation=custom_variation,
        product_price=Decimal("20.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )
    instant_line = OrderProduct.objects.create(
        order=order,
        user=customer,
        product=instant_product,
        product_variation=instant_variation,
        product_price=Decimal("30.00"),
        quantity=1,
        ordered=True,
        fulfilled_by=profile,
        fulfillment_started_at=timezone.now(),
    )

    return {
        "artisan_user": artisan_user,
        "profile": profile,
        "customer": customer,
        "order": order,
        "physical_line": physical_line,
        "custom_line": custom_line,
        "instant_line": instant_line,
    }


class TestPendingBuckets:

    def test_physical_line_is_in_pending_physical(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        ids = {line.id for line in response.context["pending_physical"]}
        assert chain["physical_line"].id in ids

    def test_custom_digital_line_is_in_pending_custom_digital(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        ids = {line.id for line in response.context["pending_custom_digital"]}
        assert chain["custom_line"].id in ids

    def test_instant_digital_line_is_in_neither_pending_bucket(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200

        physical_ids = {line.id for line in response.context["pending_physical"]}
        custom_ids = {line.id for line in response.context["pending_custom_digital"]}

        assert chain["instant_line"].id not in physical_ids
        assert chain["instant_line"].id not in custom_ids


class TestDispatchLineGuard:

    def test_physical_line_dispatch_still_works(
        self, client, artisan_orders_setup,
    ):
        """
        Regression guard: the guard added for digital lines must not
        break the physical-line flow.
        """
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["physical_line"]
        assert line.is_dispatched is False

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SF-12345", "carrier": "SF Express"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is True
        assert line.dispatched_at is not None
        assert TrackingNumber.objects.filter(
            order_product=line, tracking_code="SF-12345",
        ).exists()

    def test_custom_digital_line_dispatch_is_rejected(
        self, client, artisan_orders_setup,
    ):
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["custom_line"]

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SHOULD-NOT", "carrier": "X"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is False
        assert line.dispatched_at is None
        assert not TrackingNumber.objects.filter(order_product=line).exists()

    def test_instant_digital_line_dispatch_is_rejected(
        self, client, artisan_orders_setup,
    ):
        from orders.models import TrackingNumber

        chain = artisan_orders_setup
        line = chain["instant_line"]

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_dispatch_line", args=[line.id])
        response = client.post(
            url, {"tracking_code": "SHOULD-NOT", "carrier": "X"},
        )
        assert response.status_code == 200

        line.refresh_from_db()
        assert line.is_dispatched is False
        assert not TrackingNumber.objects.filter(order_product=line).exists()


class TestContextConsolidation:
    """
    Structural guards: the shared context builder lives in
    creators.context, and the sidebar count reflects only actionable
    lines (physical + custom digital), not every undispatched line.
    """

    def test_no_local_artisan_dashboard_context_in_views(self):
        from creators import views

        assert not hasattr(views, "_artisan_dashboard_context"), (
            "Duplicate _artisan_dashboard_context found in creators.views. "
            "Use creators.context.artisan_dashboard_context instead."
        )

    def test_sidebar_count_reflects_only_actionable_lines(
        self, rf, artisan_orders_setup,
    ):
        from creators.context import artisan_dashboard_context

        chain = artisan_orders_setup
        request = rf.get("/")
        request.user = chain["artisan_user"]

        ctx = artisan_dashboard_context(request)
        # physical + custom digital = 2; INSTANT digital is excluded.
        assert ctx["pending_dispatch_count"] == 2
        assert ctx["unread_messages_count"] == 0
        assert ctx["profile"] == chain["profile"]


class TestOrdersPanelTemplate:
    """
    The template must reflect the view's bucket split. Before commit 2
    it still iterated the old `pending_lines` context key, which the
    view no longer provides, so the pending tab rendered empty even
    when actionable lines existed.
    """

    def _get_panel_html(self, client, chain):
        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200
        return response.content.decode()

    def test_physical_line_renders_tracking_form(
        self, client, artisan_orders_setup,
    ):
        html = self._get_panel_html(client, artisan_orders_setup)
        assert 'name="tracking_code"' in html

    def test_custom_digital_line_renders_upload_button(
        self, client, artisan_orders_setup,
    ):
        """
        The custom-digital card must open the order-product-scoped
        vault upload modal, not the 2026-10-14 product-edit stopgap.

        Both halves matter: the new hx-get must be present, and the
        old product-edit link must be absent. A future regression that
        reintroduces the stopgap link (perhaps by "simplifying" the
        partial back to its pre-2026-10-22 shape) fails the second
        assertion even if someone leaves the new button in place too.
        """
        chain = artisan_orders_setup
        html = self._get_panel_html(client, chain)

        new_url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["custom_line"].id],
        )
        assert f'hx-get="{new_url}"' in html

        # Absence assertion: the old product-edit link (with the
        # product's id, not the order-product's id) must not be the
        # custom card's action. Scoped to the pending panel so the
        # "no product-edit link at all" reading isn't misleading —
        # other parts of the page may legitimately link there.
        start = html.find('data-panel="pending"')
        end = html.find('data-panel="dispatched"', start)
        pending_html = html[start:end]
        old_url = reverse(
            "a_dashboard_product_edit",
            args=[chain["custom_line"].product.id],
        )
        assert old_url not in pending_html, (
            "The custom-digital card still links to the product-edit "
            "stopgap. It should open the order-product-scoped upload "
            "modal instead."
        )

    def test_custom_digital_line_renders_disclosure_line(
        self, client, artisan_orders_setup,
    ):
        """
        The 2026-10-21 Q1 decision requires an artisan-side disclosure
        that this line cannot be self-cancelled by the customer. The
        copy decision (2026-10-22) is the (b) shorter phrasing; the
        full policy text is not duplicated here.
        """
        html = self._get_panel_html(client, artisan_orders_setup)
        assert "cannot be self-cancelled by the customer" in html
        assert "此訂單顧客無法自行取消" in html

    def test_custom_digital_line_does_not_render_tracking_form(
        self, client, artisan_orders_setup,
    ):
        """
        Scope the assertion to the pending panel: the physical line
        renders a tracking form in the same page, so a naive "no
        tracking_code input exists" check would be wrong. Slice the
        pending panel between its data-panel marker and the next one.
        """
        html = self._get_panel_html(client, artisan_orders_setup)
        start = html.find('data-panel="pending"')
        assert start != -1, "pending tab panel marker missing"
        end = html.find('data-panel="dispatched"', start)
        assert end != -1, "dispatched tab panel marker missing"
        pending_html = html[start:end]

        assert pending_html.count('name="tracking_code"') == 1, (
            "Exactly one tracking form should render in pending — the "
            "physical line's. A second means the custom-digital card "
            "regressed to the old unconditional form."
        )

    def test_instant_digital_line_absent_from_response(
        self, client, artisan_orders_setup,
    ):
        chain = artisan_orders_setup
        html = self._get_panel_html(client, chain)
        # The INSTANT line has never been dispatched and is excluded
        # from every panel, so its product name should not appear.
        assert chain["instant_line"].product.product_name not in html


class TestOrderProductVaultUploadView:
    """
    The order-product-scoped vault upload view. See the 2026-10-22
    commit "store: close the artisan-side CUSTOM pipeline".

    Two contracts:
      1. GET renders the shared form with an hx-post pointing at this
         line's upload endpoint, targeting the orders-dashboard modal.
      2. POST creates an ArtisanVaultUpload scoped to the order-product,
         and supersession targets by order-product — not by variation.
         The second half is what distinguishes the CUSTOM path from the
         INSTANT path; the helper's branch exists precisely to prevent
         cross-line supersession.
    """

    @pytest.fixture
    def vault_root(self, settings, tmp_path):
        settings.XINDENG_VAULT_ROOT = tmp_path
        (tmp_path / "_pending").mkdir()
        return tmp_path

    def test_get_returns_form_with_order_product_post_url(
        self, client, artisan_orders_setup, vault_root,
    ):
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["custom_line"].id],
        )
        response = client.get(url)
        assert response.status_code == 200

        body = response.content.decode()
        assert f'hx-post="{url}"' in body
        # The order-product view's modal target, not the variation-page
        # default. If the view forgot to pass upload_target, the form
        # would carry the variation default and fail this assertion.
        assert 'hx-target="#order-product-vault-upload-modal-body"' in body

    def test_get_404s_for_non_custom_line(
        self, client, artisan_orders_setup, vault_root,
    ):
        """Forged-GET guard: a physical line's id is not a valid target."""
        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])
        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["physical_line"].id],
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_get_404s_for_another_artisans_line(
        self, client, artisan_orders_setup, vault_root, django_user_model,
    ):
        """Ownership guard: fulfilled_by must match the logged-in artisan."""
        from creators.models import CreatorProfile

        chain = artisan_orders_setup

        other_user = django_user_model.objects.create_user(
            username="other_artisan",
            email="other-artisan@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        CreatorProfile.objects.create(
            user=other_user,
            display_name="Other Artisan",
            slug="other-artisan",
            is_verified=True,
        )

        client.force_login(other_user)
        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["custom_line"].id],
        )
        response = client.get(url)
        assert response.status_code == 404

    def test_post_creates_order_product_scoped_upload(
        self, client, artisan_orders_setup, vault_root,
    ):
        from store.models import ArtisanVaultUpload
        from django.core.files.uploadedfile import SimpleUploadedFile

        chain = artisan_orders_setup
        client.force_login(chain["artisan_user"])

        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["custom_line"].id],
        )
        upload = SimpleUploadedFile(
            "art.pdf", b"%PDF-1.4 test", "application/pdf",
        )
        response = client.post(url, {
            "upload_type": "DIRECT",
            "file": upload,
        })
        assert response.status_code == 200

        row = ArtisanVaultUpload.objects.get(
            order_product=chain["custom_line"], status="PENDING",
        )
        assert row.variation_id == chain["custom_line"].product_variation_id
        assert row.product_id == chain["custom_line"].product_id
        assert row.staged_filename
        assert (vault_root / "_pending" / row.staged_filename).exists()

    def test_reupload_supersedes_by_order_product_not_variation(
        self, client, artisan_orders_setup, vault_root,
    ):
        """
        The load-bearing test. Two CUSTOM lines on the same variation.
        Uploading on line A must not supersede line B's PENDING upload.

        A shape-only test (assert PENDING row exists after re-upload)
        would pass with a variation-keyed filter — the supersession
        would have hit the wrong row but a PENDING row would still
        exist. The comparison against line B's row is what catches the
        bug the helper's branch exists to prevent.
        """
        from store.models import ArtisanVaultUpload
        from orders.models import OrderProduct
        from django.core.files.uploadedfile import SimpleUploadedFile

        chain = artisan_orders_setup
        custom_line = chain["custom_line"]
        client.force_login(chain["artisan_user"])

        # Line B: same order, same product, same variation, own row.
        line_b = OrderProduct.objects.create(
            order=custom_line.order,
            user=custom_line.user,
            product=custom_line.product,
            product_variation=custom_line.product_variation,
            product_price=custom_line.product_price,
            quantity=1,
            ordered=True,
            fulfilled_by=custom_line.fulfilled_by,
            fulfillment_started_at=timezone.now(),
        )

        url_a = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[custom_line.id],
        )
        url_b = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[line_b.id],
        )

        # First upload on A.
        client.post(url_a, {
            "upload_type": "DIRECT",
            "file": SimpleUploadedFile("a1.pdf", b"%PDF-1.4 a1", "application/pdf"),
        })
        pending_a1 = ArtisanVaultUpload.objects.get(
            order_product=custom_line, status="PENDING",
        )

        # Upload on B.
        client.post(url_b, {
            "upload_type": "DIRECT",
            "file": SimpleUploadedFile("b1.pdf", b"%PDF-1.4 b1", "application/pdf"),
        })
        pending_b = ArtisanVaultUpload.objects.get(
            order_product=line_b, status="PENDING",
        )

        # Re-upload on A: supersedes A's PENDING, not B's.
        client.post(url_a, {
            "upload_type": "DIRECT",
            "file": SimpleUploadedFile("a2.pdf", b"%PDF-1.4 a2", "application/pdf"),
        })

        pending_a1.refresh_from_db()
        pending_b.refresh_from_db()
        assert pending_a1.status == "SUPERSEDED"
        assert pending_b.status == "PENDING", (
            "Re-upload on line A superseded line B's pending upload. "
            "The helper's supersession filter is keying on variation "
            "rather than order_product — a silent data bug."
        )

        new_pending_a = ArtisanVaultUpload.objects.get(
            order_product=custom_line, status="PENDING",
        )
        assert new_pending_a.pk != pending_a1.pk


class TestPendingCustomDigitalRejectionState:
    """
    The artisan's per-line upload card must distinguish four states:
    no upload / pending / rejected / approved. The rejection state
    renders the reviewer's note so the artisan knows why they need
    to re-upload; the approved state hides the upload action because
    the file has already been served to the customer.
    """

    def _custom_line_html(self, client, chain):
        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_orders"))
        assert response.status_code == 200
        html = response.content.decode()
        start = html.find('data-panel="pending"')
        end = html.find('data-panel="dispatched"', start)
        return html[start:end]

    def test_rejection_renders_review_note(
        self, client, artisan_orders_setup,
    ):
        from store.models import ArtisanVaultUpload

        chain = artisan_orders_setup
        ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["custom_line"].product,
            variation=chain["custom_line"].product_variation,
            order_product=chain["custom_line"],
            status="REJECTED",
            storage_kind="LOCAL",
            staged_filename="x.pdf",
            original_filename="x.pdf",
            file_size=10, checksum="a" * 64,
            review_note="File is blurry — please rescan at 300dpi.",
        )
        html = self._custom_line_html(client, chain)
        assert "Rejected｜已拒絕" in html
        assert "File is blurry — please rescan at 300dpi." in html

    def test_approved_state_hides_upload_action(
        self, client, artisan_orders_setup,
    ):
        from store.models import ArtisanVaultUpload
        from django.utils import timezone as tz

        chain = artisan_orders_setup
        ArtisanVaultUpload.objects.create(
            artisan=chain["profile"],
            product=chain["custom_line"].product,
            variation=chain["custom_line"].product_variation,
            order_product=chain["custom_line"],
            status="APPROVED",
            storage_kind="LOCAL",
            staged_filename="x.pdf",
            original_filename="x.pdf",
            file_size=10, checksum="a" * 64,
            reviewed_at=tz.now(),
        )
        html = self._custom_line_html(client, chain)
        assert "已交付｜Delivered" in html
        # The upload endpoint URL must NOT appear as an hx-get in this
        # line's card. The pending and the initial states both render
        # an hx-get; only the approved state does not.
        url = reverse(
            "a_dashboard_order_product_upload_vault",
            args=[chain["custom_line"].id],
        )
        assert f'hx-get="{url}"' not in html


class TestDispatchedAndDeliveredTabs:
    """
    Both tabs must show enough information for the artisan to identify
    the order and the line without switching to the member side. The
    pre-change templates rendered only the product name and (for
    dispatched) the date.
    """

    def _panel_slice(self, html, start_marker, end_marker):
        start = html.find(start_marker)
        end = html.find(end_marker, start)
        assert start != -1 and end != -1
        return html[start:end]

    def test_delivered_tab_shows_order_number_and_sku(
        self, client, artisan_orders_setup, django_user_model,
    ):
        """
        A minimal delivered order — one line, dispatched, order status
        'Delivered'. The mixed-cart fixture cannot reach 'Delivered'
        because the physical and instant lines are undispatched, and
        the post_save signal correctly recomputes to 'Partly_Dispatched'
        on any line save. Trying to fight the signal is a fixture
        defect, not a view defect.
        """
        from orders.models import Order, OrderProduct

        chain = artisan_orders_setup
        customer = chain["customer"]
        profile = chain["profile"]
        product = chain["custom_line"].product
        variation = chain["custom_line"].product_variation

        delivered_order = Order.objects.create(
            user=customer,
            order_number="ORD-ARTISAN-DELIVERED",
            email=customer.email,
            is_ordered=True,
            order_status="Delivered",
        )
        delivered_line = OrderProduct.objects.create(
            order=delivered_order,
            user=customer,
            product=product,
            product_variation=variation,
            product_price=Decimal("20.00"),
            quantity=1,
            ordered=True,
            fulfilled_by=profile,
            fulfillment_started_at=timezone.now(),
            is_dispatched=True,
            dispatched_at=timezone.now(),
        )

        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_orders"))
        html = response.content.decode()
        tail = html[html.find('data-panel="delivered"'):]

        assert delivered_order.order_number in tail
        assert variation.get_sku() in tail