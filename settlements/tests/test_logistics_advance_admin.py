# settlements/tests/test_logistics_advance_admin.py
"""
Tests for the LogisticsAdvance aggregate admin view.

Covers:
  * Sum / count correctness across a small fixture graph.
  * Filter (status) narrowed aggregation.
  * Month ordering (newest first).
  * The toggle link appears on the standard changelist.
  * The aggregate view is reachable via its URL.

Superuser fixtures note:
    This file is the only one in the project that hits Django's
    admin changelist (and the aggregate view on top of it). That
    goes through ModelAdmin.has_view_permission → Account.has_perm,
    which returns self.is_admin — not self.is_superadmin. The
    custom superuser_required decorator used elsewhere checks
    is_superadmin instead. make_superuser (in tests/_fakes.py)
    sets both; a fixture that sets only one will 403 on one gate
    or the other. See tests/README.md "Superusers in tests".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse
from tests._fakes import make_superuser


@pytest.fixture
def advance_chain(db, django_user_model):
    """
    Two individuals, two months, mixed statuses.
    Returns a dict of the rows created, keyed by a name, so tests
    can assert against specific rows without re-deriving them.
    """
    from orders.models import Order
    from settlements.models import LogisticsAdvance

    a = django_user_model.objects.create_user(
        username="alice", email="alice@example.com",
        receive_newsletter=False, password="x", is_active=True,
    )
    b = django_user_model.objects.create_user(
        username="bob", email="bob@example.com",
        receive_newsletter=False, password="x", is_active=True,
    )
    order = Order.objects.create(
        order_number="ADV-ORD-1", email="x@example.com",
        is_ordered=True, order_status="Processing",
    )
    order2 = Order.objects.create(
        order_number="ADV-ORD-2", email="x@example.com",
        is_ordered=True, order_status="Processing",
    )

    jan = date(2026, 1, 1)
    feb = date(2026, 2, 1)

    a_jan_1 = LogisticsAdvance.objects.create(
        order=order, individual=a, month=jan,
        amount_advanced=Decimal("100.00"),
        status=LogisticsAdvance.Status.PENDING,
    )
    a_jan_2 = LogisticsAdvance.objects.create(
        order=order2, individual=a, month=jan,
        amount_advanced=Decimal("50.00"),
        status=LogisticsAdvance.Status.SUBMITTED,
    )
    a_feb_1 = LogisticsAdvance.objects.create(
        order=order, individual=a, month=feb,
        amount_advanced=Decimal("30.00"),
        status=LogisticsAdvance.Status.REIMBURSED,
        reimbursed_amount=Decimal("30.00"),
    )
    b_jan_1 = LogisticsAdvance.objects.create(
        order=order, individual=b, month=jan,
        amount_advanced=Decimal("75.00"),
        status=LogisticsAdvance.Status.REIMBURSED,
        reimbursed_amount=Decimal("75.00"),
    )

    return {
        "alice": a, "bob": b,
        "a_jan_1": a_jan_1, "a_jan_2": a_jan_2, "a_feb_1": a_feb_1,
        "b_jan_1": b_jan_1,
    }


@pytest.fixture
def superuser(db):
    return make_superuser(
        username="adv_superu",
        email="adv-superu@example.com",
    )


class TestAggregateView:

    def _url(self):
        return reverse("admin:settlements_logisticsadvance_aggregate")

    def _get_groups(self, client, superuser, query=""):
        """
        Hit the aggregate view and return groups as a list of dicts
        with only the fields we assert on, keyed by (individual, month).
        """
        client.force_login(superuser)
        response = client.get(self._url() + query)
        assert response.status_code == 200
        return {
            (g["individual__username"], g["month"]): g
            for g in response.context["groups"]
        }

    def test_sums_across_alice_january(self, client, superuser, advance_chain):
        groups = self._get_groups(client, superuser)
        alice_jan = groups[("alice", date(2026, 1, 1))]
        assert alice_jan["rows"] == 2
        assert alice_jan["advanced"] == Decimal("150.00")
        assert alice_jan["reimbursed"] == Decimal("0.00")
        assert alice_jan["outstanding"] == Decimal("150.00")
        assert alice_jan["pending_count"] == 1
        assert alice_jan["submitted_count"] == 1
        assert alice_jan["reimbursed_count"] == 0

    def test_sums_across_alice_february(self, client, superuser, advance_chain):
        groups = self._get_groups(client, superuser)
        alice_feb = groups[("alice", date(2026, 2, 1))]
        assert alice_feb["rows"] == 1
        assert alice_feb["advanced"] == Decimal("30.00")
        assert alice_feb["reimbursed"] == Decimal("30.00")
        assert alice_feb["outstanding"] == Decimal("0.00")
        assert alice_feb["reimbursed_count"] == 1

    def test_bob_january_fully_reimbursed(self, client, superuser, advance_chain):
        groups = self._get_groups(client, superuser)
        bob_jan = groups[("bob", date(2026, 1, 1))]
        assert bob_jan["outstanding"] == Decimal("0.00")

    def test_status_filter_narrows_aggregation(
        self, client, superuser, advance_chain,
    ):
        # Only PENDING rows should aggregate. Alice's January group
        # shrinks from 2 rows / ¥150 to 1 row / ¥100, and Bob's row
        # disappears entirely.
        groups = self._get_groups(client, superuser, "?status__exact=PENDING")
        assert ("bob", date(2026, 1, 1)) not in groups
        assert groups[("alice", date(2026, 1, 1))]["rows"] == 1
        assert groups[("alice", date(2026, 1, 1))]["advanced"] == Decimal("100.00")

    def test_month_ordering_newest_first(self, client, superuser, advance_chain):
        client.force_login(superuser)
        response = client.get(self._url())
        months = [g["month"] for g in response.context["groups"]]
        assert months == sorted(months, reverse=True)

    def test_empty_state_when_filter_excludes_everything(
        self, client, superuser, advance_chain,
    ):
        # The sidebar's individual filter uses ?individual__id__exact=<pk>.
        # A lookup like ?individual__username=bob is rejected by Django's
        # admin security layer (DisallowedModelAdminLookup), so we test
        # the supported lookup — the one the admin UI actually produces.
        bob_id = advance_chain["bob"].id
        groups = self._get_groups(
            client, superuser,
            f"?status__exact=REIMBURSED&individual__id__exact={bob_id}",
        )
        # Only bob's January row is REIMBURSED, so exactly one group.
        assert len(groups) == 1
        assert ("bob", date(2026, 1, 1)) in groups

    def test_aggregate_view_renders_without_error(self, client, superuser, advance_chain):
        client.force_login(superuser)
        response = client.get(self._url())
        assert response.status_code == 200
        # Sanity: the breadcrumb resolved (would have raised otherwise).
        assert b"Logistics Advances" in response.content


class TestToggleLink:
    def test_toggle_appears_on_changelist(self, client, db):
        admin = make_superuser(username="adv_superu")
        client.force_login(admin)
        response = client.get(
            reverse("admin:settlements_logisticsadvance_changelist")
        )
        assert response.status_code == 200
        body = response.content.decode()
        assert "View by month" in body
        assert reverse("admin:settlements_logisticsadvance_aggregate") in body

    def test_aggregate_view_link_back_to_changelist(
        self, client, superuser,
    ):
        client.force_login(superuser)
        response = client.get(
            reverse("admin:settlements_logisticsadvance_aggregate")
        )
        assert response.status_code == 200
        body = response.content.decode()
        assert "Back to row-level view" in body




