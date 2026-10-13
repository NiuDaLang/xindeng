# creators/context.py
from datetime import date
from django.conf import settings
from orders.models import OrderProduct
from django.db.models import Q
from .models import ArtisanChatMessage


def artisan_dashboard_context(request):
    """
    Shared context for every artisan dashboard view.

    pending_dispatch_count counts lines where the artisan has a pending
    action (physical shipments, custom-digital files).

    unread_messages_count reflects the artisan's own inbox. It was a
    placeholder until ArtisanChatMessage shipped; do NOT repoint it at
    accounts.ChatMessage — that model is the member↔admin channel and
    has nothing to do with the artisan's sidebar.
    """
    profile = request.user.creator_profile

    pending_dispatch = OrderProduct.objects.filter(
        fulfilled_by=profile,
        is_dispatched=False,
    ).filter(
        Q(product__is_physical=True)
        | Q(product__is_digital=True, product__digital_fulfillment_type="CUSTOM")
    ).count()

    unread_messages = ArtisanChatMessage.objects.filter(
        artisan=profile,
        is_read=False,
    ).count()

    return {
        "profile": profile,
        "pending_dispatch_count": pending_dispatch,
        "unread_messages_count": unread_messages,
    }