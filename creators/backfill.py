# creators/migrations/backfill.py
"""
Lives in creators/ rather than creators/migrations/ because Django's
migration loader imports every non-underscore module in the
migrations package and requires each to define a Migration class.
run_backfill is consumed by both 0017_backfill_frontline_threads
(via RunPython) and creators/tests/test_backfill_frontline_threads.py
(directly), so it needs to be importable without being part of the
migration package.

Backfill FrontlineThread rows for order-scoped ArtisanChatMessage
rows that predate creators/migrations/0014_frontlinethread.py — or
that were inserted by a code path that bypassed the post_save
signal (shell, test, script).

Scope, precisely:

  * IN SCOPE:
      Distinct (artisan, customer, order_product) triples present
      on ArtisanChatMessage where order_product is non-null AND
      no FrontlineThread exists for that triple. Exactly one thread
      is created per missing triple, with last_message_at set to
      MAX(ArtisanChatMessage.created_at).

  * OUT OF SCOPE, deliberately:

      - Messages with order_product=NULL. These are unreachable
        through the UI: the customer thread composer posts a
        hidden order_product_id (see
        templates/artisans/dashboard/partials/_customer_thread_body.html
        and the DevTools screenshot from the 2026-11-26 session).
        Pre-purchase / general queries route through the Contact
        Us desk, not the customer↔artisan thread. If such rows
        exist in the DB they are anomalies, and the admin
        oversight panel is the wrong place to surface them. The
        signal (creators.signals.maintain_frontline_thread)
        short-circuits on NULL, and the FrontlineThread unique
        constraint is over non-null fields. Do not create a
        thread for a NULL-order message.

      - Messages whose OrderProduct has since been deleted.
        ArtisanChatMessage.order_product is SET_NULL; once the
        line is gone, the message carries NULL and is caught by
        the rule above. FrontlineThread.order_product is CASCADE,
        so any existing thread went with the line. This is the
        documented asymmetry (2026-11-02 handoff §S2), and the
        migration respects it by doing nothing.

  * BACKFILLED STATE:

      - last_message_at: MAX(ArtisanChatMessage.created_at) for
        the triple. Matches the signal's "always advances, never
        retreats" rule.

      - settled_at, settled_by, escalated_at, escalated_by: NULL.
        The thread did not exist to be actioned; fabricating an
        audit timestamp would be wrong (gotcha-113 class).

  * RECONCILIATION SCOPE (locked 2026-11-26):

      Create-only. Existing threads' last_message_at is trusted
      as-is — the signal advances it on every new message and
      never retreats, so drift on an existing thread implies a
      signal bug, not a backfill gap. If the following query
      returns rows on production after this migration runs, that
      is a signal bug to investigate — not something to paper
      over with a blanket UPDATE here:

          SELECT ft.id, ft.last_message_at, MAX(acm.created_at)
          FROM   creators_frontlinethread ft
          JOIN   creators_artisanchatmessage acm
            ON   acm.artisan_id       = ft.artisan_id
            AND  acm.customer_id      = ft.customer_id
            AND  acm.order_product_id = ft.order_product_id
          GROUP BY ft.id, ft.last_message_at
          HAVING MAX(acm.created_at) <> ft.last_message_at;

  * REVERSIBILITY: none (RunPython.noop). A backfill that has been
    live for a week cannot be safely undone: an admin may have
    settled or escalated a backfilled thread by then, and
    deleting the thread would destroy that audit state. Accept
    the one-way door.

  * SIGNALS: FrontlineThread has no post_save receiver today
    (the auto-maintenance signal lives on ArtisanChatMessage —
    see creators/signals.py::maintain_frontline_thread).
    bulk_create therefore bypasses nothing. If a future
    maintainer adds a FrontlineThread post_save, add a hand-off
    in this file so the backfill's write path stays auditable.

  * FRESH-DB SAFETY: on a fresh database this is a no-op.
"""

from django.db.models import Max


def run_backfill(apps):
    """
    Reconcile missing FrontlineThread rows. Extracted as a sibling
    so creators/tests/test_backfill_frontline_threads.py can call
    the exact function the migration runs, with the live app
    registry, without going through the migration machinery.

    `apps` is a Django app registry — either the historical one
    passed by RunPython, or django.apps.apps in tests. Both expose
    get_model("app_label", "ModelName"), which is the only API
    this function touches.
    """
    ArtisanChatMessage = apps.get_model("creators", "ArtisanChatMessage")
    FrontlineThread = apps.get_model("creators", "FrontlineThread")

    # One query: distinct triples + MAX(created_at) per triple.
    # .order_by() clears the model Meta.ordering (created_at) so
    # the GROUP BY is not polluted by a stray sort column.
    triples = (
        ArtisanChatMessage.objects
        .filter(order_product__isnull=False)
        .values("artisan_id", "customer_id", "order_product_id")
        .annotate(last_at=Max("created_at"))
        .order_by()
    )

    existing = set(
        FrontlineThread.objects.values_list(
            "artisan_id", "customer_id", "order_product_id",
        )
    )

    to_create = [
        FrontlineThread(
            artisan_id=t["artisan_id"],
            customer_id=t["customer_id"],
            order_product_id=t["order_product_id"],
            last_message_at=t["last_at"],
            # settled_at / escalated_at / *_by intentionally left
            # NULL — see module docstring.
        )
        for t in triples
        if (
            t["artisan_id"],
            t["customer_id"],
            t["order_product_id"],
        ) not in existing
    ]

    if to_create:
        # batch_size=200 keeps multi-row INSERTs under SQLite's
        # historical 999-param ceiling (4 cols × 200 = 800 params)
        # while remaining efficient on Postgres. Adjust only if
        # the param count per row ever grows.
        FrontlineThread.objects.bulk_create(to_create, batch_size=200)


def backfill_frontline_threads(apps, schema_editor):
    run_backfill(apps)
