# creators/admin.py
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import CreatorProfile, CraftType, ArtisanChatMessage, ArtisanAdminMessage

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
        'page_template',
        'is_verified',
        'preview_page_link',
        'created_at',
    )
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
            'fields': ('province', 'city', 'craft_types', 'tags')
        }),
        ("Media｜影像", {
            'fields': ('avatar', 'banner', 'wechat_qr')
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
        }),
        ("Contact & Social｜聯絡與社交", {
            'fields': ('website', 'instagram'),
            'classes': ('collapse',)
        }),
        ("Timestamps｜時間戳", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_artisans', 'unverify_artisans']

    def preview_page_link(self, obj):
        if obj.pk and obj.is_verified:
            url = reverse('artisan_detail', kwargs={'slug': obj.slug})
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">View page ↗</a>',
                url
            )
        return "—"
    preview_page_link.short_description = "Preview"

    def craft_list(self, obj):
        return ", ".join(ct.label for ct in obj.craft_types.all())
    craft_list.short_description = "Crafts"

    @admin.action(description="✅ Approve selected artisans (is_verified=True)")
    def approve_artisans(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} artisan(s) approved.")

    @admin.action(description="🚫 Un-verify selected artisans (is_verified=False)")
    def unverify_artisans(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} artisan(s) un-verified.")


@admin.register(ArtisanChatMessage)
class ArtisanChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'artisan', 
        'customer', 
        'sender', 
        'order_product',
        'is_read', 
        'created_at'
    )
    list_filter = ('is_read', 'artisan', 'customer')
    search_fields = (
        'content', 
        'artisan__display_name', 
        'customer__username', 
        'sender__username',
        'order_product__order__order_number' # 👈 Added this
    )
    raw_id_fields = ('artisan', 'customer', 'sender', 'order_product')


from .models import FrontlineThread

@admin.register(FrontlineThread)
class FrontlineThreadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'customer', 
        'artisan', 
        'order_product', 
        'is_escalated', 
        'is_settled', 
        'last_message_at'
    )
    list_filter = (
        'escalated_at', 
        'settled_at', 
        'artisan', 
        'customer'
    )
    search_fields = (
        'customer__username', 
        'artisan__display_name', 
        'order_product__order__order_number'
    )
    raw_id_fields = ('customer', 'artisan', 'order_product', 'settled_by', 'escalated_by')
    readonly_fields = ('created_at', 'updated_at', 'last_message_at')

    # Custom boolean indicators for the list view
    @admin.display(boolean=True, description='Escalated')
    def is_escalated(self, obj):
        return obj.escalated_at is not None

    @admin.display(boolean=True, description='Settled')
    def is_settled(self, obj):
        return obj.settled_at is not None

    # Action to quickly reset an escalation for testing
    @admin.action(description="↩️ Un-escalate selected threads (for testing)")
    def un_escalate_threads(self, request, queryset):
        updated = queryset.update(escalated_at=None, escalated_by=None)
        self.message_user(request, f"{updated} thread(s) un-escalated.")

    actions = ['un_escalate_threads']