# category/migrations/0009_backfill_category_vault_subfolder.py
"""
Backfill Category.vault_subfolder for the two categories whose
digital files already have an intended subfolder on disk.

  * slug="epainting" → "epaintings"
        The epaintings/ directory exists under XINDENG_VAULT_ROOT
        (created 2026-06-13). It is currently empty; the three
        approved CUSTOM files live at the vault root and are
        correct there (Decision A, 2026-10-25). The first future
        approval of an epaintings-category file will route here.

  * slug="ebooks" → "ebooks"
        The ebooks/ directory exists (created 2026-06-14) and
        already contains law_of_one.pdf, referenced by the
        ProductVariation of the "Law of One (e-book)" product as
        "ebooks/law_of_one.pdf". The pointer was written by a
        previous version of review_vault_upload_approve that
        routed by category; the current code regressed to
        root-only. The backfill makes the category mapping
        explicit so the routing change can restore the previous
        behaviour with a field rather than a guess.

Every other category keeps the field default ("") — meaning the
vault root — until an admin sets a subfolder explicitly.
"""

from django.db import migrations


def forwards(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    Category.objects.filter(slug="epainting").update(vault_subfolder="epaintings")
    Category.objects.filter(slug="ebooks").update(vault_subfolder="ebooks")


def reverses(apps, schema_editor):
    Category = apps.get_model("category", "Category")
    Category.objects.update(vault_subfolder="")


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0008_category_vault_subfolder"),
    ]

    operations = [
        migrations.RunPython(forwards, reverses),
    ]