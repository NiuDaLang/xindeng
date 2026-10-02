# core/signals.py
"""
Image-optimisation signals.

A single registry maps (app_label, model_name, field_name) -> options.
Every registered image field gets a post_save receiver that:
  * skips shared defaults / already-optimised / tiny files
  * processes small files inline
  * pushes large files to Celery (transaction.on_commit)

Processing mode is decided in this order:

  1. If the file is >= INLINE_HARD_CAP_BYTES (20 MB), always async.
     This is a safety valve: a genuinely huge file should not tie up
     a web worker for tens of seconds, regardless of field config.

  2. If the field is registered with `inline_above_threshold=True`,
     always inline. Used for fields whose UI needs the post-pipeline
     result immediately (hero images, featured images) to avoid the
     redirect-then-async race where the page renders before the
     pipeline has updated the DB.

  3. Otherwise, the default: files >= INLINE_SIZE_THRESHOLD_BYTES
     go to Celery; smaller files process inline.

The receiver is idempotent: a guard attribute prevents re-entry when
the save() call from inside the receiver would otherwise fire the
signal again.
"""

from __future__ import annotations

import logging

from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save

from .image_utils import (
    INLINE_SIZE_THRESHOLD_BYTES,
    is_already_optimized,
    is_skippable,
    optimize_image,
    save_optimized_to_field,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Safety valve: above this size, always defer to Celery.
# ──────────────────────────────────────────────────────────────
INLINE_HARD_CAP_BYTES = 20 * 1024 * 1024  # 20 MB


# ──────────────────────────────────────────────────────────────
# Registry — every (app.model, field) pair we want to process.
#
# Per-field options:
#   max_dimension          int   — clamp longest side to this many px
#   quality                int   — WebP/JPEG quality
#   inline_above_threshold bool  — force inline even above
#                                  INLINE_SIZE_THRESHOLD_BYTES
#                                  (subject to INLINE_HARD_CAP_BYTES)
# ──────────────────────────────────────────────────────────────
IMAGE_FIELD_REGISTRY = {
    # ── Store ────────────────────────────────────────────────
    # Hero image: force inline so the editor page renders the
    # optimised .webp immediately after redirect.
    ("store", "product", "images"): {
        "max_dimension": 1600,
        "quality": 82,
        "inline_above_threshold": True,
    },
    # Variation image: same reasoning — the modal returns a fresh
    # card partial that should show the optimised image.
    ("store", "productvariation", "images"): {
        "max_dimension": 1600,
        "quality": 82,
        "inline_above_threshold": True,
    },
    # Gallery images: keep async. Bulk uploads (up to 5 per save)
    # would otherwise block the request for many seconds.
    ("store", "productgallery", "image"): {"max_dimension": 1600, "quality": 82},
    ("store", "productvariationgallery", "image"): {"max_dimension": 1600, "quality": 82},

    # ── Creators ─────────────────────────────────────────────
    # Avatars and QR codes are small enough to stay inline by default.
    ("creators", "creatorprofile", "avatar"):    {"max_dimension": 400,  "quality": 85},
    ("creators", "creatorprofile", "wechat_qr"): {"max_dimension": 800,  "quality": 85},
    # Banner is 2000px wide — a banner upload can easily exceed 1 MB,
    # so leave it async. It renders on the artisan's public page, not
    # immediately after upload, so a small pipeline delay is invisible.
    ("creators", "creatorprofile", "banner"):    {"max_dimension": 2000, "quality": 82},

    # ── Blog ─────────────────────────────────────────────────
    # Featured image: force inline, same reasoning as product hero.
    ("blog", "post", "featured_image"): {
        "max_dimension": 1600,
        "quality": 82,
        "inline_above_threshold": True,
    },

    # ── Accounts ─────────────────────────────────────────────
    ("accounts", "userprofile", "profile_picture"): {"max_dimension": 400, "quality": 85},
    ("accounts", "perk", "featured_image"):         {"max_dimension": 1200, "quality": 82},
    ("accounts", "chatmessage", "image"):           {"max_dimension": 800, "quality": 85},
}


def _process_inline(instance, field_name, opts):
    """Run optimisation synchronously; safe to call from inside post_save."""
    field_file = getattr(instance, field_name)
    if is_skippable(field_file) or is_already_optimized(field_file):
        return

    # Strip our internal control keys before passing to optimize_image.
    clean_opts = {
        k: v for k, v in opts.items()
        if k not in ("inline_above_threshold",)
    }

    result = optimize_image(field_file, **clean_opts)
    if result is None:
        return

    content, new_name = result
    save_optimized_to_field(instance, field_name, content, new_name)

    logger.info(
        "image_utils: inline-optimised %s.%s pk=%s -> %s",
        f"{instance._meta.app_label}.{instance._meta.model_name}",
        field_name, instance.pk, new_name,
    )


def _schedule_async(instance, field_name, opts):
    """Queue a Celery task; runs after the current DB transaction commits."""
    model_label = f"{instance._meta.app_label}.{instance._meta.model_name}"
    pk = instance.pk

    from .tasks import optimize_image_task

    # Strip our internal control keys before passing to the task.
    clean_opts = {
        k: v for k, v in opts.items()
        if k not in ("inline_above_threshold",)
    }

    transaction.on_commit(
        lambda: optimize_image_task.delay(model_label, pk, field_name, clean_opts)
    )
    logger.debug(
        "image_utils: queued async optimisation for %s.%s pk=%s",
        model_label, field_name, pk,
    )


def make_receiver(app_label, model_name, field_name, opts):
    """Build a bound post_save receiver for one specific field."""
    def receiver(sender, instance, created, **kwargs):
        if getattr(instance, "_skip_image_optimization", False):
            return

        field_file = getattr(instance, field_name, None)
        if is_skippable(field_file) or is_already_optimized(field_file):
            return

        try:
            size = field_file.size
        except (OSError, ValueError):
            size = 0

        # ── Rule 1: hard cap — always async above 20 MB ──
        if size and size >= INLINE_HARD_CAP_BYTES:
            _schedule_async(instance, field_name, opts)
            return

        # ── Rule 2: per-field override — force inline ──
        if opts.get("inline_above_threshold", False):
            _process_inline(instance, field_name, opts)
            return

        # ── Rule 3: default — async above 1 MB ──
        if size and size >= INLINE_SIZE_THRESHOLD_BYTES:
            _schedule_async(instance, field_name, opts)
        else:
            _process_inline(instance, field_name, opts)

    receiver.__name__ = f"optimize_{app_label}_{model_name}_{field_name}"
    return receiver


def register_all():
    """Idempotent: connect a receiver per registry entry."""
    for (app_label, model_name, field_name), opts in IMAGE_FIELD_REGISTRY.items():
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            logger.warning(
                "image_utils: model %s.%s not found — skipping field %s",
                app_label, model_name, field_name,
            )
            continue

        if not hasattr(model, field_name):
            logger.warning(
                "image_utils: %s.%s has no field %r — skipping",
                app_label, model_name, field_name,
            )
            continue

        receiver = make_receiver(app_label, model_name, field_name, opts)
        dispatch_uid = f"image_optimize::{app_label}::{model_name}::{field_name}"

        post_save.connect(
            receiver, sender=model,
            dispatch_uid=dispatch_uid, weak=False,
        )
        logger.debug("image_utils: registered %s", dispatch_uid)


register_all()