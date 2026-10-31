# creators/tests/test_artisan_admin_messages.py
"""
Tests for ArtisanAdminMessage (artisan ↔ admin thread) and its
unread_admin_messages_count context counter.

Scope of v1 (Option A, plain text):

  * One thread per artisan, implied by the FK. The counterparty is
    fixed (the platform admin), so there is no `customer` FK and no
    thread picker on the artisan side.
  * No WebSocket, no attachments, no search.
  * unread_admin_messages_count is a sibling of unread_messages_count
    (the customer thread). Repointing one at the other is the bug this
    file exists to catch.
"""

from django.urls import reverse as _reverse
from django.urls import reverse
from tests._fakes import make_superuser
import pytest


@pytest.fixture
def artisan_with_admin_peer(db, django_user_model):
    from creators.models import CreatorProfile

    artisan_user = django_user_model.objects.create_user(
        username="adminmsg_artisan",
        email="adminmsg-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Admin Msg Artisan",
        slug="admin-msg-artisan",
        is_verified=True,
    )
    # The admin is a separate Account; the thread is keyed only on
    # the artisan, but `sender` still resolves to this row when the
    # admin writes.
    admin_user = django_user_model.objects.create_user(
        username="adminmsg_admin",
        email="adminmsg-admin@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    return {"artisan_user": artisan_user, "profile": profile, "admin_user": admin_user}


@pytest.fixture
def other_artisan(db, django_user_model):
    from creators.models import CreatorProfile

    user = django_user_model.objects.create_user(
        username="adminmsg_other",
        email="adminmsg-other@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    return CreatorProfile.objects.create(
        user=user,
        display_name="Other Admin Msg Artisan",
        slug="other-admin-msg-artisan",
        is_verified=True,
    )


class TestModel:

    def test_str_and_ordering(self, artisan_with_admin_peer):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        m1 = ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"],
            sender=ctx["admin_user"],
            content="first",
        )
        m2 = ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"],
            sender=ctx["artisan_user"],
            content="second",
        )

        ordered = list(
            ArtisanAdminMessage.objects.filter(artisan=ctx["profile"])
        )
        assert ordered == [m1, m2]
        assert "first" in str(m1)

    def test_is_read_defaults_false(self, artisan_with_admin_peer):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        m = ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"],
            sender=ctx["admin_user"],
            content="unread by default",
        )
        assert m.is_read is False


class TestContextUnreadAdminCount:

    def test_counts_only_admin_authored_unread(
        self, rf, artisan_with_admin_peer,
    ):
        from creators.models import ArtisanAdminMessage
        from creators.context import artisan_dashboard_context

        ctx = artisan_with_admin_peer
        # Two unread from the admin.
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["admin_user"], content="a1",
        )
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["admin_user"], content="a2",
        )
        # Artisan-authored: is_read=False (waiting for admin), doesn't count.
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["artisan_user"],
            content="reply", is_read=False,
        )
        # Read admin message: doesn't count.
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["admin_user"],
            content="already read", is_read=True,
        )

        request = rf.get("/")
        request.user = ctx["artisan_user"]
        result = artisan_dashboard_context(request)
        assert result["unread_admin_messages_count"] == 2

    def test_customer_thread_count_unaffected(
        self, rf, artisan_with_admin_peer, django_user_model,
    ):
        """
        The two counters are siblings: writing to ArtisanAdminMessage
        must not move unread_messages_count (ArtisanChatMessage), and
        vice versa.
        """
        from creators.models import ArtisanChatMessage, ArtisanAdminMessage
        from creators.context import artisan_dashboard_context

        ctx = artisan_with_admin_peer
        customer = django_user_model.objects.create_user(
            username="adminmsg_customer",
            email="adminmsg-customer@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        ArtisanChatMessage.objects.create(
            artisan=ctx["profile"], customer=customer,
            sender=customer, content="customer msg",
        )
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["admin_user"],
            content="admin msg",
        )

        request = rf.get("/")
        request.user = ctx["artisan_user"]
        result = artisan_dashboard_context(request)
        assert result["unread_messages_count"] == 1
        assert result["unread_admin_messages_count"] == 1

    def test_other_artisans_messages_do_not_count(
        self, rf, artisan_with_admin_peer, other_artisan,
    ):
        from creators.models import ArtisanAdminMessage
        from creators.context import artisan_dashboard_context

        ctx = artisan_with_admin_peer
        # The admin wrote to a different artisan; this artisan's
        # counter must not move.
        ArtisanAdminMessage.objects.create(
            artisan=other_artisan, sender=ctx["admin_user"],
            content="to a different artisan",
        )

        request = rf.get("/")
        request.user = ctx["artisan_user"]
        result = artisan_dashboard_context(request)
        assert result["unread_admin_messages_count"] == 0


