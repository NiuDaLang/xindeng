# creators/signals.py
"""
Signal handlers for the creators app.

Currently one handler: upsert the FrontlineThread row on every
ArtisanChatMessage create, and clear the thread's settled_at when a
new message arrives. See the 2026-11-02 handoff §S3 for why this is
a signal rather than a model save() override.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ArtisanChatMessage, FrontlineThread


@receiver(post_save, sender=ArtisanChatMessage)
def maintain_frontline_thread(sender, instance, created, **kwargs):
    """
    Upsert the FrontlineThread for this message's (artisan, customer,
    order_product) triple, and refresh last_message_at.

    On create (created=True):
      * get_or_create the thread; no-op if order_product is None
        (legacy pre-Frontline messages, or a message the (now
        disallowed) pre-purchase path could theoretically have
        created).
      * set thread.last_message_at to max(existing, message.created_at)
        — always advances.
      * clear thread.settled_at / settled_by — new message unsettles
        the thread.

    On update (created=False):
      * only refresh last_message_at if the message's created_at is
        somehow newer than the thread's (rare; exists as a safety
        net for out-of-order writes, e.g. backfills). Do NOT clear
        settled_at on updates — the message body changing does not
        constitute new activity.

    The signal lives in creators.signals and is registered by
    creators.apps.CreatorProfileConfig.ready(). The registration is
    inside the app config so it fires exactly once regardless of
    import order.
    """
    if instance.order_product_id is None:
        # Pre-purchase or legacy message — no thread.
        return

    thread, thread_created = FrontlineThread.objects.get_or_create(
        artisan=instance.artisan,
        customer=instance.customer,
        order_product=instance.order_product,
        defaults={
            "last_message_at": instance.created_at,
        },
    )

    update_fields = []

    # Always advance last_message_at, never retreat.
    if (
        thread.last_message_at is None
        or instance.created_at > thread.last_message_at
    ):
        thread.last_message_at = instance.created_at
        update_fields.append("last_message_at")

    # On create: unsettle. On update: leave as-is.
    if created and thread.settled_at is not None:
        thread.settled_at = None
        thread.settled_by = None
        update_fields.extend(["settled_at", "settled_by"])

    if update_fields:
        update_fields.append("updated_at")
        thread.save(update_fields=update_fields)