# core/management/commands/sweep_orphan_media.py
"""
Find files under MEDIA_ROOT that are not referenced by any FileField
in any registered model.

Strategy: instead of scanning all of MEDIA_ROOT and trying to guess
which files are "static" vs "managed", we only scan folders that are
KNOWN to be exclusively owned by Django models. Static content folders
(hero/, images/about/, videos/, etc.) are never scanned.

By default, prints a report. Pass --delete to remove them.

Usage:
    python manage.py sweep_orphan_media
    python manage.py sweep_orphan_media --path-prefix=ckeditor5_storage/
    python manage.py sweep_orphan_media --delete
"""

import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand


# ──────────────────────────────────────────────────────────────
# Managed folder registry — the source of truth for what we sweep.
# ──────────────────────────────────────────────────────────────
#
# Format: relative_path -> list of (app_label, model_name, field_name)
#
# A folder is ONLY scanned if it appears in this dict. Anything else
# under MEDIA_ROOT is presumed static content and left alone.
#
MANAGED_FOLDERS = {
    "images/products": [
        ("store", "product",                 "images"),
        ("store", "productvariation",        "images"),
        ("store", "productgallery",          "image"),
        ("store", "productvariationgallery", "image"),
    ],
    "images/categories": [
        ("category", "category", "cat_image"),
    ],
    "blog/featured_images": [
        ("blog", "post", "featured_image"),
    ],
    "creators/avatars": [
        ("creators", "creatorprofile", "avatar"),
    ],
    "creators/banners": [
        ("creators", "creatorprofile", "banner"),
    ],
    "creators/wechat_qr": [
        ("creators", "creatorprofile", "wechat_qr"),
    ],
    "userprofile": [
        ("accounts", "userprofile", "profile_picture"),
    ],
    "perks": [
        ("accounts", "perk", "featured_image"),
    ],
    "reviews/attachments": [
        ("reviews", "commentimage", "image"),
    ],
    "chat_images": [
        ("accounts", "chatmessage", "image"),
    ],
    # NOTE: ckeditor5_storage/ is deliberately EXCLUDED. It will be
    # handled by a dedicated sweep command in a later phase, because
    # its files are referenced by HTML content, not by a DB column.
}

# Files under managed folders that must NEVER be deleted, even if the
# DB doesn't reference them. These are template-side fallbacks.
PROTECTED_FILES = {
    "images/products/variations/pattern1.png",
    "images/products/variations/pattern2.png",
    "images/products/variations/pattern3.png",
}


