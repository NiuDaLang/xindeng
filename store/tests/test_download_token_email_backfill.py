# store/tests/test_download_token_email_backfill.py
"""
Data migration test for the two store migrations that make
DigitalDownloadToken user-nullable and snapshot the buyer's email
onto the token:

    0039_digital_download_token_email
        AddField: email (EmailField, blank=True, default="")
        RunPython: backfill email from order_product.order.email

    0040_digital_download_token_user_nullable
        AlterField: user (null=True, blank=True)

Seeds member orders and tokens at the pre-migration state (0038),
migrates forward, and asserts:

    * The backfill populated token.email from the parent order's email.
    * A null Order.email backfills to "" (defensive — checkout requires
      an email in practice, but the field must not crash on legacy rows).
    * Tokens with user=None can now be created (user is nullable).
      This is the whole point of #7.5.

Uses TransactionTestCase because schema-altering migrations cannot be
run inside the TestCase transaction wrapper.

Design note on model resolution
--------------------------------
Only DigitalDownloadToken is resolved through the historical app
registry, because only its schema changes between 0038 and 0040.
Everything else uses the current model classes.

Reason: Django's historical-model construction drops managers whose
`use_in_migrations` is False and does not re-add a default `objects`
in their place. The current Product model defines
`products = ProductManager()` and `objects = Manager()`, neither of
which opts in, so the historical Product class has no `.objects`.
Using current classes avoids this without giving up anything —
Product/Category/etc. are unchanged across the two migrations.

FK values into the historical DigitalDownloadToken are passed by
`*_id` rather than by instance. Django's FK descriptor checks
`isinstance(value, self.field.remote_field.model)`, and a
current-model instance is not an instance of the historical class.
Passing the raw PK sidesteps that check.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class TestDownloadTokenEmailBackfill(TransactionTestCase):
    migrate_from = [("store", "0038_vaultuploadreviewlog")]
    migrate_to = [("store", "0040_digital_download_token_user_nullable")]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        self._seed(old_apps)

        # build_graph() forces the loader to re-read the migrations
        # directory now that 0039/0040 exist on disk.
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(self.migrate_to)
        self.new_apps = executor.loader.project_state(self.migrate_to).apps

    def _seed(self, apps):
        # See module docstring: current models for everything except
        # DigitalDownloadToken, whose schema is under test.
        Account = get_user_model()
        from category.models import Category
        from store.models import Product, ProductVariation
        from orders.models import Order, OrderProduct

        DigitalDownloadToken = apps.get_model("store", "DigitalDownloadToken")

        member = Account.objects.create(
            username="backfill_member",
            email="member@example.com",
            password="!",  # unusable; we never authenticate here
            is_active=True,
        )
        category = Category.objects.create(
            category_name="Backfill Cat",
            slug="backfill-cat",
            product_format="e-product",
        )
        product = Product.objects.create(
            product_name="Backfill Ebook",
            slug="backfill-ebook",
            category=category,
            is_digital=True,
            digital_fulfillment_type="INSTANT",
            is_physical=False,
            is_active=True,
            status="Published",
        )
        variation = ProductVariation.objects.create(
            product=product,
            price=Decimal("10.00"),
            stock=1,
            is_available=True,
        )

        # ── Case 1: member order with a real email ────────────────
        member_order = Order.objects.create(
            user=member,
            order_number="BACKFILL-MEMBER-1",
            email="member-buyer@example.com",
            is_ordered=True,
            order_status="Processing",
        )
        member_op = OrderProduct.objects.create(
            order=member_order,
            user=member,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
        )
        DigitalDownloadToken.objects.create(
            user_id=member.pk,
            order_product_id=member_op.pk,
            expires_at=timezone.now() + timedelta(days=7),
        )

        # ── Case 2: order whose email is None ─────────────────────
        null_email_order = Order.objects.create(
            user=member,
            order_number="BACKFILL-NULL-EMAIL-1",
            email=None,
            is_ordered=True,
            order_status="Processing",
        )
        null_email_op = OrderProduct.objects.create(
            order=null_email_order,
            user=member,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
        )
        DigitalDownloadToken.objects.create(
            user_id=member.pk,
            order_product_id=null_email_op.pk,
            expires_at=timezone.now() + timedelta(days=7),
        )

    # ─────────────────────────────────────────────────────────────
    # Backfill correctness
    # ─────────────────────────────────────────────────────────────

    def test_member_token_email_backfilled_from_order(self):
        DigitalDownloadToken = self.new_apps.get_model("store", "DigitalDownloadToken")
        token = DigitalDownloadToken.objects.get(
            order_product__order__order_number="BACKFILL-MEMBER-1"
        )
        assert token.email == "member-buyer@example.com"

    def test_null_order_email_backfills_to_empty_string(self):
        DigitalDownloadToken = self.new_apps.get_model("store", "DigitalDownloadToken")
        token = DigitalDownloadToken.objects.get(
            order_product__order__order_number="BACKFILL-NULL-EMAIL-1"
        )
        assert token.email == ""

    # ─────────────────────────────────────────────────────────────
    # Nullability contract
    # ─────────────────────────────────────────────────────────────

    def test_guest_token_can_now_be_created_with_user_none(self):
        from store.models import Product, ProductVariation
        from orders.models import Order, OrderProduct

        DigitalDownloadToken = self.new_apps.get_model("store", "DigitalDownloadToken")

        product = Product.objects.get(slug="backfill-ebook")
        variation = ProductVariation.objects.get(product=product)

        guest_order = Order.objects.create(
            user=None,
            order_number="BACKFILL-GUEST-1",
            email="guest-buyer@example.com",
            is_ordered=True,
            order_status="Processing",
        )
        guest_op = OrderProduct.objects.create(
            order=guest_order,
            user=None,
            product=product,
            product_variation=variation,
            product_price=Decimal("10.00"),
            quantity=1,
            ordered=True,
        )
        token = DigitalDownloadToken.objects.create(
            user_id=None,
            email="guest-buyer@example.com",
            order_product_id=guest_op.pk,
            expires_at=timezone.now() + timedelta(days=7),
        )
        assert token.user_id is None
        assert token.email == "guest-buyer@example.com"

    def test_existing_member_token_still_has_its_user(self):
        """Regression guard: the AlterField must not drop existing FKs."""
        DigitalDownloadToken = self.new_apps.get_model("store", "DigitalDownloadToken")
        token = DigitalDownloadToken.objects.get(
            order_product__order__order_number="BACKFILL-MEMBER-1"
        )
        assert token.user_id is not None