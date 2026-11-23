# creators/tests/test_artisan_admin_messages_htmx.py
"""
HTMX tests for the artisan ↔ admin threads (Session 9).
"""
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from PIL import Image

from accounts.models import Account
from creators.models import ArtisanAdminMessage, CreatorProfile


def _png_bytes(color=(255, 0, 0)):
    buf = BytesIO()
    Image.new("RGB", (8, 8), color).save(buf, format="PNG")
    buf.seek(0)
    buf.name = "test.png"
    return buf


class ArtisanAdminSendHTMXTests(TestCase):
    """creators.dashboard_messages_admin_send — artisan → admin."""

    @classmethod
    def setUpTestData(cls):
        # is_active=True is required: Account.is_active defaults to False
        # and create_user does not flip it (only create_superuser does).
        cls.artisan_user = Account.objects.create_user(
            username="artisan1",
            email="a1@example.com",
            password="pass1234",
            receive_newsletter=False,
            is_active=True,
        )
        cls.profile = CreatorProfile.objects.create(
            user=cls.artisan_user, display_name="A1", is_verified=True,
        )

    def setUp(self):
        self.client.force_login(self.artisan_user)
        self.url = reverse("a_dashboard_messages_admin_send")

    def test_htmx_success_returns_partial_with_new_message(self):
        resp = self.client.post(
            self.url, {"content": "hello"}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(b"<html", resp.content)
        self.assertIn(b"hello", resp.content)
        self.assertTrue(
            ArtisanAdminMessage.objects.filter(content="hello").exists()
        )

    def test_htmx_empty_returns_error_and_restores_textarea(self):
        resp = self.client.post(
            self.url, {"content": ""}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'id="admin-message-error"', resp.content)
        self.assertIn(b"Message cannot be empty", resp.content)
        self.assertIn(b'id="admin-message-content"', resp.content)
        self.assertEqual(ArtisanAdminMessage.objects.count(), 0)

    def test_htmx_empty_with_typed_text_restores_it(self):
        resp = self.client.post(
            self.url, {"content": "   "}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Message cannot be empty", resp.content)
        self.assertIn(b">   </textarea>", resp.content)

    def test_htmx_corrupt_image_returns_error(self):
        bad = BytesIO(b"not an image")
        bad.name = "bad.png"
        resp = self.client.post(
            self.url, {"content": "", "image": bad},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"not a readable image", resp.content)
        self.assertIn(b'id="admin-message-error"', resp.content)
        self.assertEqual(ArtisanAdminMessage.objects.count(), 0)

    def test_non_htmx_still_redirects(self):
        resp = self.client.post(self.url, {"content": "hello"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("a_dashboard_messages_admin"), resp.url)


class ArtisanMessagesSendHTMXTests(TestCase):
    """accounts.artisan_messages_send — admin → artisan."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Account.objects.create_superuser(
            username="admin1",
            email="admin@example.com",
            password="pass1234",
        )
        cls.artisan_user = Account.objects.create_user(
            username="artisan2",
            email="a2@example.com",
            password="pass1234",
            receive_newsletter=False,
            is_active=True,
        )
        cls.profile = CreatorProfile.objects.create(
            user=cls.artisan_user, display_name="A2", is_verified=True,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)
        self.url = reverse("artisan_messages_send", args=[self.profile.id])

    def test_htmx_success_returns_partial_with_new_message(self):
        resp = self.client.post(
            self.url, {"content": "reply from admin"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"reply from admin", resp.content)
        self.assertNotIn(b"<html", resp.content)
        self.assertTrue(
            ArtisanAdminMessage.objects
            .filter(content="reply from admin", sender=self.admin_user)
            .exists()
        )

    def test_htmx_empty_returns_error_banner(self):
        resp = self.client.post(
            self.url, {"content": ""}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'id="admin-artisan-message-error"', resp.content)
        self.assertIn(b"Message cannot be empty", resp.content)
        self.assertEqual(ArtisanAdminMessage.objects.count(), 0)

    def test_htmx_corrupt_image_returns_error(self):
        bad = BytesIO(b"not an image")
        bad.name = "bad.png"
        resp = self.client.post(
            self.url, {"content": "", "image": bad},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"not a readable image", resp.content)
        self.assertEqual(ArtisanAdminMessage.objects.count(), 0)

    def test_non_htmx_still_redirects(self):
        resp = self.client.post(self.url, {"content": "reply"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("artisan=", resp.url)

    def test_non_superadmin_htmx_still_403s(self):
        self.client.force_login(self.artisan_user)
        resp = self.client.post(
            self.url, {"content": "not allowed"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(ArtisanAdminMessage.objects.count(), 0)


class AdminArtisanDirectoryTests(TestCase):
    """Admin sees all verified artisans, not only those with prior threads."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Account.objects.create_superuser(
            username="admin1", email="admin1@example.com", password="pass1234",
        )
        cls.artisan_with_thread = Account.objects.create_user(
            username="a_with", email="aw@example.com",
            password="pass1234", receive_newsletter=False, is_active=True,
        )
        cls.profile_with = CreatorProfile.objects.create(
            user=cls.artisan_with_thread, display_name="Has Thread", is_verified=True,
        )
        cls.artisan_no_thread = Account.objects.create_user(
            username="a_without", email="an@example.com",
            password="pass1234", receive_newsletter=False, is_active=True,
        )
        cls.profile_no = CreatorProfile.objects.create(
            user=cls.artisan_no_thread, display_name="No Thread", is_verified=True,
        )
        ArtisanAdminMessage.objects.create(
            artisan=cls.profile_with, sender=cls.admin_user,
            content="hi", is_read=False,
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_artisan_with_no_thread_appears_in_list(self):
        resp = self.client.get(
            reverse("dashboard", kwargs={"subpage": "artisan_messages"})
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Has Thread")
        self.assertContains(resp, "No Thread")


class SendSetsHxTriggerTests(TestCase):
    """Success paths set HX-Trigger so the client clears the form."""

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = Account.objects.create_superuser(
            username="admin2", email="admin2@example.com", password="pass1234",
        )
        cls.artisan_user = Account.objects.create_user(
            username="artisan3", email="a3@example.com",
            password="pass1234", receive_newsletter=False, is_active=True,
        )
        cls.profile = CreatorProfile.objects.create(
            user=cls.artisan_user, display_name="A3", is_verified=True,
        )

    def test_artisan_send_sets_hx_trigger_on_success(self):
        self.client.force_login(self.artisan_user)
        url = reverse("a_dashboard_messages_admin_send")
        resp = self.client.post(
            url, {"content": "hi"}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("adminMessageSent", resp.headers.get("HX-Trigger", ""))

    def test_admin_send_sets_hx_trigger_on_success(self):
        self.client.force_login(self.admin_user)
        url = reverse("artisan_messages_send", args=[self.profile.id])
        resp = self.client.post(
            url, {"content": "hi"}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("adminArtisanMessageSent", resp.headers.get("HX-Trigger", ""))

    def test_artisan_send_error_does_not_set_trigger(self):
        # An error path must NOT set the trigger, or the client wipes the restored textarea.
        self.client.force_login(self.artisan_user)
        url = reverse("a_dashboard_messages_admin_send")
        resp = self.client.post(
            url, {"content": ""}, HTTP_HX_REQUEST="true",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("adminMessageSent", resp.headers.get("HX-Trigger", ""))