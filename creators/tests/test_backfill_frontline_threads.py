# creators/tests/test_backfill_frontline_threads.py
"""
Tests for creators/migrations/0017_backfill_frontline_threads.py.

The migration's job, per the 2026-11-26 clarification and the
module docstring of 0017, is narrow:

  * Create FrontlineThread rows for order-scoped ArtisanChatMessage
    triples that have no thread. This happens when messages predate
    0014_frontlinethread.py or were inserted by a code path that
    bypassed the post_save signal (shell, test, script).

  * Do nothing else. NULL-order messages are not threaded. Deleted-
    order messages (whose order_product has already flipped to NULL
    via SET_NULL) are not threaded. Existing threads are not
    touched (create-only reconciliation, locked 2026-11-26). Audit
    fields (settled_at, escalated_at) are never fabricated.

`run_backfill(apps)` is called directly with the live app registry
(django.apps.apps) rather than via the migration machinery. The
migration is a thin RunPython wrapper around the same function, so
the reconciliation logic — which is the interesting part — is
under test without the cost and fragility of calling migrate()
inside a test. Django's own migration runner is responsible for
"migrate ran"; this file is responsible for "run_backfill does the
right thing."

Every orphan-case test must suppress the
creators.signals.maintain_frontline_thread receiver while creating
the orphan message; otherwise the signal would create the thread
for us and the backfill would find nothing to do. The project's
test idiom is post_save.disconnect / reconnect in a try/finally —
see test_artisan_admin_messages_htmx.py for precedent.

The fixture chain (customer, artisan_profile, order_product) is
copied from creators/tests/test_frontline_thread.py rather than
imported: the project's tests are deliberately self-contained so
each file reads top-to-bottom without cross-file chasing. See the
module docstring of test_artisan_message_fks.py.
"""

import pytest
from django.apps import apps as live_apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from category.models import Category
from creators.models import (
    ArtisanChatMessage,
    CreatorProfile,
    FrontlineThread,
)
from creators.signals import maintain_frontline_thread
from orders.models import Order, OrderProduct
from store.models import Product, ProductVariation

import importlib
backfill_migration = importlib.import_module(
    "creators.migrations.0017_backfill_frontline_threads"
)
run_backfill = backfill_migration.run_backfill


Account = get_user_model()


