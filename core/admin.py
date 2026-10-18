# core/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(admin.ModelAdmin):
    """
    Singleton admin: exactly one row exists, and the page is
    read-mostly — the point is the ddp_enabled toggle, not a list of
    records. has_add_permission=False prevents creating a second row;
    has_delete_permission=False prevents deleting the only one. The
    change form is the entire UI.
    """

    list_display = ("__str__", "updated_at")
    readonly_fields = ("updated_at", "policy_link")

    fieldsets = (
        ("DDP availability", {
            "fields": ("ddp_enabled", "policy_link"),
            "description": (
                "Toggles whether checkout shows the DDP "
                "(duties-prepaid) notice or the DAP (duties-at-"
                "destination) notice. See docs/物流方案討論稿 for "
                "the underlying policy decision."
            ),
        }),
        ("Audit", {
            "fields": ("updated_at",),
            "classes": ("collapse",),
        }),
    )

    def policy_link(self, obj):
        return format_html(
            "<em>See:</em> <code>docs/物流方案討論稿</code> — "
            "the policy decision this flag gates."
        )
    policy_link.short_description = "Policy reference"

    def has_add_permission(self, request):
        # Singleton: at most one row. If it does not exist yet, the
        # first change-form visit creates it via get_solo(), which
        # Django will not treat as "add" from the admin's perspective
        # — see get_object below.
        return not SiteConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirect the changelist to the singleton change form. The
        # list view is meaningless for a single row.
        from django.shortcuts import redirect
        obj = SiteConfig.get_solo()
        return redirect(
            f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change",
            obj.pk,
        )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Explicit cache invalidation even though SiteConfig.save()
        # does it — defence against a future refactor that skips
        # save().
        from django.core.cache import cache
        cache.delete("site_config:ddp_enabled")