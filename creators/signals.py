# creators/signals.py
"""
Signal handlers for the creators app.

Currently one handler: upsert the FrontlineThread row on every
ArtisanChatMessage create, and clear the thread's settled_at when a
new message arrives. See the 2026-11-02 handoff §S3 for why this is
a signal rather than a model save() override.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image, UnidentifiedImageError
from .models import ArtisanChatMessage, FrontlineThread
from django.core.exceptions import ValidationError


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


@receiver(pre_save, sender=ArtisanChatMessage)
def validate_artisan_chat_image(sender, instance, **kwargs):
    """
    Reject unreadable image uploads before the row is written.

    The image-optimization pipeline (core.image_utils.optimize_image)
    is deliberately *tolerant*: on UnidentifiedImageError, OSError,
    encode failure, or an "encoded >= original" result it logs and
    returns None — the caller leaves the field untouched. That is the
    right behaviour for optional optimization, but it means a corrupt
    file would otherwise be stored and rendered as a broken <img>
    in the bubble.

    This receiver is the fail-closed counterpart. It opens the
    uploaded file (if present) and loads it through Pillow; if that
    fails, it raises ValidationError before Django's FieldFile has
    committed the bytes to storage. The three view call sites
    (creators.views.customer_thread_send,
    creators.views.dashboard_messages_send,
    accounts.views.frontline_message_send) catch the exception and
    surface a user-visible error.

    The receiver deliberately does NOT close the file handle.
    Closing would break Django's FileField.pre_save,
    which streams the bytes to storage immediately after this receiver
    returns (see the 3f-bis test run that surfaced the initial
    'I/O operation on closed file' bug).
    The pipeline's own finally block (post_save) is the correct place to close,
    and that same pipeline handles the write-back save by setting
    instance._skip_image_optimization, which this receiver honours
    as an early return.

    Registered in CreatorsConfig.ready() via `from . import signals`
    — same discipline as maintain_frontline_thread (handoff §F10).
    Do not move this to a module-level handler in models.py.
    """
    image = getattr(instance, "image", None)
    if not image or not getattr(image, "name", ""):
        # No image attached — nothing to validate. This is the common
        # case (text-only messages) and must remain a fast no-op.
        return

    # Skip when this save is the image optimizer's own write-back.
    # save_optimized_to_field sets _skip_image_optimization=True
    # around its instance.save(update_fields=["image"]), and the
    # optimizer has ALREADY:
    #   * opened the original upload,
    #   * validated it via Image.open().load(),
    #   * encoded it to WebP,
    #   * written the .webp file,
    #   * closed the handle in its finally block.
    # Re-opening the (now-closed) handle here crashes with
    # ValueError: seek of closed file. The pipeline is not a new
    # upload; trust it and skip validation.
    if getattr(instance, "_skip_image_optimization", False):
        return

    try:
        img = Image.open(image)
        img.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValidationError(
            "The attached file is not a readable image.｜"
            "所附加的檔案不是可讀取的圖片。"
            f" ({exc.__class__.__name__})"
        )

    # Do NOT close the file here. Django's FileField.pre_save will
    # stream the bytes to storage after this receiver returns, and it
    # needs the handle to stay open. seek(0) is safe (and free) but
    # not strictly required for InMemoryUploadedFile; keeping it for
    # clarity in case an upstream caller has read the stream.
    try:
        image.seek(0)
    except Exception:
        pass