# ──────────────────────────────────────────────────────────────
# Fixtures (mirrors test_frontline_thread.py)
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def customer(db):
    return Account.objects.create_user(
        username="fl-customer",
        email="fl-customer@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_user(db):
    return Account.objects.create_user(
        username="fl-artisan",
        email="fl-artisan@example.com",
        receive_newsletter=False,
        password="x",
        is_active=True,
    )


@pytest.fixture
def artisan_profile(artisan_user):
    return CreatorProfile.objects.create(
        user=artisan_user,
        display_name="FL Artisan",
        is_verified=True,
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        category_name="FL Category", slug="fl-category",
    )


@pytest.fixture
def product(category, artisan_profile):
    return Product.objects.create(
        product_name="FL Product", slug="fl-product",
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
        order_number="FL-ORDER-0001",
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


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _create_orphan_message(**kwargs):
    """
    Create an ArtisanChatMessage with the frontline-thread signal
    temporarily disconnected. Returns the created message; no
    FrontlineThread is created as a side effect.
    """
    post_save.disconnect(
        maintain_frontline_thread, sender=ArtisanChatMessage,
    )
    try:
        return ArtisanChatMessage.objects.create(**kwargs)
    finally:
        post_save.connect(
            maintain_frontline_thread, sender=ArtisanChatMessage,
        )


# ──────────────────────────────────────────────────────────────
# Create-only reconciliation — the primary path
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBackfillCreatesMissingThreads:

    def test_orphan_message_gets_a_thread(
        self, customer, artisan_profile, order_product,
    ):
        msg = _create_orphan_message(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="orphan",
            order_product=order_product,
        )
        assert FrontlineThread.objects.count() == 0  # precondition

        run_backfill(live_apps)

        thread = FrontlineThread.objects.get()
        assert thread.artisan_id == artisan_profile.id
        assert thread.customer_id == customer.id
        assert thread.order_product_id == order_product.id
        assert thread.last_message_at == msg.created_at

    def test_multiple_orphan_messages_on_same_triple_get_one_thread(
        self, customer, artisan_profile, artisan_user, order_product,
    ):
        first = _create_orphan_message(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="first",
            order_product=order_product,
        )
        second = _create_orphan_message(
            artisan=artisan_profile, customer=customer,
            sender=artisan_user, content="second",
            order_product=order_product,
        )
        assert FrontlineThread.objects.count() == 0
        assert second.created_at > first.created_at

        run_backfill(live_apps)

        assert FrontlineThread.objects.count() == 1
        thread = FrontlineThread.objects.get()
        assert thread.last_message_at == second.created_at


# ──────────────────────────────────────────────────────────────
# Out-of-scope guarantees — the assertions that pin the design
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBackfillOutOfScope:

    def test_null_order_product_message_gets_no_thread(
        self, customer, artisan_profile,
    ):
        """
        A message without an order_product is unreachable through
        the UI (the composer always posts a hidden order_product_id;
        pre-purchase queries go through Contact Us). If one exists
        in the DB, it is a data anomaly and must NOT be surfaced
        in the admin Frontline panel.
        """
        ArtisanChatMessage.objects.create(
            artisan=artisan_profile,
            customer=customer,
            sender=customer,
            content="anomalous pre-order message",
            order_product=None,
        )
        assert FrontlineThread.objects.count() == 0  # signal skipped too

        run_backfill(live_apps)

        assert FrontlineThread.objects.count() == 0

    def test_orphan_whose_order_product_was_deleted_gets_no_thread(
        self, customer, artisan_profile, order_product,
    ):
        """
        order_product on ArtisanChatMessage is SET_NULL: deleting
        the line flips the message's FK to NULL. The message is
        then caught by the null-order rule above. FrontlineThread
        .order_product is CASCADE, so any existing thread went with
        the line — deliberate asymmetry, see 2026-11-02 handoff §S2.
        """
        _create_orphan_message(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="orphan-then-deleted",
            order_product=order_product,
        )
        assert FrontlineThread.objects.count() == 0

        order_product.delete()

        run_backfill(live_apps)

        assert FrontlineThread.objects.count() == 0


# ──────────────────────────────────────────────────────────────
# Idempotency and no-fabrication
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBackfillIdempotency:

    def test_existing_thread_is_not_duplicated(
        self, customer, artisan_profile, order_product,
    ):
        """
        Create a thread the normal way (signal fires), then run
        the backfill. The backfill must be a no-op for existing
        triples: no duplicate row, no last_message_at overwrite.
        """
        msg = ArtisanChatMessage.objects.create(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="via signal",
            order_product=order_product,
        )
        thread = FrontlineThread.objects.get()
        assert thread.last_message_at == msg.created_at

        run_backfill(live_apps)

        assert FrontlineThread.objects.count() == 1
        thread.refresh_from_db()
        assert thread.last_message_at == msg.created_at

    def test_running_twice_is_a_noop(
        self, customer, artisan_profile, order_product,
    ):
        _create_orphan_message(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="orphan",
            order_product=order_product,
        )
        run_backfill(live_apps)
        assert FrontlineThread.objects.count() == 1

        # Second run: existing set catches it.
        run_backfill(live_apps)
        assert FrontlineThread.objects.count() == 1

    def test_empty_db_is_a_noop(self):
        assert FrontlineThread.objects.count() == 0
        run_backfill(live_apps)
        assert FrontlineThread.objects.count() == 0


# ──────────────────────────────────────────────────────────────
# Audit-field non-fabrication
# ──────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestBackfillAuditFields:

    def test_backfill_does_not_set_audit_fields(
        self, customer, artisan_profile, order_product,
    ):
        """
        A backfilled thread was never settled or escalated —
        fabricating audit timestamps would be wrong (gotcha-113
        class). All four audit fields must be NULL after backfill.
        """
        _create_orphan_message(
            artisan=artisan_profile, customer=customer,
            sender=customer, content="orphan",
            order_product=order_product,
        )

        run_backfill(live_apps)

        thread = FrontlineThread.objects.get()
        assert thread.settled_at is None
        assert thread.settled_by is None
        assert thread.escalated_at is None
        assert thread.escalated_by is None