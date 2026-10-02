# dataentry/management/commands/merge_tags.py

from django.core.management.base import BaseCommand, CommandError
from taggit.models import Tag, TaggedItem

# python manage.py merge_tags <target> <source1> <source2> ...
# example: python manage.py merge_tags --dry-run "粉色|Pink" "粉色Pink"
# python manage.py merge_tags "粉色|Pink" "粉色Pink"

class Command(BaseCommand):
    help = (
        "Merge one or more tags into a canonical tag. "
        "Migrates all tagged objects to the target tag, then deletes the source tags."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'target',
            type=str,
            help="The canonical tag name to keep (e.g., '療癒|Healing').",
        )
        parser.add_argument(
            'sources',
            nargs='+',
            help="One or more tag names to merge into the target and then delete.",
        )
        parser.add_argument(
            '--create-target',
            action='store_true',
            help="Create the target tag if it does not already exist.",
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Preview the changes without applying them.",
        )

    def handle(self, *args, **options):
        target_name = options['target']
        source_names = options['sources']
        dry_run = options['dry_run']
        create_target = options['create_target']

        # ── 1. Resolve target tag ──
        target = Tag.objects.filter(name=target_name).first()
        if not target:
            if create_target:
                if dry_run:
                    self.stdout.write(self.style.WARNING(
                        f"Target '{target_name}' does not exist. "
                        f"Would be created. (dry-run)"
                    ))
                else:
                    target = Tag.objects.create(name=target_name)
                    self.stdout.write(self.style.SUCCESS(
                        f"Created target tag '{target_name}'."
                    ))
            else:
                raise CommandError(
                    f"Target tag '{target_name}' not found. "
                    f"Use --create-target to create it."
                )
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Target tag: '{target.name}' (id={target.id})"
            ))

        # ── 2. Sanity check: sources must not include target ──
        if target_name in source_names:
            raise CommandError(
                f"Target '{target_name}' cannot also be a source. "
                f"Remove it from the sources list."
            )

        # ── 3. Migrate each source tag ──
        total_migrated = 0
        total_deleted = 0
        missing = []

        for source_name in source_names:
            source = Tag.objects.filter(name=source_name).first()
            if not source:
                missing.append(source_name)
                self.stdout.write(self.style.WARNING(
                    f"  ⚠ '{source_name}' not found — skipping."
                ))
                continue

            items = TaggedItem.objects.filter(tag=source)
            count = items.count()
            self.stdout.write(
                f"  → '{source_name}' (id={source.id}): {count} tagged item(s)."
            )

            if dry_run:
                continue

            for item in items:
                content_object = item.content_object
                if content_object is None:
                    # Dangling TaggedItem — clean up
                    item.delete()
                    continue

                content_object.tags.add(target_name)
                content_object.tags.remove(source_name)
                total_migrated += 1

            source.delete()
            total_deleted += 1
            self.stdout.write(f"     ✔ Migrated and deleted '{source_name}'.")

        # ── 4. Summary ──
        self.stdout.write("")
        if missing:
            self.stdout.write(self.style.WARNING(
                f"Missing tags (not found): {', '.join(missing)}"
            ))

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "Dry run complete. No changes made. "
                "Re-run without --dry-run to apply."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Done. Migrated {total_migrated} object(s); "
                f"deleted {total_deleted} tag(s)."
            ))