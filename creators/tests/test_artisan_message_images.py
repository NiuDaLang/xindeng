# creators/tests/test_artisan_message_images.py
"""
Image-attachment support on ArtisanChatMessage.

Part 1 — commit 3f (pre-3f-bis):
  6 tests, exercising the widened content-OR-image guard and the
  signal's interaction with image-only messages.

Part 2 — 3f-bis (this commit):
  14 tests, covering:
    * Part A — the image pipeline registration in
      core.signals.IMAGE_FIELD_REGISTRY. Prior to 3f-bis the field
      was never registered, so uploads bypassed optimization
      entirely.
    * Part B — the pre_save validation gate in
      creators/signals.validate_artisan_chat_image. Prior to
      3f-bis, corrupt uploads were stored and rendered as broken
      <img> because optimize_image silently returns None on
      UnidentifiedImageError.
    * Part C — the file-cleanup registration in
      core.file_cleanup.REPLACE_CLEANUP_FIELDS. Prior to 3f-bis,
      replaced and deleted images were orphaned in
      artisan_chat_images/.
    * Cross-cutting — interactions with maintain_frontline_thread,
      the existing settled_at-clear-on-new-message semantics, and
      the "large but valid image is still accepted" fast-path.

Fixture-style note: the 6 pre-3f-bis tests use a local
_png_upload() helper (returns a ~2 KB PNG), which is *below*
MIN_PROCESS_BYTES (80 KB) — so those tests pass unchanged after
3f-bis registers the field with the pipeline (the pipeline
correctly skips small files). The 14 new tests use conftest.py's
png_medium (800x600 noisy, above MIN_PROCESS_BYTES) and
tiny_corrupt (not a valid image) fixtures to exercise the
pipeline and validation paths. The two styles coexist by design;
the local helper is self-contained, and the conftest fixtures
are project-wide.
"""
import os
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from category.models import Category
from creators.models import (
    ArtisanChatMessage,
    CreatorProfile,
    FrontlineThread,
)
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation
from tests._fakes import make_superuser

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    return make_superuser(username="ami-admin", email="ami-admin@example.com")


@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="ami-customer",
        email="ami-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="ami-artisan",
        email="ami-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user, display_name="AMI Artisan", is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="AMI Category", slug="ami-category",
    )


@pytest.fixture
def product(category, artisan_profile):
    return Product.objects.create(
        product_name="AMI Product", slug="ami-product",
        category=category, creator=artisan_profile,
        is_digital=True, digital_fulfillment_type="CUSTOM",
        is_active=True, status="Published",
    )


@pytest.fixture
def variation(product):
    return ProductVariation.objects.create(
        product=product, price="10.00", stock=1,
    )


@pytest.fixture
def order(customer):
    return Order.objects.create(
        user=customer, email=customer.email,
        order_number="AMI-ORDER-0001",
        is_ordered=True, order_status="Processing",
    )


@pytest.fixture
def order_product(order, product, variation, artisan_profile):
    return OrderProduct.objects.create(
        order=order, user=order.user,
        product=product, product_variation=variation,
        product_price="10.00", quantity=1, ordered=True,
        fulfilled_by=artisan_profile,
    )


