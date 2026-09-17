from django.core.management.base import BaseCommand
from store.models import Color


class Command(BaseCommand):
    help = 'Seed the store with starter color records.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Preview what would be created without writing to the DB.",
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        dataset = [
            {"color_name": "綠色|Green"},
            {"color_name": "粉色|Pink"},
            {"color_name": "藍色|Blue"},
            {"color_name": "紅色|Red"},
        ]
        for data in dataset:
            exists = Color.objects.filter(color_name=data["color_name"]).exists()
            if not exists:
                if dry_run:
                    self.stdout.write(f"Would create: {data['color_name']}")
                else:
                    Color.objects.create(color_name=data["color_name"])
                    self.stdout.write(f"Created: {data['color_name']}")
            else:
                self.stdout.write(self.style.WARNING(f"Exists, skipping: {data['color_name']}"))

        if dry_run:
            self.stdout.write(self.style.NOTICE("Dry run — no changes made."))
        else:
            self.stdout.write(self.style.SUCCESS("Seeding complete."))