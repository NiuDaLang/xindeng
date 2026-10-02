# store/admin.py
from django.contrib import admin
from .models import (
    Product, ProductVariation, Color, Size, Type,
    ProductGallery, ProductVariationGallery, ProductReviewLog
)
import admin_thumbnails
from reviews.admin import CommentInline


# ═══════════════════════════════════════════════════════════════
# INLINES
# ═══════════════════════════════════════════════════════════════

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
    fields = (
        'image',
        'title',
        'is_featured_in_gallery',
        'gallery_caption',
        'gallery_order',
    )


@admin_thumbnails.thumbnail('image')
class ProductVariationGalleryInline(admin.TabularInline):
    model = ProductVariationGallery
    extra = 1


# ═══════════════════════════════════════════════════════════════
# ADMIN CLASSES
# ═══════════════════════════════════════════════════════════════

class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product_name',
        'category',
        'craft_list',
        'creator',
        'modified_date',
        'origin',
        'status',
        'submitted_at',
        'is_deleted',
    )
    list_filter = (
        'category',
        'craft_types',
        'origin',
        'is_active',
        'is_physical',
        'is_digital',
        'status',
        'is_deleted',
    )
    search_fields = (
        'product_name',
        'slug',
        'brand',
        'description',
        'creator__display_name',
    )
    prepopulated_fields = {'slug': ('product_name',)}
    filter_horizontal = ('craft_types',)
    inlines = [ProductGalleryInline, CommentInline]
    readonly_fields = ('created_date', 'modified_date')
    actions = ['restore_products']

    fieldsets = (
        ("Identity｜身份", {
            'fields': ('product_name', 'slug', 'brand', 'creator', 'category')
        }),
        ("Classification｜分類", {
            'fields': ('craft_types', 'tags', 'origin', 'color', 'gender', 'blood')
        }),
        ("Content｜內容", {
            'fields': ('description', 'details', 'images')
        }),
        ("Product Type｜產品類型", {
            'fields': (
                'is_physical',
                'is_digital',
                'digital_fulfillment_type',
                'is_voucher',
                'is_active',
            )
        }),
        ("Review Status｜審核狀態", {
            'fields': ('status', 'submitted_at'),
        }),
        ("Tax & Customs｜稅務", {
            'fields': ('hs_code', 'tax_category'),
            'classes': ('collapse',)
        }),
        ("Timestamps｜時間戳", {
            'fields': ('created_date', 'modified_date'),
            'classes': ('collapse',)
        }),
    )

    def craft_list(self, obj):
        return ", ".join(ct.label for ct in obj.craft_types.all()) or "—"
    craft_list.short_description = "Crafts"

    def save_model(self, request, obj, form, change):
        # ─────────────────────────────────────────────────────
        # 1. Capture the OLD state BEFORE saving.
        # ─────────────────────────────────────────────────────
        old_status = None
        old_is_active = None
        if change:
            try:
                old = Product.objects.get(pk=obj.pk)
                old_status = old.status
                old_is_active = old.is_active
            except Product.DoesNotExist:
                pass

        # ─────────────────────────────────────────────────────
        # 2. Save the object (single call).
        # ─────────────────────────────────────────────────────
        super().save_model(request, obj, form, change)

        # ─────────────────────────────────────────────────────
        # 3. Post-save: inherit craft_types from creator if empty.
        # ─────────────────────────────────────────────────────
        if not obj.craft_types.exists() and obj.creator and obj.creator.craft_types.exists():
            obj.craft_types.set(obj.creator.craft_types.all())

        # ─────────────────────────────────────────────────────
        # 4. Post-save: close any outstanding de-list request if
        #    the admin just unpublished / deactivated the product.
        # ─────────────────────────────────────────────────────
        if change and old_status is not None:
            was_published = (old_status == "Published" and old_is_active)
            is_now_unpublished = (obj.status != "Published" or not obj.is_active)

            if was_published and is_now_unpublished:
                latest = obj.review_logs.order_by("-created_at").first()
                if latest and latest.action == "deactivation_requested":
                    ProductReviewLog.objects.create(
                        product=obj,
                        action="deletion_approved",
                        actor=request.user,
                        note="Admin resolved the de-list request by setting the product to Unpublished / inactive.",
                    )


    @admin.action(description="Restore selected soft-deleted products")
    def restore_products(self, request, queryset):
        restored = 0
        for p in queryset.filter(is_deleted=True):
            p.is_deleted = False
            p.is_active = (p.status == "Published")
            p.save(update_fields=["is_deleted", "is_active"])
            restored += 1
        self.message_user(request, f"Restored {restored} product(s).")


class ProductVariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'display_category_name',
        'color',
        'size',
        'type',
        'stock',
        'with_shipping',
        'single_pack',
        'weight',
        'is_available',
        'price',
        'created_date',
        'modified_date',
    )
    inlines = [ProductVariationGalleryInline]

    def display_category_name(self, obj):
        return obj.product.category.category_name if obj.product.category else None
    display_category_name.short_description = "Category Name"
    display_category_name.admin_order_field = 'product__category'


@admin.register(ProductGallery)
class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'title', 'is_featured_in_gallery', 'gallery_order')
    list_filter = ('is_featured_in_gallery',)
    list_editable = ('is_featured_in_gallery', 'gallery_order')
    search_fields = ('product__product_name', 'title', 'gallery_caption')
    list_per_page = 50


@admin.register(ProductReviewLog)
class ProductReviewLogAdmin(admin.ModelAdmin):
    list_display = ("product", "action", "actor", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("product", "note")
    readonly_fields = ("product", "action", "actor", "note", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Type)
admin.site.register(ProductVariationGallery)