class Command(BaseCommand):
    help = (
        "Find files under MEDIA_ROOT that aren't referenced by any DB row. "
        "Only scans folders managed by Django models."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete", action="store_true",
            help="Actually delete the orphans (default: report only).",
        )
        parser.add_argument(
            "--folder", type=str, default=None,
            help="Restrict scan to one managed folder, e.g. 'images/products'.",
        )
        parser.add_argument(
            "--list-folders", action="store_true",
            help="List the managed folders and their owning models, then exit.",
        )

    def handle(self, *args, **opts):
        if opts["list_folders"]:
            self._print_folder_registry()
            return

        do_delete = opts["delete"]
        only_folder = opts["folder"]

        if only_folder and only_folder not in MANAGED_FOLDERS:
            self.stderr.write(
                f"Unknown folder: {only_folder!r}. "
                f"Use --list-folders to see available options."
            )
            return

        media_root = Path(settings.MEDIA_ROOT).resolve()

        # Collect all referenced names across every model in our registry.
        # We do this once, globally, because a file may live in one folder
        # but be referenced by a field pointing elsewhere.
        referenced = self._collect_referenced_names()
        self.stdout.write(
            self.style.NOTICE(f"Found {len(referenced)} referenced files in DB.")
        )

        grand_total_files = 0
        grand_total_orphans = 0
        grand_total_bytes = 0
        all_orphans = []  # (folder, full_path, rel_name, size)

        for folder, field_specs in MANAGED_FOLDERS.items():
            if only_folder and folder != only_folder:
                continue

            scan_root = media_root / folder
            if not scan_root.exists():
                continue

            folder_orphans = []
            folder_files = 0

            for dirpath, dirnames, filenames in os.walk(scan_root):
                for filename in filenames:
                    if filename == ".DS_Store":
                        continue

                    full_path = Path(dirpath) / filename
                    try:
                        rel_name = full_path.relative_to(media_root).as_posix()
                    except ValueError:
                        continue

                    if rel_name in PROTECTED_FILES:
                        continue

                    folder_files += 1

                    if rel_name in referenced:
                        continue

                    folder_orphans.append(
                        (full_path, rel_name, full_path.stat().st_size)
                    )

            folder_bytes = sum(s for _, _, s in folder_orphans)

            grand_total_files += folder_files
            grand_total_orphans += len(folder_orphans)
            grand_total_bytes += folder_bytes

            self.stdout.write("")
            self.stdout.write(
                self.style.NOTICE(
                    f"▶ {folder}/  "
                    f"({folder_files} files, {len(folder_orphans)} orphans, "
                    f"{folder_bytes / 1024 / 1024:.2f} MB)"
                )
            )

            if folder_orphans:
                for path, rel_name, size in sorted(
                    folder_orphans, key=lambda x: x[1]
                ):
                    self.stdout.write(
                        f"    {size / 1024:8.1f} KB  {rel_name}"
                    )
                all_orphans.extend(
                    (folder, p, r, s) for (p, r, s) in folder_orphans
                )

        # ── Summary ──
        self.stdout.write("")
        self.stdout.write(
            self.style.NOTICE(
                f"Total files scanned: {grand_total_files}"
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f"Total orphans: {grand_total_orphans} "
                f"({grand_total_bytes / 1024 / 1024:.2f} MB)"
            )
        )

        # ── Delete ──
        if do_delete and all_orphans:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Deleting..."))
            deleted = 0
            errors = 0

            for folder, path, rel_name, _ in all_orphans:
                try:
                    path.unlink()
                    deleted += 1
                except Exception as exc:
                    self.stderr.write(f"  FAILED {rel_name}: {exc}")
                    errors += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted: {deleted} | Errors: {errors}"
                )
            )

    # ──────────────────────────────────────────────────────────
    # Internals
    # ──────────────────────────────────────────────────────────

    def _collect_referenced_names(self):
        """
        Walk every registered model+field and collect the set of storage
        names actually in use. A name is 'referenced' if ANY model points
        at it — we don't try to attribute a file to a specific field.
        """
        referenced = set()

        # Flatten the registry into a unique list of (app, model, field).
        seen = set()
        for field_specs in MANAGED_FOLDERS.values():
            for spec in field_specs:
                if spec not in seen:
                    seen.add(spec)

        for app_label, model_name, field_name in seen:
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                self.stderr.write(
                    f"  (skipped: {app_label}.{model_name} not found)"
                )
                continue

            if not hasattr(model, field_name):
                self.stderr.write(
                    f"  (skipped: {app_label}.{model_name} has no field "
                    f"{field_name!r})"
                )
                continue

            values = (
                model.objects
                .values_list(field_name, flat=True)
                .exclude(**{f"{field_name}__isnull": True})
                .exclude(**{field_name: ""})
            )
            for v in values.iterator():
                if v:
                    referenced.add(v.replace("\\", "/").lstrip("/"))

        return referenced

    def _print_folder_registry(self):
        """List every managed folder and the models that write into it."""
        self.stdout.write("Managed folders (sweep targets):")
        self.stdout.write("")
        for folder, specs in MANAGED_FOLDERS.items():
            self.stdout.write(f"  ▶ {folder}/")
            for app_label, model_name, field_name in specs:
                self.stdout.write(
                    f"      ← {app_label}.{model_name}.{field_name}"
                )
            self.stdout.write("")
        self.stdout.write(
            "Any folder NOT in this list is treated as static content "
            "and is never scanned."
        )