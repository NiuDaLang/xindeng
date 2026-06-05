from django.core.management.base import BaseCommand, CommandError
from carts.models import ShippingCharge
from django.apps import apps
import csv


# Proposed command - python manage.py importdata file_path model_name
class Command(BaseCommand):
    help = "importdata from csv and insert to the database"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="path to the csv file")
        parser.add_argument("model_name", type=str, help="name of the model")

    def handle(self, *args, **options):
        file_path = options["file_path"]
        model_name = options["model_name"].capitalize()

        # Search for the model across all installed apps
        model = None
        for app_conig in apps.get_app_configs():
            # Try to search for the model 
            try:
                model = apps.get_model(app_conig.label, model_name)
                break # stop searching once the model is found
            except LookupError:
                continue # continue searching in the next app

        if not model:
            raise CommandError(f"Model {model_name} not found in any app!")

        with open(file_path, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                model.objects.create(**row)

        # n = 5
        # with open(file_path, "r") as csv_file:
        #     reader = csv.DictReader(csv_file)
        #     for i, row in enumerate(reader):
        #         if i >= n:
        #             break
        #         print(row)
        #         ShippingCharge.objects.create(**row)
        #         print(f"Row {i+1} inserted")

        self.stdout.write(self.style.SUCCESS("Data imported successfully"))