class TestDashboardMessagesAdminView:

    def test_no_messages_renders_empty_state(
        self, client, artisan_with_admin_peer,
    ):
        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])
        response = client.get(reverse("a_dashboard_messages_admin"))
        assert response.status_code == 200
        assert list(response.context["admin_messages"]) == []

    def test_opening_flips_unread_to_read(
        self, client, artisan_with_admin_peer,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        m = ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["admin_user"],
            content="please read",
        )
        assert m.is_read is False

        client.force_login(ctx["artisan_user"])
        response = client.get(reverse("a_dashboard_messages_admin"))
        assert response.status_code == 200

        m.refresh_from_db()
        assert m.is_read is True

    def test_other_artisans_messages_are_not_visible(
        self, client, artisan_with_admin_peer, other_artisan,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        ArtisanAdminMessage.objects.create(
            artisan=other_artisan, sender=ctx["admin_user"],
            content="private to other",
        )

        client.force_login(ctx["artisan_user"])
        response = client.get(reverse("a_dashboard_messages_admin"))
        assert response.status_code == 200
        assert list(response.context["admin_messages"]) == []


class TestDashboardMessagesAdminSend:

    def test_send_creates_unread_message(
        self, client, artisan_with_admin_peer,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])
        response = client.post(
            reverse("a_dashboard_messages_admin_send"),
            {"content": "hi platform"},
        )
        assert response.status_code in (301, 302)

        m = ArtisanAdminMessage.objects.get(artisan=ctx["profile"])
        assert m.content == "hi platform"
        assert m.sender == ctx["artisan_user"]
        assert m.is_read is False

    def test_send_rejects_empty_content(
        self, client, artisan_with_admin_peer,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])
        response = client.post(
            reverse("a_dashboard_messages_admin_send"),
            {"content": "   "},
        )
        assert response.status_code in (301, 302)
        assert not ArtisanAdminMessage.objects.filter(
            artisan=ctx["profile"],
        ).exists()


class TestAdminThreadAccessControl:

    def test_non_artisan_gets_403(self, client, db, django_user_model):
        user = django_user_model.objects.create_user(
            username="adminmsg_non_artisan",
            email="adminmsg-non-artisan@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        client.force_login(user)
        response = client.get(reverse("a_dashboard_messages_admin"))
        assert response.status_code == 403

    def test_anonymous_redirected_to_login(self, client):
        response = client.get(reverse("a_dashboard_messages_admin"))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]


