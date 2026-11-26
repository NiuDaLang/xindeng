# creators/migrations/0017_backfill_frontline_threads.py
from django.db import migrations
from creators.backfill import run_backfill


class Migration(migrations.Migration):
    dependencies = [("creators", "0016_artisanadminmessage_image")]
    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: run_backfill(apps),
            reverse_code=migrations.RunPython.noop,
        ),
    ]