# creators/context.py
from datetime import date
from django.conf import settings
from orders.models import OrderProduct
from django.db.models import Q
from .models import ArtisanChatMessage, ArtisanAdminMessage


def artisan_dashboard_context(request):
    """
    Shared context for every artisan dashboard view.

    pending_dispatch_count counts lines where the artisan has a pending
    action (physical shipments, custom-digital files).

    unread_messages_count reflects the artisan's customer-thread inbox
    (ArtisanChatMessage). unread_admin_messages_count reflects the
    artisan's admin-thread inbox (ArtisanAdminMessage). They are
    sibling counters on separate models; do NOT repoint one at the
    other, and do NOT merge the two queries. The sidebar renders both
    independently.
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

    unread_admin_messages = ArtisanAdminMessage.objects.filter(
        artisan=profile,
        is_read=False,
    ).exclude(sender=profile.user).count()

    return {
        "profile": profile,
        "pending_dispatch_count": pending_dispatch,
        "unread_messages_count": unread_messages,
        "unread_admin_messages_count": unread_admin_messages,
    }