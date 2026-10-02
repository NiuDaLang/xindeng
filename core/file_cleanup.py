# core/file_cleanup.py
"""
Automatic cleanup of superseded FileField/ImageField files.

Covers three lifecycle events:
  * Field replacement  (user uploads a new image; old one should be deleted)
  * Model deletion     (row is deleted; its files should be deleted)
  * Field cleared      (user checks the clear checkbox; file should be deleted)

Two registries are provided:
  * REPLACE_CLEANUP_FIELDS  — fields to monitor for replacement/clearing
  * DELETE_CLEANUP_FIELDS   — fields to monitor for row deletion

Deletion is defensive: it only removes files inside MEDIA_ROOT, and only
if no other DB row still references the same path.
"""

from __future__ import annotations

import logging
import os

from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Registries
# ──────────────────────────────────────────────────────────────
#
# Format: (app_label, model_name, field_name) tuples.
#
# REPLACE_CLEANUP_FIELDS: when the field's value changes (new upload,
# or cleared), delete the previous file if it's no longer referenced.
#
# DELETE_CLEANUP_FIELDS: when the row is deleted, delete the field's file.
#
# The two lists often overlap — most image fields should be in both.

REPLACE_CLEANUP_FIELDS = [
    # Store
    ("store", "product",                  "images"),
    ("store", "productvariation",         "images"),
    ("store", "productgallery",           "image"),
    ("store", "productvariationgallery",  "image"),

    # Creators
    ("creators", "creatorprofile", "avatar"),
    ("creators", "creatorprofile", "banner"),
    ("creators", "creatorprofile", "wechat_qr"),

    # Blog
    ("blog", "post", "featured_image"),

    # Accounts
    ("accounts", "userprofile", "profile_picture"),
    ("accounts", "perk", "featured_image"),
    ("accounts", "chatmessage", "image"),

    # category
    ("category", "category", "cat_image"),

    # reviews
    ("reviews", "commentimage", "image"),
]

# Same set for delete cleanup. Kept as a separate list so you can tune
# them independently (e.g. keep avatars around for audit, delete products).
DELETE_CLEANUP_FIELDS = list(REPLACE_CLEANUP_FIELDS)


# ──────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────

def _is_under_media_root(path: str) -> bool:
    """Safety check: only ever delete files inside MEDIA_ROOT."""
    try:
        media_root = os.path.abspath(str(settings.MEDIA_ROOT))
        abs_path = os.path.abspath(path)
        return abs_path.startswith(media_root + os.sep)
    except Exception:
        return False


def _is_still_referenced(model, field_name, storage_name: str) -> bool:
    """
    Return True if any row other than the current one still points at this
    file. Prevents deleting a file that's shared (rare, but possible if
    someone intentionally reused a path).
    """
    if not storage_name:
        return False
    return model.objects.filter(**{field_name: storage_name}).exists()


def _safe_delete_file(model, field_name, storage_name: str, *, reason: str = ""):
    """
    Delete a file from storage, with safety guards:
      - Only inside MEDIA_ROOT
      - Only if not still referenced by another row
      - Log and swallow errors (cleanup must never break a save/delete)
    """
    if not storage_name:
        return

    if _is_still_referenced(model, field_name, storage_name):
        logger.debug(
            "file_cleanup: skipping %s — still referenced by another row",
            storage_name,
        )
        return

    # NEW: invalidate dimension cache for this file.
    from .image_utils import invalidate_image_dimensions_cache
    invalidate_image_dimensions_cache(storage_name)

    try:
        storage = model._meta.get_field(field_name).storage
    except Exception:
        logger.warning("file_cleanup: cannot resolve storage for %s", field_name)
        return

    try:
        if hasattr(storage, "path"):
            full_path = storage.path(storage_name)
            if not _is_under_media_root(full_path):
                logger.warning(
                    "file_cleanup: refusing to delete %s (outside MEDIA_ROOT)",
                    full_path,
                )
                return
        storage.delete(storage_name)
        logger.info(
            "file_cleanup: deleted %s (%s)", storage_name, reason or "unspecified",
        )
    except Exception as exc:
        logger.warning(
            "file_cleanup: could not delete %s (%s): %s",
            storage_name, reason or "unspecified", exc,
        )


# ──────────────────────────────────────────────────────────────
# Signal handlers
# ──────────────────────────────────────────────────────────────

