# dataentry/management/commands/clean_orphans.py
from django.core.management.base import BaseCommand
from django.db.models import Count
from taggit.models import Tag


# python manage.py clean_orphans --dry-run
# python manage.py clean_orphans

class Command(BaseCommand):
    help = "Delete all orphan tags (zero tagged items)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        orphans = Tag.objects.annotate(c=Count('taggit_taggeditem_items')).filter(c=0)

        if not orphans.exists():
            self.stdout.write(self.style.SUCCESS("No orphan tags."))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Would delete {orphans.count()} orphan(s):"))
            for t in orphans:
                self.stdout.write(f"  {t.name!r}")
            return

        count, _ = orphans.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} orphan(s)."))