from django.contrib import admin
from .models import Comment, CommentImage
from django.contrib.contenttypes.admin import GenericTabularInline

# Optional: Add this inline to view/manage attached images directly inside the comment editor
class CommentImageInline(admin.TabularInline):
    model = CommentImage
    extra = 1

class CommentInline(GenericTabularInline):
    model = Comment
    ct_field = "content_type"  # Fixed typo: ct_field, not ck_field
    ct_fk_field = "object_id"  # Fixed typo: ct_fk_field, not ck_fk_field

    fields = ("user", "text", "rating", "is_approved")
    extra = 1  
    can_delete = True  
    verbose_name = "Associated Comment or Review"
    verbose_name_plural = "Associated Comments or Reviews"


class CommentAdmin(admin.ModelAdmin):
    # Added "content_object_summary" here to replace raw content_type filtering if desired
    list_display = ("user", "is_approved", "ip", "created_at", "rating_display", "content_object_summary")
    list_filter = ("is_approved", "created_at", "content_type")
    search_fields = ("text", "user__username", "user__email")

    # 🌟 FIX: Register non-editable fields as read-only for the main model admin view
    readonly_fields = ("created_at",)

    # Customize the form in the admin to group related fields
    fieldsets = (
        (None, {
            "fields": ("user", "text", "created_at", "is_approved", "ip") # 🌟 WORKS NOW: Because it's in readonly_fields
        }),
        ("Review Details", {
            "fields": ("rating",),
            "description": "Rating is only used for Product Reviews."
        }),
        ("Threading", {  # Fixed minor typo "Treading" -> "Threading"
            "fields": ("parent_comment",),
        }),
        ("Target Object (Generic)", {
            "fields": ("content_type", "object_id"),
            "classes": ("collapse",),
        }),
    )

    # Wire up image attachments inline so you can see reviewer photos
    inlines = [CommentImageInline]

    def content_object_summary(self, obj):
        return f"{obj.content_type.model.capitalize()} - ID: {obj.object_id}"
    content_object_summary.short_description = "Target Object"

    def rating_display(self, obj):
        return f"{obj.rating} stars" if obj.is_review else "N/A"
    rating_display.short_description = "Rating"


admin.site.register(Comment, CommentAdmin)