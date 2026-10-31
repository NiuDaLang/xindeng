# creators/context_processors.py
"""
Context processors for the creators app.

Mirrors accounts.context_processors.product_review_count and
blog.context_processors.blog_review_count: a superadmin-only badge
that must be present on every page the sidebar renders on. Only
authenticated superusers trigger the DB query.
"""


def artisan_message_count(request):
    """
    Provide the count of unread ArtisanAdminMessage rows to any
    template render. Only queries the DB for authenticated
    superusers — safe for all pages.

    This is the ADMIN-side counter (across all artisans). Do not
    confuse it with creators.context.artisan_dashboard_context's
    unread_admin_messages_count, which is the ARTISAN-side counter
    (for a single artisan's own thread). They are siblings on the
    same model, but they answer different questions and live in
    different places.
    """
    if not request.user.is_authenticated:
        return {}
    if not getattr(request.user, "is_superadmin", False):
        return {}

    from creators.models import ArtisanAdminMessage
    from django.contrib.auth import get_user_model
    Account = get_user_model()
    admin_user = Account.objects.filter(is_superadmin=True).first()
    return {
        "pending_artisan_message_count": ArtisanAdminMessage.objects.filter(
            is_read=False,
        ).exclude(sender=admin_user).count(),
    }
