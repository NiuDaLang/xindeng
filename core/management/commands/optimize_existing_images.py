# core/management/commands/optimize_existing_images.py
from django.apps import apps
from django.core.management.base import BaseCommand

from core.image_utils import (
    is_already_optimized,
    is_skippable,
    optimize_image,
    save_optimized_to_field,      # ← NEW: use the shared helper
)
from core.signals import IMAGE_FIELD_REGISTRY


class Command(BaseCommand):
    help = (
        "Retroactively optimise all registered image fields. "
        "Use --dry-run first to preview the impact."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would change without writing anything.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-process even files that appear already optimised.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Rows to process per queryset chunk (default 100).",
        )
        parser.add_argument(
            "--model",
            type=str,
            default=None,
            help="Restrict to one model label, e.g. 'store.product'.",
        )

    def handle(self, *args, **opts):
        dry_run = opts["dry_run"]
        force = opts["force"]
        batch_size = opts["batch_size"]
        only_model = opts["model"]

        total_processed = 0
        total_skipped = 0

        for (app_label, model_name, field_name), field_opts in IMAGE_FIELD_REGISTRY.items():
            model_label = f"{app_label}.{model_name}"

            if only_model and model_label != only_model:
                continue

            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                continue

            qs = model.objects.all().order_by("pk")
            self.stdout.write(f"\n▶ {model_label}.{field_name}")

            for instance in qs.iterator(chunk_size=batch_size):
                field_file = getattr(instance, field_name, None)

                if is_skippable(field_file):
                    total_skipped += 1
                    continue

                if not force and is_already_optimized(field_file):
                    total_skipped += 1
                    continue

                if dry_run:
                    try:
                        size_kb = field_file.size / 1024
                    except Exception:
                        size_kb = 0
                    self.stdout.write(
                        f"   [DRY] pk={instance.pk} {field_file.name} ({size_kb:.1f} KB)"
                    )
                    total_processed += 1
                    continue

                # ── Applied mode ──
                result = optimize_image(field_file, force=force, **field_opts)
                if result is None:
                    total_skipped += 1
                    continue

                content, new_name = result

                # THE FIX: delegate persistence to the shared helper, which
                # correctly handles upload_to prefixing, atomic replacement,
                # and deletion of the old file when the path changes.
                save_optimized_to_field(instance, field_name, content, new_name)

                total_processed += 1
                if total_processed % 25 == 0:
                    self.stdout.write(f"   … {total_processed} processed so far")

        mode = "DRY RUN" if dry_run else "APPLIED"
        self.stdout.write(self.style.SUCCESS(
            f"\n[{mode}] Processed: {total_processed} | Skipped: {total_skipped}"
        ))