def _make_pre_save_tracker(app_label, model_name, field_name):
    """
    pre_save: snapshot the *current* DB value of the field so post_save
    can compare. We do this by re-fetching from the DB rather than
    trusting `instance.<field>` (which may already have the new value
    if the caller mutated it in memory).
    """
    def handler(sender, instance, **kwargs):
        if not instance.pk:
            # New row — nothing to compare against.
            instance._cleanup_old_file = None
            return

        try:
            old_instance = sender.objects.only(field_name).get(pk=instance.pk)
            old_file = getattr(old_instance, field_name)
            old_name = old_file.name if old_file and old_file.name else None
        except sender.DoesNotExist:
            old_name = None
        except Exception as exc:
            logger.debug(
                "file_cleanup: pre_save snapshot failed for %s.%s pk=%s: %s",
                app_label, model_name, instance.pk, exc,
            )
            old_name = None

        instance._cleanup_old_file = old_name

    handler.__name__ = f"pre_save_track_{app_label}_{model_name}_{field_name}"
    return handler


def _make_post_save_cleanup(app_label, model_name, field_name):
    """
    post_save: if the field's value changed, delete the old file.

    Runs after the DB write succeeds, so a failure here doesn't roll
    back the user's upload. Uses transaction.on_commit so the deletion
    only happens if the outer transaction (if any) commits.
    """
    def handler(sender, instance, created, **kwargs):
        old_name = getattr(instance, "_cleanup_old_file", None)
        if not old_name:
            return

        try:
            new_file = getattr(instance, field_name)
            new_name = new_file.name if new_file and new_file.name else None
        except Exception:
            new_name = None

        # Nothing to do if the path didn't change.
        if old_name == new_name:
            return

        # Schedule deletion after the current transaction commits.
        # Falls back to immediate execution if not in a transaction.
        transaction.on_commit(
            lambda: _safe_delete_file(
                sender, field_name, old_name,
                reason=f"replaced on {app_label}.{model_name} pk={instance.pk}",
            )
        )

    handler.__name__ = f"post_save_cleanup_{app_label}_{model_name}_{field_name}"
    return handler


def _make_post_delete_cleanup(app_label, model_name, field_name):
    """
    post_delete: delete the file associated with the row being removed.
    """
    def handler(sender, instance, **kwargs):
        try:
            field_file = getattr(instance, field_name)
            name = field_file.name if field_file and field_file.name else None
        except Exception:
            name = None

        if not name:
            return

        transaction.on_commit(
            lambda: _safe_delete_file(
                sender, field_name, name,
                reason=f"row deleted on {app_label}.{model_name} pk={instance.pk}",
            )
        )

    handler.__name__ = f"post_delete_cleanup_{app_label}_{model_name}_{field_name}"
    return handler


# ──────────────────────────────────────────────────────────────
# Wiring
# ──────────────────────────────────────────────────────────────

def _resolve_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        logger.warning(
            "file_cleanup: model %s.%s not found — skipping",
            app_label, model_name,
        )
        return None


def register_all():
    """
    Connect pre_save / post_save / post_delete receivers for every
    entry in the registries. Idempotent (uses dispatch_uid).
    """
    # Replacement / clearing cleanup
    for app_label, model_name, field_name in REPLACE_CLEANUP_FIELDS:
        model = _resolve_model(app_label, model_name)
        if model is None or not hasattr(model, field_name):
            continue

        pre_save.connect(
            _make_pre_save_tracker(app_label, model_name, field_name),
            sender=model,
            dispatch_uid=f"file_cleanup_pre::{app_label}::{model_name}::{field_name}",
            weak=False,
        )
        post_save.connect(
            _make_post_save_cleanup(app_label, model_name, field_name),
            sender=model,
            dispatch_uid=f"file_cleanup_post::{app_label}::{model_name}::{field_name}",
            weak=False,
        )

    # Row-deletion cleanup
    for app_label, model_name, field_name in DELETE_CLEANUP_FIELDS:
        model = _resolve_model(app_label, model_name)
        if model is None or not hasattr(model, field_name):
            continue

        post_delete.connect(
            _make_post_delete_cleanup(app_label, model_name, field_name),
            sender=model,
            dispatch_uid=f"file_cleanup_del::{app_label}::{model_name}::{field_name}",
            weak=False,
        )


register_all()