from django.core.management.base import BaseCommand
from store.models import Color


class Command(BaseCommand):
    help = 'Insert data to the database'
    
    def handle(self, *args, **options):
        dataset = [
            {"color_name": "綠色|Green"},
            {"color_name": "粉色|Pink"},
            {"color_name": "藍色|Blue"},
            {"color_name": "紅色|Red"},
        ]

        for data in dataset:
            data_exists = Color.objects.filter(color_name=data["color_name"]).exists()
            if not data_exists:
                Color.objects.create(color_name=data["color_name"])
            else:
                self.stdout.write(self.style.WARNING(f"Data with color name {data['color_name']} already exists. Skipping insertion."))

        self.stdout.write(self.style.SUCCESS("Data inserted successfully!"))