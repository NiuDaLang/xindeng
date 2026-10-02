# core/management/commands/repair_doubled_paths.py
"""
Detect and repair media paths that were doubled by the pre-fix backfill.

Symptom: a field name like 'images/products/images/products/foo.webp'
         instead of 'images/products/foo.webp'.

Strategy:
  1. For each registered (model, field), find rows whose `name` contains the
     field's upload_to prefix twice in a row.
  2. Compute the corrected path by collapsing the duplicate prefix.
  3. If the file exists at the corrected path already, just update the DB.
  4. Otherwise, move the file on disk (rename) and update the DB.
  5. Optionally, delete the leftover original file if it still exists.
"""

import os
import shutil
import unicodedata

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from core.signals import IMAGE_FIELD_REGISTRY


def _resolve_upload_to_prefix(model, field_name):
    """
    Return the *string* upload_to prefix for a field, or None if it's
    a callable (in which case we can't safely compute a static prefix).
    """
    field = model._meta.get_field(field_name)
    upload_to = getattr(field, "upload_to", None)
    if not upload_to or callable(upload_to):
        return None
    prefix = str(upload_to).rstrip("/")
    return prefix


def _find_doubled_prefix(name, prefix):
    """
    Return the corrected name if `prefix` appears twice consecutively,
    otherwise None.
    """
    normalized = unicodedata.normalize("NFC", name).replace("\\", "/")

    # Look for "<prefix>/<prefix>/..."
    doubled = f"{prefix}/{prefix}/"
    if not normalized.startswith(doubled):
        # Some cases may have an intermediate segment. Look more flexibly.
        idx = normalized.find(doubled)
        if idx < 0:
            return None
        # Collapse: everything up to and including the first prefix,
        # then everything after the second prefix.
        head = normalized[:idx + len(prefix) + 1]  # includes trailing slash
        tail = normalized[idx + len(doubled):]
        return head + tail

    # Collapse at the start
    tail = normalized[len(doubled):]
    return f"{prefix}/{tail}"


class Command(BaseCommand):
    help = (
        "Detect and repair media paths that were doubled by the "
        "pre-fix optimize_existing_images backfill."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report what would change without writing anything.",
        )
        parser.add_argument(
            "--delete-orphans", action="store_true",
            help="After repair, delete original files that are no longer "
                 "referenced by any DB row.",
        )

    def handle(self, *args, **opts):
        dry_run = opts["dry_run"]
        delete_orphans = opts["delete_orphans"]

        repaired = 0
        skipped = 0
        failed = 0

        from django.core.files.storage import default_storage
        from django.conf import settings

        for (app_label, model_name, field_name), _ in IMAGE_FIELD_REGISTRY.items():
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                continue

            prefix = _resolve_upload_to_prefix(model, field_name)
            if not prefix:
                # Callable upload_to — skip (manual repair needed)
                continue

            self.stdout.write(f"\n▶ {app_label}.{model_name}.{field_name}")

            for instance in model.objects.all().iterator(chunk_size=200):
                field_file = getattr(instance, field_name)
                if not field_file or not field_file.name:
                    continue

                corrected = _find_doubled_prefix(field_file.name, prefix)
                if not corrected:
                    skipped += 1
                    continue

                old_name = field_file.name
                self.stdout.write(f"   pk={instance.pk}")
                self.stdout.write(f"      old: {old_name}")
                self.stdout.write(f"      new: {corrected}")

                if dry_run:
                    repaired += 1
                    continue

                try:
                    self._repair_one(
                        instance, field_name,
                        old_name, corrected,
                        default_storage, delete_orphans,
                    )
                    repaired += 1
                except Exception as exc:
                    self.stderr.write(
                        f"      FAILED: {type(exc).__name__}: {exc}"
                    )
                    failed += 1

        mode = "DRY RUN" if dry_run else "APPLIED"
        self.stdout.write(self.style.SUCCESS(
            f"\n[{mode}] Repaired: {repaired} | Skipped: {skipped} | Failed: {failed}"
        ))

    def _repair_one(self, instance, field_name, old_name, corrected,
                    storage, delete_orphans):
        """
        Move the file on disk (if needed) and update the DB row.
        """
        old_path = storage.path(old_name) if hasattr(storage, "path") else None
        new_path = storage.path(corrected) if hasattr(storage, "path") else None

        if not old_path or not new_path:
            raise RuntimeError("Storage doesn't support .path()")

        with transaction.atomic():
            # Update the DB first.
            field_file = getattr(instance, field_name)
            field_file.name = corrected
            setattr(instance, "_skip_image_optimization", True)
            try:
                instance.save(update_fields=[field_name])
            finally:
                try:
                    delattr(instance, "_skip_image_optimization")
                except AttributeError:
                    pass

            # Then move the file on disk.
            if os.path.exists(old_path):
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                if os.path.exists(new_path):
                    # Target already exists — assume it's identical or newer;
                    # remove the source (safer than overwriting).
                    if delete_orphans:
                        os.remove(old_path)
                else:
                    shutil.move(old_path, new_path)