# store/admin.py
from django.contrib import admin
from .models import (
    Product, ProductVariation, Color, Size, Type,
    ProductGallery, ProductVariationGallery,
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
    )
    list_filter = (
        'category',
        'craft_types',
        'origin',
        'is_active',
        'is_physical',
        'is_digital',
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
        """
        Called when the admin form is submitted.
        If the product has no crafts and the creator does, inherit them.
        """
        super().save_model(request, obj, form, change)
        if not obj.craft_types.exists() and obj.creator and obj.creator.craft_types.exists():
            obj.craft_types.set(obj.creator.craft_types.all())
            

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


# ═══════════════════════════════════════════════════════════════
# REGISTRATION
# ═══════════════════════════════════════════════════════════════

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Type)
admin.site.register(ProductVariationGallery)