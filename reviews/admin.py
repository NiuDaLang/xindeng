from django.contrib import admin
from .models import Comment
from django.contrib.contenttypes.admin import GenericTabularInline

# Register your models here.
class CommentInline(GenericTabularInline):
    model = Comment
    ck_field = "content_type"
    ck_fk_field = "object_id"

    fields = ("user", "text", "rating", "is_approved")
    readonly_fields = ("created_at", "ip")
    extra = 1  # Number of extra inline forms to display (0 for no extra forms
    can_delete = True  # Allow deleting inline forms
    verbose_name = "Associated Comment or Review"
    verbose_name_plural = "Associated Comments or Reviews"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "is_approved", "is_approved", "ip", "created_at", "rating_display")
    list_filter = ("is_approved", "created_at", "content_type")
    search_fields = ("text", "user__username", "user__email")

    # Customize the form in the admin to group related fields
    fieldsets = (
        (None, {
            "fields": ("user", "text", "created_at", "is_approved", "ip")
        }),
        ("Review Details", {
            "fields": ("rating",),
            "description": "Rating is only used for Product Reviews."
        }),
        ("Treading", {
            "fields": ("parent_comment",),
        }),
        ("Target Object (Generic)", {
            "fields": ("content_type", "object_id"),
            "classes": ("collapse",),
        }),
    )

    def content_object_summary(self, obj):
        return f"{obj.content_type.model.capitalize()} - ID: {obj.object_id}"
    content_object_summary.short_description = "Target Object"

    def rating_display(self, obj):
        return f"{obj.rating} stars" if obj.is_review else "N/A"
    rating_display.short_description = "Rating"


admin.site.register(Comment, CommentAdmin)