class TestAdminSideView:

    def test_non_superadmin_redirected(
        self, client, artisan_with_admin_peer,
    ):
        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])  # artisan, not superadmin
        response = client.get(
            _reverse("dashboard", kwargs={"subpage": "artisan_messages"}),
        )
        # dashboard's non-superadmin branch redirects to main
        assert response.status_code == 302
        assert "/accounts/dashboard/main/" in response["Location"]

    def test_superadmin_can_open_and_pick_an_artisan(
        self, client, artisan_with_admin_peer, db,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        admin = make_superuser(
            username="artisan_msgs_superu",
            email="artisan-msgs-superu@example.com",
        )
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["artisan_user"],
            content="ping",
        )
        client.force_login(admin)
        url = (
            _reverse("dashboard", kwargs={"subpage": "artisan_messages"})
            + f"?artisan={ctx['profile'].id}"
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["active_artisan"].id == ctx["profile"].id
        assert len(list(response.context["active_artisan_messages"])) == 1

    def test_superadmin_sees_threads_grouped_by_artisan(
        self, client, artisan_with_admin_peer, other_artisan, db,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        admin = make_superuser(
            username="artisan_msgs_superu2",
            email="artisan-msgs-superu2@example.com",
        )
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["artisan_user"],
            content="hello A",
        )
        ArtisanAdminMessage.objects.create(
            artisan=other_artisan, sender=other_artisan.user,
            content="hello B",
        )
        client.force_login(admin)
        response = client.get(
            _reverse("dashboard", kwargs={"subpage": "artisan_messages"}),
        )
        threads = list(response.context["artisan_message_threads"])
        assert {t["artisan"] for t in threads} == {
            ctx["profile"].id, other_artisan.id,
        }


class TestAdminSendView:

    def test_superadmin_send_creates_message(
        self, client, artisan_with_admin_peer, db,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        admin = make_superuser(
            username="artisan_msgs_superu3",
            email="artisan-msgs-superu3@example.com",
        )
        client.force_login(admin)
        response = client.post(
            _reverse("artisan_messages_send", args=[ctx["profile"].id]),
            {"content": "admin reply"},
        )
        assert response.status_code in (301, 302)

        m = ArtisanAdminMessage.objects.get(artisan=ctx["profile"])
        assert m.content == "admin reply"
        assert m.sender == admin
        assert m.is_read is False

    def test_non_superadmin_send_returns_403(
        self, client, artisan_with_admin_peer,
    ):
        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])
        response = client.post(
            _reverse("artisan_messages_send", args=[ctx["profile"].id]),
            {"content": "sneaky"},
        )
        assert response.status_code == 403

    def test_empty_content_rejected(
        self, client, artisan_with_admin_peer, db,
    ):
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        admin = make_superuser(
            username="artisan_msgs_superu4",
            email="artisan-msgs-superu4@example.com",
        )
        client.force_login(admin)
        client.post(
            _reverse("artisan_messages_send", args=[ctx["profile"].id]),
            {"content": "   "},
        )
        assert not ArtisanAdminMessage.objects.filter(
            artisan=ctx["profile"],
        ).exists()


# ─── appended: context-processor test ───

class TestArtisanMessageCountProcessor:

    def test_non_superadmin_gets_no_key(self, rf, artisan_with_admin_peer):
        from creators.context_processors import artisan_message_count

        ctx = artisan_with_admin_peer
        request = rf.get("/")
        request.user = ctx["artisan_user"]
        assert artisan_message_count(request) == {}

    def test_anonymous_gets_no_key(self, rf):
        from django.contrib.auth.models import AnonymousUser
        from creators.context_processors import artisan_message_count

        request = rf.get("/")
        request.user = AnonymousUser()
        assert artisan_message_count(request) == {}

    def test_superadmin_gets_global_unread_count(
        self, rf, artisan_with_admin_peer, other_artisan, db,
    ):
        from creators.context_processors import artisan_message_count
        from creators.models import ArtisanAdminMessage
        from tests._fakes import make_superuser

        ctx = artisan_with_admin_peer
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["artisan_user"], content="unread A",
        )
        ArtisanAdminMessage.objects.create(
            artisan=other_artisan, sender=other_artisan.user, content="unread B",
        )
        admin = make_superuser(
            username="cc_superu_proc",
            email="cc-superu-proc@example.com",
        )
        request = rf.get("/")
        request.user = admin
        result = artisan_message_count(request)
        assert result["pending_artisan_message_count"] == 2

    def test_admin_sent_messages_do_not_count_toward_admin_badge(
        self, rf, artisan_with_admin_peer, other_artisan, db,
    ):
        """The admin's inbox badge counts artisan-authored unread
        messages, not admin-authored unread messages the artisan
        hasn't seen."""
        from creators.context_processors import artisan_message_count
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=ctx["artisan_user"],
            content="from artisan A", is_read=False,
        )
        ArtisanAdminMessage.objects.create(
            artisan=other_artisan, sender=other_artisan.user,
            content="from artisan B", is_read=False,
        )
        # Admin-authored message; should not count toward the admin's
        # own badge.
        admin = make_superuser(
            username="cc_superu_proc2",
            email="cc-superu-proc2@example.com",
        )
        ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"], sender=admin,
            content="from admin", is_read=False,
        )

        request = rf.get("/")
        request.user = admin
        result = artisan_message_count(request)
        assert result["pending_artisan_message_count"] == 2


