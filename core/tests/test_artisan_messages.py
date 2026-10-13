# core/tests/test_artisan_messages.py
"""
Tests for the artisan Messages dashboard and the ArtisanChatMessage
model.

Scope of v1 (Option A, plain text):

  * One thread per (artisan, customer) pair, implied by the FKs.
  * No WebSocket, no attachments, no search, no customer-side view.
  * unread_messages_count in creators.context reflects the artisan's
    own inbox, not the member↔admin ChatMessage table.

The last point matters: the previous session's context builder
hardcoded the count to 0 as a placeholder precisely so it would not be
mistakenly wired to ChatMessage. These tests pin the real wire-up.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.fixture
def artisan_with_customers(db, django_user_model):
    from creators.models import CreatorProfile

    artisan_user = django_user_model.objects.create_user(
        username="msg_artisan",
        email="msg-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    profile = CreatorProfile.objects.create(
        user=artisan_user,
        display_name="Messages Artisan",
        slug="messages-artisan",
        is_verified=True,
    )
    customer_a = django_user_model.objects.create_user(
        username="msg_customer_a",
        email="msg-customer-a@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    customer_b = django_user_model.objects.create_user(
        username="msg_customer_b",
        email="msg-customer-b@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )
    return {
        "artisan_user": artisan_user,
        "profile": profile,
        "customer_a": customer_a,
        "customer_b": customer_b,
    }


@pytest.fixture
def non_artisan(db, django_user_model):
    return django_user_model.objects.create_user(
        username="not_artisan",
        email="not-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


class TestModel:

    def test_message_str_and_ordering(self, artisan_with_customers):
        from creators.models import ArtisanChatMessage

        chain = artisan_with_customers
        m1 = ArtisanChatMessage.objects.create(
            artisan=chain["profile"],
            customer=chain["customer_a"],
            sender=chain["customer_a"],
            content="first",
        )
        m2 = ArtisanChatMessage.objects.create(
            artisan=chain["profile"],
            customer=chain["customer_a"],
            sender=chain["artisan_user"],
            content="second",
        )

        # Default ordering is chronological.
        ordered = list(ArtisanChatMessage.objects.filter(artisan=chain["profile"]))
        assert ordered == [m1, m2]
        assert "first" in str(m1)


class TestContextUnreadCount:

    def test_counts_only_customer_authored_unread(
        self, rf, artisan_with_customers,
    ):
        from creators.models import ArtisanChatMessage
        from creators.context import artisan_dashboard_context

        chain = artisan_with_customers
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["customer_a"], content="a1",
        )
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["customer_a"], content="a2",
        )
        # Artisan-authored message: is_read=True, doesn't count.
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["artisan_user"], content="reply",
            is_read=True,
        )
        # A different customer's message: still this artisan's inbox.
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_b"],
            sender=chain["customer_b"], content="b1",
        )

        request = rf.get("/")
        request.user = chain["artisan_user"]
        ctx = artisan_dashboard_context(request)
        assert ctx["unread_messages_count"] == 3


class TestDashboardMessagesView:

    def test_no_messages_renders_empty_state(
        self, client, artisan_with_customers,
    ):
        chain = artisan_with_customers
        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_messages"))
        assert response.status_code == 200
        assert list(response.context["threads"]) == []

    def test_threads_grouped_by_customer(
        self, client, artisan_with_customers,
    ):
        from creators.models import ArtisanChatMessage

        chain = artisan_with_customers
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["customer_a"], content="hello A",
        )
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_b"],
            sender=chain["customer_b"], content="hello B",
        )
        ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["customer_a"], content="A again",
        )

        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_messages"))
        threads = list(response.context["threads"])
        assert len(threads) == 2
        by_id = {t["customer"]: t for t in threads}
        assert by_id[chain["customer_a"].id]["unread"] == 2
        assert by_id[chain["customer_b"].id]["unread"] == 1

    def test_opening_a_thread_flips_unread_to_read(
        self, client, artisan_with_customers,
    ):
        from creators.models import ArtisanChatMessage

        chain = artisan_with_customers
        msg = ArtisanChatMessage.objects.create(
            artisan=chain["profile"], customer=chain["customer_a"],
            sender=chain["customer_a"], content="please read",
        )
        assert msg.is_read is False

        client.force_login(chain["artisan_user"])
        url = reverse("a_dashboard_messages") + f"?customer={chain['customer_a'].id}"
        response = client.get(url)
        assert response.status_code == 200

        msg.refresh_from_db()
        assert msg.is_read is True

    def test_other_artisans_messages_are_not_visible(
        self, client, artisan_with_customers, django_user_model,
    ):
        from creators.models import ArtisanChatMessage, CreatorProfile

        chain = artisan_with_customers
        other_user = django_user_model.objects.create_user(
            username="other_artisan",
            email="other-artisan@example.com",
            receive_newsletter=False,
            password="x",
            is_active=True,
        )
        other_profile = CreatorProfile.objects.create(
            user=other_user,
            display_name="Other Artisan",
            slug="other-artisan",
            is_verified=True,
        )
        ArtisanChatMessage.objects.create(
            artisan=other_profile, customer=chain["customer_a"],
            sender=chain["customer_a"], content="private to other",
        )

        client.force_login(chain["artisan_user"])
        response = client.get(reverse("a_dashboard_messages"))
        assert list(response.context["threads"]) == []


class TestDashboardMessagesSend:

    def test_send_creates_message_marked_read(
        self, client, artisan_with_customers,
    ):
        from creators.models import ArtisanChatMessage

        chain = artisan_with_customers
        client.force_login(chain["artisan_user"])
        url = reverse(
            "a_dashboard_messages_send", args=[chain["customer_a"].id],
        )
        response = client.post(url, {"content": "hi there"})
        assert response.status_code in (301, 302)

        msg = ArtisanChatMessage.objects.get(artisan=chain["profile"])
        assert msg.content == "hi there"
        assert msg.sender == chain["artisan_user"]
        assert msg.is_read is True

    def test_send_rejects_empty_content(
        self, client, artisan_with_customers,
    ):
        from creators.models import ArtisanChatMessage

        chain = artisan_with_customers
        client.force_login(chain["artisan_user"])
        url = reverse(
            "a_dashboard_messages_send", args=[chain["customer_a"].id],
        )
        response = client.post(url, {"content": "   "})
        assert response.status_code in (301, 302)
        assert not ArtisanChatMessage.objects.filter(
            artisan=chain["profile"],
        ).exists()


class TestAccessControl:

    def test_non_artisan_gets_403_on_messages(
        self, client, non_artisan,
    ):
        client.force_login(non_artisan)
        response = client.get(reverse("a_dashboard_messages"))
        assert response.status_code == 403

    def test_anonymous_redirected_to_login(self, client):
        response = client.get(reverse("a_dashboard_messages"))
        assert response.status_code == 302
        assert "/accounts/login/" in response["Location"]