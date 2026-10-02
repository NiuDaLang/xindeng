# blog/admin.py
from django.contrib import admin
from .models import Post, BlogPostReviewLog
from reviews.admin import CommentInline


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = (
        "title", "slug", "post_category", "post_type", "author",
        "status", "is_featured", "created_at", "updated_at", "is_deleted",
    )
    list_filter = ("is_deleted",)
    search_fields = ("id", "title", "post_category", "status", "is_featured", "tags")
    inlines = [CommentInline,]
    actions = ["soft_delete_posts", "restore_posts"]

    @admin.action(description="Soft-delete selected posts")
    def soft_delete_posts(self, request, queryset):
        # Only soft-delete Drafts/Rejected/Unpublished — matches the artisan rule.
        candidates = queryset.filter(status__in=("Draft", "Rejected", "Unpublished"), is_deleted=False)
        skipped = queryset.count() - candidates.count()
        updated = candidates.update(is_deleted=True)
        msg = f"Soft-deleted {updated} post(s)."
        if skipped:
            msg += f" Skipped {skipped} post(s) that are not Draft/Rejected/Unpublished."
        self.message_user(request, msg)

    @admin.action(description="Restore selected soft-deleted posts")
    def restore_posts(self, request, queryset):
        restored = queryset.filter(is_deleted=True).update(is_deleted=False)
        self.message_user(request, f"Restored {restored} post(s).")


@admin.register(BlogPostReviewLog)
class BlogPostReviewLogAdmin(admin.ModelAdmin):
    list_display = ("post", "action", "actor", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("post__title", "note")
    readonly_fields = ("post", "action", "actor", "note", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False