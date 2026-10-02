# accounts.context_processors.py
from django.conf import settings


def get_google_api(request):
    return {
        "GOOGLE_API_KEY": getattr(settings, "GOOGLE_API_KEY", None)
    }


def product_review_count(request):
    """
    Provide the pending-product-review count to any template render.
    Only queries the DB for authenticated superusers — safe for all pages.
    """
    if not request.user.is_authenticated:
        return {}
    if not getattr(request.user, "is_superadmin", False):
        return {}

    from store.models import Product
    return {
        "pending_product_count": Product.objects.filter(
            status="Pending", is_deleted=False
        ).count(),
    }