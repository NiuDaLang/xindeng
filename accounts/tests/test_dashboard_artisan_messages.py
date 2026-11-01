# accounts/tests/test_dashboard_artisan_messages.py
"""
Tests for the `artisan_messages` branch of the dashboard view
(`accounts/views.py::dashboard`) — backlog item 29.

The 2026-10-31 walkthrough caught an ordering bug: the
`artisan_rows` annotation query was materialised *before* the flip
that marks the active artisan's *incoming* messages read. The row
badge in the thread list therefore didn't clear when the admin
opened the thread, even though the sidebar badge (recomputed by
the context processor post-flip) did. The fix reordered the branch:

    resolve active entity → flip → annotate → build dicts → load active thread

These tests pin the invariant. Two things are asserted:

  1. The flip itself. Opening the active thread sets `is_read=True`
     on **artisan-authored**, unread messages for that artisan
     (the ones the admin is reading). Per handoff §A2, the flip
     uses `.exclude(sender=request.user)` so that the admin's
     own outbound messages are not flipped — they're the
     admin's own sends, and the artisan's inbox is the one
     that needs to clear when the *artisan* opens the thread.

     The seed below therefore sends from `artisan_user`, not
     from the admin. That is the semantically correct direction
     for the admin-side flip.

  2. The flip runs *before* the annotation. `artisan_rows` for
     the active artisan reports `unread == 0` after a single GET.
     If the annotation ran pre-flip, it would report the
     pre-flip count (2 in the test seeds) despite the flip
     having cleared the rows — which is the exact bug the
     walkthrough caught.

Both tests exercise the `?artisan=<id>` query-string path through
the view (the artisan is resolved from `request.GET["artisan"]`,
not from `artisan_rows`, which is the documented behaviour in the
view's own comments).

Style mirrors `accounts/tests/test_activate.py`. The superuser is
built via `tests/_fakes.py::make_superuser` (the README says
fixtures must set both `is_admin` and `is_superadmin`).
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from creators.models import ArtisanAdminMessage, CreatorProfile
from tests._fakes import make_superuser

Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def admin_user(db):
    """Superuser with both `is_admin` and `is_superadmin` set."""
    return make_superuser(username="admin-ami", email="admin-ami@example.com")


@pytest.fixture
def artisan_user(db):
    """Non-superuser Account that will own the CreatorProfile."""
    return Account.objects.create_user(
        username="artisan-ami",
        email="artisan-ami@example.com",
        receive_newsletter=False,
        password="a-test-password-1!",
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(user=artisan_user)


def _dashboard_url():
    return reverse("dashboard", kwargs={"subpage": "artisan_messages"})


def _seed_artisan_inbound(artisan_profile, artisan_user, n=2):
    """
    Create `n` unread messages *from the artisan* (i.e. the admin's
    inbound unread). These are the messages the admin's flip should
    clear when they open the thread.

    Seeding from the admin instead would be vacuous: the flip
    `.exclude(sender=request.user)` deliberately leaves the
    admin's own outbound sends untouched, so the flip would be
    a no-op and both tests would pass without exercising anything.
    """
    return [
        ArtisanAdminMessage.objects.create(
            artisan=artisan_profile,
            sender=artisan_user,
            content=f"artisan inbound {i}",
            is_read=False,
        )
        for i in range(1, n + 1)
    ]


# ──────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestArtisanMessagesFlipVsAnnotation:

    def test_active_artisan_row_badge_clears_on_open(
        self, client, admin_user, artisan_user, artisan_profile,
    ):
        """
        Opening the active artisan's thread sets `is_read=True` on
        the artisan-authored unread messages for that artisan.

        Direct regression for the walkthrough catch: the row's
        `unread` count must be 0 in the same response that
        performed the flip — not the pre-flip count.
        """
        _seed_artisan_inbound(artisan_profile, artisan_user, n=2)

        # Sanity: both start unread.
        assert ArtisanAdminMessage.objects.filter(
            artisan=artisan_profile, is_read=False,
        ).count() == 2

        client.force_login(admin_user)
        response = client.get(
            _dashboard_url() + f"?artisan={artisan_profile.id}"
        )

        # 1. Non-error response. A 302 would mean the superadmin
        #    gate fired; a 500 would mean the branch crashed.
        assert response.status_code == 200

        # 2. The flip: both artisan-sent messages are now read.
        assert ArtisanAdminMessage.objects.filter(
            artisan=artisan_profile, is_read=False,
        ).count() == 0
        assert ArtisanAdminMessage.objects.filter(
            artisan=artisan_profile, is_read=True,
        ).count() == 2

        # 3. The ordering pin: the row for the active artisan
        #    reports unread == 0 in the response rendered *after*
        #    the flip.
        rows = response.context["artisan_message_threads"]
        active_row = next(
            r for r in rows if r["artisan"] == artisan_profile.id
        )
        assert active_row["unread"] == 0

    def test_annotation_runs_post_flip(
        self, client, admin_user, artisan_user, artisan_profile,
    ):
        """
        A stronger formulation of the same invariant: the count
        that lands in `artisan_rows` for the active artisan must
        equal the *post-flip* count, not the pre-flip count.

        Seeds 2 unread artisan-authored messages. If the
        annotation ran pre-flip, `unread` would be 2. If the flip
        ran first, it's 0.

        Deliberately does *not* re-assert on `is_read` (test 1
        already pins that); the point is the ordering, in
        isolation.
        """
        _seed_artisan_inbound(artisan_profile, artisan_user, n=2)

        client.force_login(admin_user)
        response = client.get(
            _dashboard_url() + f"?artisan={artisan_profile.id}"
        )
        assert response.status_code == 200

        rows = response.context["artisan_message_threads"]
        active_row = next(
            r for r in rows if r["artisan"] == artisan_profile.id
        )

        # The two admissible values are 0 (flip-then-annotate, the
        # fixed order) and 2 (annotate-then-flip, the bug). Pin 0
        # explicitly so a future reorder to the buggy sequence
        # fails loudly.
        assert active_row["unread"] == 0, (
            "artisan_rows for the active artisan reported "
            f"unread={active_row['unread']}; expected 0 after the "
            "flip. If this regresses to 2, the annotation has been "
            "moved back before the flip."
        )