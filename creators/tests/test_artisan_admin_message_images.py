# creators/tests/test_artisan_admin_message_images.py
"""
Image-attachment support on ArtisanAdminMessage (Backlog 3b-bis).

Mirrors creators/tests/test_artisan_message_images.py, minus the
order-product / FrontlineThread machinery — ArtisanAdminMessage has
neither. The delta vs. the sibling:

  * No Order / OrderProduct / Product fixtures.
  * No FrontlineThread interaction (the admin-side thread is not
    threaded; it's one row per artisan).
  * The admin-side send view (accounts.views.artisan_messages_send)
    dispatches a notification email via transaction.on_commit. The
    image-only path must still dispatch it, and the corrupt-image
    path must not. Two tests pin that.
  * Storage folder is artisan_admin_chat_images/, not
    artisan_chat_images/.

Known limitation (inherited from the sibling, not new): the
sweep_orphan_media.py registry entry for the new folder has no
dedicated test. See HANDOFF_2026-11-19-Part2.md, "Known Limitation".
"""
import io
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from creators.models import ArtisanAdminMessage, CreatorProfile
from tests._fakes import make_superuser

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    return make_superuser(
        username="aami-admin", email="aami-admin@example.com",
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="aami-artisan",
        email="aami-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user, display_name="AAMI Artisan", is_verified=True,
    )


def _png_upload(name="preview.png", size=(300, 300), color=(10, 100, 200)):
    """Small PNG — below MIN_PROCESS_BYTES, so the pipeline skips it."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return SimpleUploadedFile(
        name, buf.getvalue(), content_type="image/png",
    )


def _png_inline(name="probe_inline.png", size=(400, 400)):
    """
    Noisy PNG in the inline-processing band (80 KB .. 1 MB).
    Copy of the sibling's helper — the seed and size guard are
    deliberate.
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
    assert 80 * 1024 < len(body) < 1024 * 1024, (
        f"fixture size {len(body)} is outside the inline band "
        f"(80 KB .. 1 MB); adjust dimensions."
    )
    return SimpleUploadedFile(name, body, content_type="image/png")


# ──────────────────────────────────────────────────────────────
# Field shape
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_artisanadminmessage_image_field_shape():
    from django.db.models import ImageField

    field = ArtisanAdminMessage._meta.get_field("image")
    assert isinstance(field, ImageField)
    assert field.null is True
    assert field.blank is True
    assert field.upload_to == "artisan_admin_chat_images/"


# ──────────────────────────────────────────────────────────────
# Artisan-side send (creators.views.dashboard_messages_admin_send)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanSideImageSend:

    URL = "a_dashboard_messages_admin_send"

    def test_image_only_message_succeeds(
        self, client, artisan_user, artisan_profile,
    ):
        client.force_login(artisan_user)
        response = client.post(
            reverse(self.URL),
            {"content": "", "image": _png_upload()},
        )
        assert response.status_code == 302

        msg = ArtisanAdminMessage.objects.get(
            artisan=artisan_profile, sender=artisan_user,
        )
        assert msg.content == ""
        assert msg.image
        assert msg.image.name.startswith("artisan_admin_chat_images/")
        assert msg.image.name.endswith(".png")

    def test_neither_content_nor_image_rejects(
        self, client, artisan_user, artisan_profile,
    ):
        before = ArtisanAdminMessage.objects.count()
        client.force_login(artisan_user)
        response = client.post(
            reverse(self.URL),
            {"content": ""},
        )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.count() == before

    def test_corrupt_image_rejected(
        self, client, artisan_user, artisan_profile, tiny_corrupt,
    ):
        before = ArtisanAdminMessage.objects.count()
        client.force_login(artisan_user)
        response = client.post(
            reverse(self.URL),
            {"content": "text", "image": tiny_corrupt},
        )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.count() == before

    def test_image_only_with_valid_image_succeeds(
        self, client, artisan_user, artisan_profile, png_medium,
    ):
        client.force_login(artisan_user)
        response = client.post(
            reverse(self.URL),
            {"content": "", "image": png_medium},
        )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.filter(
            artisan=artisan_profile, content="",
        ).exists()


