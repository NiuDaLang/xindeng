from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug', 'vault_subfolder')
    fieldsets = (
        ("Identity｜身份", {
            "fields": ("category_name", "slug", "description", "product_format", "cat_image"),
        }),
        ("Digital delivery｜電子交付", {
            "fields": ("vault_subfolder",),
            "description": (
                "Approved digital files in this category are written to "
                "XINDENG_VAULT_ROOT / <vault_subfolder> / <uuid>.<ext>. "
                "Leave blank to write to the vault root. The subfolder "
                "is created automatically on first approval."
            ),
        }),
    )
    
# Register your models here.
admin.site.register(Category, CategoryAdmin)