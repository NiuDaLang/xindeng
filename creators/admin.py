# creators/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import CreatorProfile, CraftType


@admin.register(CraftType)
class CraftTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'label', 'order')
    list_editable = ('label', 'order')
    search_fields = ('name', 'label')
    ordering = ('order', 'label')


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = (
        'display_name',
        'user',
        'craft_list',
        'province',
        'is_premium',
        'page_template',       # 🌟 NEW
        'is_verified',
        'tag_list',            # 🌟 Re-add this
        'preview_page_link',   # 🌟 NEW
        'created_at',
    )
    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = "Tags"

    list_editable = ('is_verified', 'is_premium', 'page_template')
    list_filter = (
        'is_verified',
        'is_premium',
        'page_template',
        'craft_types',
        'province',
    )
    search_fields = (
        'display_name',
        'user__username',
        'user__email',
        'bio',
        'tagline',
    )
    prepopulated_fields = {'slug': ('display_name',)}
    readonly_fields = ('created_at', 'updated_at', 'preview_page_link')
    filter_horizontal = ('craft_types',)

    fieldsets = (
        ("Identity｜身份", {
            'fields': ('user', 'display_name', 'slug', 'tagline', 'bio')
        }),
        ("Location & Craft｜地域與工藝", {
            'fields': ('province', 'city', 'craft_types', 'dispatch_address')
        }),
        ("Media｜影像", {
            'fields': ('avatar', 'banner')
        }),
        ("Status｜狀態", {
            'fields': ('is_verified', 'is_premium')
        }),
        ("Page Layout｜頁面版型", {
            'fields': (
                'page_template',
                'premium_page_slug',
                'premium_page_published',
            ),
            'description': (
                "Layouts A/B/C are standard; D is reserved for premium "
                "artisans. The custom template file is named "
                "<code>&lt;pk&gt;_premium_page.html</code> and lives under "
                "<code>templates/artisans/premium/</code>."
            ),
        }),
        ("Contact & Social｜聯絡與社交", {
            'fields': ('website', 'instagram', 'wechat'),
            'classes': ('collapse',)
        }),
        ("Timestamps｜時間戳", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_artisans', 'unverify_artisans']

    def craft_list(self, obj):
        return ", ".join(ct.label for ct in obj.craft_types.all())
    craft_list.short_description = "Crafts"

    def preview_page_link(self, obj):
        if obj.pk and obj.is_verified:
            url = reverse('artisan_detail', kwargs={'slug': obj.slug})
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">'
                'View page ↗</a>',
                url
            )
        return "—"
    preview_page_link.short_description = "Preview"

    @admin.action(description="✅ Approve selected artisans (is_verified=True)")
    def approve_artisans(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} artisan(s) approved.")

    @admin.action(description="🚫 Un-verify selected artisans (is_verified=False)")
    def unverify_artisans(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} artisan(s) un-verified.")