# ──────────────────────────────────────────────────────────────
# Admin-side send (accounts.views.artisan_messages_send)
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAdminSideImageSend:

    @staticmethod
    def _url(artisan_profile):
        return reverse("artisan_messages_send", args=[artisan_profile.id])

    def test_image_only_message_succeeds(
        self, client, admin_user, artisan_profile,
    ):
        client.force_login(admin_user)
        response = client.post(
            self._url(artisan_profile),
            {"content": "", "image": _png_upload()},
        )
        assert response.status_code == 302

        msg = ArtisanAdminMessage.objects.get(
            artisan=artisan_profile, sender=admin_user,
        )
        assert msg.content == ""
        assert msg.image
        assert msg.image.name.startswith("artisan_admin_chat_images/")

    def test_neither_content_nor_image_rejects(
        self, client, admin_user, artisan_profile,
    ):
        before = ArtisanAdminMessage.objects.count()
        client.force_login(admin_user)
        response = client.post(
            self._url(artisan_profile),
            {"content": ""},
        )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.count() == before

    def test_corrupt_image_rejected_no_email_queued(
        self, client, admin_user, artisan_profile, tiny_corrupt, monkeypatch,
    ):
        """
        ValidationError inside the atomic block must roll back the
        row *and* prevent the on_commit email dispatch. The email
        task's .delay is mocked so we can assert it wasn't called.
        """
        from creators import tasks as creators_tasks

        queued = []
        monkeypatch.setattr(
            creators_tasks.send_artisan_admin_message_email_task,
            "delay",
            lambda mid: queued.append(mid),
        )

        before = ArtisanAdminMessage.objects.count()
        client.force_login(admin_user)
        response = client.post(
            self._url(artisan_profile),
            {"content": "typed text", "image": tiny_corrupt},
        )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.count() == before
        assert queued == [], (
            "email task must not be queued when the image is rejected"
        )

    def test_image_only_dispatches_email(
        self, client, admin_user, artisan_profile, monkeypatch,
        django_capture_on_commit_callbacks,
    ):
        """
        Image-only messages are still messages — the counterparty
        notification must fire. Pins that the content-OR-image
        widening didn't accidentally bypass the on_commit.

        Uses pytest-django's django_capture_on_commit_callbacks
        (execute=True) because the view registers the task via
        transaction.on_commit, which does not fire under the test
        transaction wrapper without an explicit capture.
        """
        from creators import tasks as creators_tasks

        queued = []
        monkeypatch.setattr(
            creators_tasks.send_artisan_admin_message_email_task,
            "delay",
            lambda mid: queued.append(mid),
        )

        client.force_login(admin_user)
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(
                self._url(artisan_profile),
                {"content": "", "image": _png_upload()},
            )
        assert response.status_code == 302
        assert ArtisanAdminMessage.objects.filter(
            artisan=artisan_profile, content="",
        ).exists()
        assert queued, (
            "email task must be queued for image-only admin messages"
        )


# ──────────────────────────────────────────────────────────────
# Pipeline registration
# ──────────────────────────────────────────────────────────────

class TestImagePipelineRegistration:

    def test_medium_png_is_optimized_to_webp(
        self, client, artisan_user, artisan_profile,
    ):
        client.force_login(artisan_user)
        response = client.post(
            reverse("a_dashboard_messages_admin_send"),
            {"content": "", "image": _png_inline()},
        )
        assert response.status_code == 302

        msg = (
            ArtisanAdminMessage.objects
            .filter(artisan=artisan_profile)
            .latest("created_at")
        )
        assert msg.image
        assert msg.image.name.startswith("artisan_admin_chat_images/")
        assert msg.image.name.endswith(".webp"), (
            f"expected .webp, got {msg.image.name}"
        )

    def test_small_png_is_left_as_png(
        self, client, artisan_user, artisan_profile,
    ):
        client.force_login(artisan_user)
        response = client.post(
            reverse("a_dashboard_messages_admin_send"),
            {"content": "", "image": _png_upload()},
        )
        assert response.status_code == 302

        msg = (
            ArtisanAdminMessage.objects
            .filter(artisan=artisan_profile)
            .latest("created_at")
        )
        assert msg.image.name.endswith(".png")


# ──────────────────────────────────────────────────────────────
# Validation gate (direct unit test on the receiver)
# ──────────────────────────────────────────────────────────────