# ─── appended: email-mirror tests ───

class TestEmailMirror:
    """
    Admin → artisan messages dispatch a notification email via
    transaction.on_commit. Artisan → admin messages do not.

    Transaction semantics: on_commit callbacks do not fire under
    pytest-django's default test transaction. Use the
    django_capture_on_commit_callbacks fixture (handoff gotcha #16).
    """

    def test_admin_send_dispatches_email_task(
        self, client, artisan_with_admin_peer, db,
        django_capture_on_commit_callbacks,
    ):
        from unittest.mock import patch
        from creators.models import ArtisanAdminMessage
        from tests._fakes import make_superuser

        ctx = artisan_with_admin_peer
        admin = make_superuser(
            username="email_mirror_admin",
            email="email-mirror-admin@example.com",
        )

        client.force_login(admin)

        with patch(
            "creators.tasks.send_artisan_admin_message_email_task.delay"
        ) as mock_delay, django_capture_on_commit_callbacks(execute=True):
            client.post(
                _reverse("artisan_messages_send", args=[ctx["profile"].id]),
                {"content": "hello artisan"},
            )

        # The task was created (the message row exists).
        msg = ArtisanAdminMessage.objects.get(artisan=ctx["profile"])
        assert msg.content == "hello artisan"

        # Exactly one task was dispatched, and it points at that row.
        assert mock_delay.call_count == 1
        dispatched_id = mock_delay.call_args.args[0]
        assert str(dispatched_id) == str(msg.id)

    def test_artisan_send_does_not_dispatch_email_task(
        self, client, artisan_with_admin_peer,
        django_capture_on_commit_callbacks,
    ):
        """
        The artisan-side view must not fire the admin-ward task.

        Pins the shape decision: admin → artisan is email-mirrored;
        artisan → admin surfaces via the sidebar badge, not email
        flood. A future refactor that "unifies" the two send views
        breaks this test by design.
        """
        from unittest.mock import patch
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        client.force_login(ctx["artisan_user"])

        with patch(
            "creators.tasks.send_artisan_admin_message_email_task.delay"
        ) as mock_delay, django_capture_on_commit_callbacks(execute=True):
            client.post(
                _reverse("a_dashboard_messages_admin_send"),
                {"content": "hi platform"},
            )

        # Message created.
        assert ArtisanAdminMessage.objects.filter(
            artisan=ctx["profile"],
        ).exists()

        # No task dispatched.
        assert mock_delay.call_count == 0

    def test_email_task_renders_and_sends(
        self, artisan_with_admin_peer,
        django_capture_on_commit_callbacks, mailoutbox,
    ):
        """
        End-to-end: the task actually renders a template and calls
        mail.send(). Uses mailoutbox (Django's locmem backend) to
        capture the payload, so this test would catch a broken
        template path or a missing context variable.
        """
        from creators.tasks import send_artisan_admin_message_email_task
        from creators.models import ArtisanAdminMessage

        ctx = artisan_with_admin_peer
        msg = ArtisanAdminMessage.objects.create(
            artisan=ctx["profile"],
            sender=ctx["admin_user"],
            content="This is a test message.\nSecond line.",
            is_read=True,
        )

        with django_capture_on_commit_callbacks(execute=False):
            send_artisan_admin_message_email_task(str(msg.id))

        # One email in the outbox, addressed to the artisan.
        assert len(mailoutbox) == 1
        sent = mailoutbox[0]
        assert sent.to == [ctx["artisan_user"].email]
        # The message body reaches the rendered plain-text part.
        assert "This is a test message" in sent.body

