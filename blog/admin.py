from django.contrib import admin
from .models import Post
from reviews.admin import CommentInline


# Register your models here.
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "slug", "post_category", "post_type", "author", "status", "is_featured", "created_at", "updated_at")
    search_fields = ("id", "title", "post_category", "status", "is_featured", "tags")
    inlines = [CommentInline,]


admin.site.register(Post, PostAdmin)