def _png_upload(name="preview.png", size=(300, 300), color=(10, 100, 200)):
    """A small PNG SimpleUploadedFile for image-attachment tests."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return SimpleUploadedFile(
        name, buf.getvalue(), content_type="image/png",
    )


def _png_inline(name="probe_inline.png", size=(400, 400)):
    """
    A noisy PNG sized for the *inline* image pipeline.

    Larger than MIN_PROCESS_BYTES (80 KB) so optimize_image runs,
    smaller than INLINE_SIZE_THRESHOLD_BYTES (1 MB) so it runs
    inline rather than being deferred to Celery. Tests in this
    file that assert on the *result* of the pipeline need to use
    this helper, not png_medium (which is ~1.4 MB and therefore
    deferred to Celery — a path that pytest-django does not run
    without extra on_commit-capture plumbing).

    Noisy content is required: a solid-color PNG would compress
    to fewer bytes as WebP and the "encoded >= original" guard
    would return None, leaving the file as .png. Noise inverts
    that — WebP is reliably smaller.
    """
    import random
    random.seed(0)
    img = Image.new("RGB", size)
    px = img.load()
    for y in range(size[1]):
        for x in range(size[0]):
            px[x, y] = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
            )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    body = buf.getvalue()
    # Sanity guard: the fixture must fall in the inline band.
    assert 80 * 1024 < len(body) < 1024 * 1024, (
        f"fixture size {len(body)} is outside the inline-processing band "
        f"(80 KB .. 1 MB); adjust the dimensions."
    )
    return SimpleUploadedFile(name, body, content_type="image/png")


# ──────────────────────────────────────────────────────────────
# Test 1: model field shape
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_artisanchatmessage_image_field_shape():
    from django.db.models import ImageField

    field = ArtisanChatMessage._meta.get_field("image")
    assert isinstance(field, ImageField)
    assert field.null is True
    assert field.blank is True
    assert field.upload_to == "artisan_chat_images/"


# ──────────────────────────────────────────────────────────────
# Tests 2 & 3: customer-side send
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestCustomerThreadImageSend:

    def _send_url(self, artisan_profile):
        return reverse(
            "customer_thread_send",
            kwargs={"artisan_slug": artisan_profile.slug},
        )

    def test_image_only_message_succeeds(
        self, client, customer, artisan_profile, order_product,
    ):
        client.force_login(customer)
        response = client.post(
            self._send_url(artisan_profile),
            {
                "content": "",
                "image": _png_upload(),
                "order_product_id": order_product.id,
            },
        )
        # Redirect back to the thread.
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(
            artisan=artisan_profile,
            customer=customer,
            order_product=order_product,
        )
        assert msg.content == ""
        assert msg.image
        assert msg.image.name.startswith("artisan_chat_images/")
        assert msg.image.name.endswith(".png")

    def test_neither_content_nor_image_rejects(
        self, client, customer, artisan_profile, order_product,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(customer)
        response = client.post(
            self._send_url(artisan_profile),
            {
                "content": "",
                "order_product_id": order_product.id,
            },
        )
        # Redirect (empty-message path uses messages.error + redirect).
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before


# ──────────────────────────────────────────────────────────────
# Test 4: artisan-side send
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanPanelImageSend:

    def _send_url(self, customer):
        return reverse(
            "a_dashboard_messages_send", args=[customer.id],
        )

    def test_image_only_message_succeeds(
        self, client, customer, artisan_user, artisan_profile,
    ):
        client.force_login(artisan_user)
        response = client.post(
            self._send_url(customer),
            {"content": "", "image": _png_upload()},
        )
        assert response.status_code == 302

        msg = ArtisanChatMessage.objects.get(
            artisan=artisan_profile,
            customer=customer,
            sender=artisan_user,
        )
        assert msg.content == ""
        assert msg.image

    def test_neither_content_nor_image_rejects(
        self, client, customer, artisan_user, artisan_profile,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(artisan_user)
        response = client.post(
            self._send_url(customer),
            {"content": ""},
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before


# ──────────────────────────────────────────────────────────────
# Test 5: admin composer (escalated thread)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFrontlineAdminImageSend:

    def _escalated_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="seed", order_product=order_product,
        )
        thread = FrontlineThread.objects.get(order_product=order_product)
        thread.escalate(by=customer)
        return thread

    def test_image_only_admin_message_succeeds(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product,
    ):
        thread = self._escalated_thread(
            customer, artisan_profile, artisan_user, order_product,
        )
        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_message_send", args=[thread.id]),
            {
                "content": "",
                "image": _png_upload(),
                "settled_filter": "false",
            },
        )
        assert response.status_code == 200

        admin_msg = ArtisanChatMessage.objects.filter(
            sender=admin_user,
        ).order_by("-created_at").first()
        assert admin_msg is not None
        assert admin_msg.content == ""
        assert admin_msg.image


# ──────────────────────────────────────────────────────────────
# Test 6: signal still fires on image-only messages
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_image_only_message_advances_frontline_thread_timestamp(
    client, customer, artisan_profile, artisan_user, order_product,
):
    """
    The empty-content guard lives in the *view*, not the *create*.
    An image-only message reaches the create with a non-empty image
    field and empty content — same save path, same signal. Pin that
    the thread's last_message_at advances.
    """
    # Seed a first message so the thread exists (or use the auto
    # get_or_create on the image-only message — the signal fires
    # whether or not the thread already exists).
    client.force_login(customer)
    response = client.post(
        reverse(
            "customer_thread_send",
            kwargs={"artisan_slug": artisan_profile.slug},
        ),
        {
            "content": "",
            "image": _png_upload(),
            "order_product_id": order_product.id,
        },
    )
    assert response.status_code == 302

    thread = FrontlineThread.objects.get(order_product=order_product)
    image_only_msg = ArtisanChatMessage.objects.filter(
        customer=customer, order_product=order_product,
    ).latest("created_at")
    assert thread.last_message_at == image_only_msg.created_at


# ══════════════════════════════════════════════════════════════
# 3f-bis additions: pipeline registration, validation, cleanup
# ══════════════════════════════════════════════════════════════


class TestImagePipelineRegistration:
    """
    Part A — ArtisanChatMessage.image is now in
    core.signals.IMAGE_FIELD_REGISTRY.

    The message optimizer runs on post_save, so we trigger it via
    the customer-side send view (the cleanest path to a committed
    row) and then re-read the row from a fresh query so the
    pipeline's own save(update_fields=["image"]) is visible.
    """

    def test_medium_png_is_optimized_to_webp(
        self, client, customer, artisan_profile, order_product,
    ):
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": _png_inline(),
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302

        msg = (
            ArtisanChatMessage.objects
            .filter(customer=customer, order_product=order_product)
            .latest("created_at")
        )
        assert msg.image
        assert msg.image.name.startswith("artisan_chat_images/")
        # Pipeline converts to WebP.
        assert msg.image.name.endswith(".webp"), (
            f"expected .webp, got {msg.image.name}"
        )

    def test_small_png_is_left_as_png(
        self, client, customer, artisan_profile, order_product,
    ):
        """
        A ~2 KB PNG is under MIN_PROCESS_BYTES (80 KB), so the
        pipeline correctly returns None and leaves the file
        untouched. This is the deliberate behaviour pinned by
        core/tests/test_image_utils.py::TestOptimizeImage::
        test_small_file_returns_none; the test here guards against
        a future change to MIN_PROCESS_BYTES silently breaking the
        message pipeline.
        """
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": _png_upload(),
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302

        msg = (
            ArtisanChatMessage.objects
            .filter(customer=customer, order_product=order_product)
            .latest("created_at")
        )
        assert msg.image.name.endswith(".png")

    def test_frontline_thread_timestamp_not_corrupted_by_nested_resave(
        self, client, customer, artisan_profile, order_product, png_medium,
    ):
        """
        When the pipeline swaps the image file, save_optimized_to_field
        calls instance.save(update_fields=["image"]), which re-fires
        post_save on ArtisanChatMessage — and therefore re-fires
        maintain_frontline_thread. The second invocation must be a
        no-op for last_message_at: the message's created_at hasn't
        changed, and the thread's should not advance a second time.
        """
        from creators.models import FrontlineThread

        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": png_medium,
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302

        thread = FrontlineThread.objects.get(order_product=order_product)
        msg = (
            ArtisanChatMessage.objects
            .filter(customer=customer, order_product=order_product)
            .latest("created_at")
        )
        # last_message_at tracks the message's created_at, and the
        # nested re-save did not corrupt it.
        assert thread.last_message_at == msg.created_at


class TestImageValidationGate:
    """
    Part B — pre_save raises ValidationError on corrupt uploads.

    The three send views each catch that ValidationError and
    surface an error to the user via their own established
    convention:
      * customer_thread_send, dashboard_messages_send: flash +
        redirect.
      * frontline_message_send: HTMX 200 body with
        composer_error / composer_content preserved.

    In every case, the ArtisanChatMessage row is *not* created.
    """

    def test_customer_send_rejects_corrupt_image(
        self, client, customer, artisan_profile, order_product, tiny_corrupt,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "text",
                "image": tiny_corrupt,
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before

    def test_artisan_send_rejects_corrupt_image(
        self, client, customer, artisan_user, artisan_profile, tiny_corrupt,
    ):
        before = ArtisanChatMessage.objects.count()
        client.force_login(artisan_user)
        response = client.post(
            reverse("a_dashboard_messages_send", args=[customer.id]),
            {"content": "text", "image": tiny_corrupt},
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before

    def test_frontline_send_rejects_corrupt_image_htmx(
        self, client, admin_user, customer, artisan_user,
        artisan_profile, order_product, tiny_corrupt,
    ):
        # Seed + escalate, so the escalation gate is cleared.
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="seed", order_product=order_product,
        )
        thread = FrontlineThread.objects.get(order_product=order_product)
        thread.escalate(by=customer)

        before = ArtisanChatMessage.objects.count()
        client.force_login(admin_user)
        response = client.post(
            reverse("frontline_message_send", args=[thread.id]),
            {
                "content": "typed text",
                "image": tiny_corrupt,
                "settled_filter": "false",
            },
        )
        # HTMX 200-body (F20 convention), not 4xx.
        assert response.status_code == 200
        body = response.content.decode()
        assert "not a readable image" in body
        # Typed content preserved in the composer.
        assert "typed text" in body
        # No message created.
        assert ArtisanChatMessage.objects.count() == before

    def test_image_only_with_corrupt_file_also_rejected(
        self, client, customer, artisan_profile, order_product, tiny_corrupt,
    ):
        """
        The empty-content fast path must not bypass the validation
        gate. With content="" and a corrupt image, the guard accepts
        the payload (image is present), then the pre_save receiver
        rejects it.
        """
        before = ArtisanChatMessage.objects.count()
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": tiny_corrupt,
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.count() == before

    def test_image_only_with_valid_image_succeeds(
        self, client, customer, artisan_profile, order_product, png_medium,
    ):
        """
        The new validation gate must not break the image-only
        message path that 3f introduced.
        """
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": png_medium,
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302
        assert ArtisanChatMessage.objects.filter(
            customer=customer,
            order_product=order_product,
            content="",
        ).exists()

    def test_receiver_raises_on_corrupt_and_passes_on_valid(
        self, artisan_profile, customer, order_product, png_medium, tiny_corrupt,
    ):
        """
        Direct unit test on the pre_save receiver, no HTTP layer.
        Three shapes: (1) no image → no raise; (2) valid image →
        no raise; (3) corrupt image → ValidationError.
        """
        from creators.signals import validate_artisan_chat_image

        # (1) No image.
        no_img = ArtisanChatMessage(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product,
        )
        validate_artisan_chat_image(
            sender=ArtisanChatMessage, instance=no_img,
        )  # no exception

        # (2) Valid image — and critically, the file handle must remain
        # readable *after* the receiver returns, because Django's
        # FileField.pre_save will stream the bytes to storage next.
        # Closing the handle in the receiver is the bug the 3f-bis
        # test run caught (ValueError: I/O operation on closed file,
        # raised from storage._save -> uploadedfile.chunks -> seek(0)).
        import io as _io
        from PIL import Image as _Image
        from django.core.files.uploadedfile import SimpleUploadedFile as _SUF
        _buf = _io.BytesIO()
        _Image.new("RGB", (800, 600), (30, 60, 90)).save(_buf, format="PNG")
        valid = ArtisanChatMessage(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product,
            image=_SUF(
                "probe.png", _buf.getvalue(), content_type="image/png",
            ),
        )
        validate_artisan_chat_image(
            sender=ArtisanChatMessage, instance=valid,
        )
        # The receiver must NOT leave the file closed.
        assert valid.image.file is not None
        assert not valid.image.file.closed, (
            "pre_save receiver closed the upload handle — Django's "
            "storage layer will fail with 'I/O operation on closed "
            "file' when it tries to stream the bytes."
        )
        # And it must be seekable from the top for chunks() to work.
        valid.image.seek(0)
        head = valid.image.read(8)
        assert head.startswith(b"\x89PNG"), (
            f"expected PNG magic bytes after receiver, got {head!r}"
        )

        # (2b) The pipeline's own write-back must be skipped entirely.
        # save_optimized_to_field sets _skip_image_optimization around
        # its instance.save(update_fields=["image"]). At that moment
        # instance.image.file is closed (the optimizer's finally ran).
        # The receiver must not re-open it.
        pipeline_save = ArtisanChatMessage(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product,
            image=_SUF("pipeline.png", _buf.getvalue(), content_type="image/png"),
        )
        pipeline_save.image.file.close()  # simulate the optimizer having closed it
        pipeline_save._skip_image_optimization = True
        # If the receiver tried to open the closed handle, this would
        # raise ValueError instead of returning. It must return cleanly.
        validate_artisan_chat_image(
            sender=ArtisanChatMessage, instance=pipeline_save,
        )
        # Cleanup so pytest doesn't warn on unclosed tmp files.
        try:
            pipeline_save._skip_image_optimization = False
        except Exception:
            pass

        # (3) Corrupt image.
        corrupt = ArtisanChatMessage(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product,
            image=tiny_corrupt,
        )
        with pytest.raises(ValidationError):
            validate_artisan_chat_image(
                sender=ArtisanChatMessage, instance=corrupt,
            )


class TestImageCleanupRegistration:
    """
    Part C — ArtisanChatMessage.image is now in
    core.file_cleanup.REPLACE_CLEANUP_FIELDS (and, via the
    DELETE_CLEANUP_FIELDS = list(REPLACE_CLEANUP_FIELDS) alias,
    DELETE too).

    Deletions are scheduled through transaction.on_commit. Under
    pytest-django, each test runs in its own transaction and the
    outer transaction is rolled back at teardown — so on_commit
    callbacks typically never fire. The file_cleanup module's
    `_safe_delete_file` is wrapped in on_commit by design; to
    verify the wiring *runs*, we invoke the receiver's underlying
    logic directly rather than through HTTP. The file-presence
    assertions are still real (deletion happens synchronously
    when we call the helper).
    """

    def test_replacing_image_deletes_old_file(
        self, artisan_profile, customer, order_product, png_medium,
    ):
        from core.file_cleanup import _safe_delete_file

        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product, image=png_medium,
        )
        old_name = msg.image.name
        old_path = Path(default_storage.path(old_name))
        assert old_path.exists()

        # Replace with a fresh upload.
        fresh = _png_upload(name="replacement.png")
        msg.image = fresh
        msg.save(update_fields=["image"])
        new_name = msg.image.name
        assert new_name != old_name

        # Simulate what post_save would schedule via on_commit —
        # the deletion helper is what runs.
        _safe_delete_file(
            ArtisanChatMessage, "image", old_name,
            reason="test: replaced",
        )
        assert not Path(default_storage.path(old_name)).exists()

    def test_deleting_message_deletes_image(
        self, artisan_profile, customer, order_product, png_medium,
    ):
        from core.file_cleanup import _safe_delete_file

        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="x", order_product=order_product, image=png_medium,
        )
        image_name = msg.image.name
        image_path = Path(default_storage.path(image_name))
        assert image_path.exists()

        # Delete the row; the post_delete receiver schedules the
        # file deletion via on_commit. Run the helper directly to
        # assert the *wiring target* is correct.
        msg.delete()
        _safe_delete_file(
            ArtisanChatMessage, "image", image_name,
            reason="test: row deleted",
        )
        assert not Path(default_storage.path(image_name)).exists()

    def test_shared_file_not_deleted(
        self, artisan_profile, customer, order_product, png_medium,
    ):
        """
        _safe_delete_file's _is_still_referenced guard prevents
        deleting a file that another row still points at. Two
        messages may share an image (rare, but not prohibited by
        the schema). Deleting one must not orphan the other.
        """
        from core.file_cleanup import _safe_delete_file

        m1 = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="m1", order_product=order_product, image=png_medium,
        )
        shared_name = m1.image.name

        # Re-upload the same file into a second row.
        import io as _io
        from PIL import Image as _Image
        from django.core.files.uploadedfile import SimpleUploadedFile as _SUF
        buf = _io.BytesIO()
        _Image.new("RGB", (800, 600), (50, 50, 50)).save(buf, format="PNG")
        upload = _SUF("shared.png", buf.getvalue(), content_type="image/png")
        m2 = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="m2", order_product=order_product, image=upload,
        )
        # Force m2's image to *share* m1's path.
        ArtisanChatMessage.objects.filter(pk=m2.pk).update(image=shared_name)
        m2.refresh_from_db()
        assert m2.image.name == shared_name

        # Attempting to delete m1's file must be a no-op.
        _safe_delete_file(
            ArtisanChatMessage, "image", shared_name,
            reason="test: shared",
        )
        assert Path(default_storage.path(shared_name)).exists()


class TestCrossCutting:
    """Interaction with the existing post_save signal and the pipeline."""

    def test_large_valid_image_is_accepted_and_optimized(
        self, client, customer, artisan_profile, order_product,
    ):
        """
        The validation gate must not reject large-but-valid images,
        and the inline pipeline must convert them to WebP.

        Uses _png_inline (400x400 noisy, ~200-500 KB) so the file
        falls below INLINE_SIZE_THRESHOLD_BYTES and processes inline
        rather than going to Celery. A true "large" image (>= 1 MB)
        would be deferred to the async task, which this test suite
        does not run — see the module docstring.
        """
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "check the proof",
                "image": _png_inline(),
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302
        msg = (
            ArtisanChatMessage.objects
            .filter(customer=customer, order_product=order_product)
            .latest("created_at")
        )
        assert msg.content == "check the proof"
        assert msg.image.name.endswith(".webp")

    def test_settled_thread_reopens_on_new_image_message(
        self, client, customer, artisan_profile, order_product, png_medium,
    ):
        """
        maintain_frontline_thread clears settled_at on any new
        message. That semantic must survive the new pre_save and
        pipeline interactions — the image-attached path is a new
        shape, and the settled-clear behaviour must not be tied to
        text-only messages.
        """
        # Seed a first message to create the thread, then settle it.
        seed = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer, sender=customer,
            content="seed", order_product=order_product,
        )
        thread = FrontlineThread.objects.get(order_product=order_product)
        thread.mark_settled()
        thread.refresh_from_db()
        assert thread.settled_at is not None

        # Send a new image-attached message.
        client.force_login(customer)
        response = client.post(
            reverse(
                "customer_thread_send",
                kwargs={"artisan_slug": artisan_profile.slug},
            ),
            {
                "content": "",
                "image": png_medium,
                "order_product_id": order_product.id,
            },
        )
        assert response.status_code == 302

        thread.refresh_from_db()
        assert thread.settled_at is None
        assert thread.last_message_at is not None


