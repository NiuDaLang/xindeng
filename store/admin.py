from django.contrib import admin
from .models import Product, ProductVariation, Color, Size, Type, ProductGallery, ProductVariationGallery
import admin_thumbnails
from reviews.admin import CommentInline


@admin_thumbnails.thumbnail('image') 
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


@admin_thumbnails.thumbnail('image') 
class ProductVariationGalleryInline(admin.TabularInline):
    model = ProductVariationGallery
    extra = 1 


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'modified_date', 'origin')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline, CommentInline,]


class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'display_category_name', 'color', 'size', 'type', 'stock', 'with_shipping', 'single_pack', 'weight', 'is_available', 'price', 'created_date', 'modified_date',)
    inlines = [ProductVariationGalleryInline]

    def display_category_name(self, obj):
        return obj.product.category.category_name if obj.product.category else None
    
    display_category_name.short_description = "Category Name"
    display_category_name.admin_order_field = 'product__category' 


# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Type)
admin.site.register(ProductGallery)
admin.site.register(ProductVariationGallery)