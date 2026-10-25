# category/migrations/0008_category_vault_subfolder.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("category", "0007_alter_category_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="vault_subfolder",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Subdirectory under XINDENG_VAULT_ROOT for approved digital "
                    "files in this category. Blank means the vault root. Created "
                    "automatically on the first approval if it does not exist. "
                    "｜此分類之電子檔案審核通過後存放於 XINDENG_VAULT_ROOT 之子目錄；"
                    "留空表示存放於根目錄。首次審核通過時若目錄不存在將自動建立。"
                ),
                max_length=100,
            ),
        ),
    ]