class TestImageValidationGate:

    def test_receiver_raises_on_corrupt_and_passes_on_valid(
        self, artisan_profile, artisan_user, png_medium, tiny_corrupt,
    ):
        from creators.signals import validate_artisan_admin_message_image

        # (1) No image → no raise.
        no_img = ArtisanAdminMessage(
            artisan=artisan_profile, sender=artisan_user, content="x",
        )
        validate_artisan_admin_message_image(
            sender=ArtisanAdminMessage, instance=no_img,
        )

        # (2) Valid image → no raise; handle still open; magic bytes.
        buf = io.BytesIO()
        Image.new("RGB", (800, 600), (30, 60, 90)).save(buf, format="PNG")
        valid = ArtisanAdminMessage(
            artisan=artisan_profile, sender=artisan_user, content="x",
            image=SimpleUploadedFile(
                "probe.png", buf.getvalue(), content_type="image/png",
            ),
        )
        validate_artisan_admin_message_image(
            sender=ArtisanAdminMessage, instance=valid,
        )
        assert valid.image.file is not None
        assert not valid.image.file.closed, (
            "pre_save receiver closed the upload handle — Django's "
            "storage layer will fail with 'I/O operation on closed "
            "file' when it tries to stream the bytes."
        )
        valid.image.seek(0)
        head = valid.image.read(8)
        assert head.startswith(b"\x89PNG"), (
            f"expected PNG magic bytes after receiver, got {head!r}"
        )

        # (2b) Pipeline write-back skip.
        pipeline_save = ArtisanAdminMessage(
            artisan=artisan_profile, sender=artisan_user, content="x",
            image=SimpleUploadedFile(
                "pipeline.png", buf.getvalue(), content_type="image/png",
            ),
        )
        pipeline_save.image.file.close()
        pipeline_save._skip_image_optimization = True
        validate_artisan_admin_message_image(
            sender=ArtisanAdminMessage, instance=pipeline_save,
        )

        # (3) Corrupt image → ValidationError.
        corrupt = ArtisanAdminMessage(
            artisan=artisan_profile, sender=artisan_user, content="x",
            image=tiny_corrupt,
        )
        with pytest.raises(ValidationError):
            validate_artisan_admin_message_image(
                sender=ArtisanAdminMessage, instance=corrupt,
            )


# ──────────────────────────────────────────────────────────────
# Cleanup registration
# ──────────────────────────────────────────────────────────────

class TestImageCleanupRegistration:

    def test_replacing_image_deletes_old_file(
        self, artisan_profile, artisan_user, png_medium,
    ):
        from core.file_cleanup import _safe_delete_file

        msg = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile, sender=artisan_user,
            content="x", image=png_medium,
        )
        old_name = msg.image.name
        assert Path(default_storage.path(old_name)).exists()

        msg.image = _png_upload(name="replacement.png")
        msg.save(update_fields=["image"])

        _safe_delete_file(
            ArtisanAdminMessage, "image", old_name,
            reason="test: replaced",
        )
        assert not Path(default_storage.path(old_name)).exists()

    def test_deleting_message_deletes_image(
        self, artisan_profile, artisan_user, png_medium,
    ):
        from core.file_cleanup import _safe_delete_file

        msg = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile, sender=artisan_user,
            content="x", image=png_medium,
        )
        image_name = msg.image.name
        assert Path(default_storage.path(image_name)).exists()

        msg.delete()
        _safe_delete_file(
            ArtisanAdminMessage, "image", image_name,
            reason="test: row deleted",
        )
        assert not Path(default_storage.path(image_name)).exists()

    def test_shared_file_not_deleted(
        self, artisan_profile, artisan_user, png_medium,
    ):
        from core.file_cleanup import _safe_delete_file

        m1 = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile, sender=artisan_user,
            content="m1", image=png_medium,
        )
        shared_name = m1.image.name

        buf = io.BytesIO()
        Image.new("RGB", (800, 600), (50, 50, 50)).save(buf, format="PNG")
        m2 = ArtisanAdminMessage.objects.create(
            artisan=artisan_profile, sender=artisan_user,
            content="m2", image=SimpleUploadedFile(
                "shared.png", buf.getvalue(), content_type="image/png",
            ),
        )
        ArtisanAdminMessage.objects.filter(pk=m2.pk).update(image=shared_name)
        m2.refresh_from_db()
        assert m2.image.name == shared_name

        _safe_delete_file(
            ArtisanAdminMessage, "image", shared_name,
            reason="test: shared",
        )
        assert Path(default_storage.path(shared_name)).exists()