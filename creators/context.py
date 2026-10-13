# creators/context.py
from datetime import date
from django.conf import settings
from orders.models import OrderProduct
from accounts.models import ChatMessage
from django.db.models import Q


def artisan_dashboard_context(request):
    """
    Shared context for every artisan dashboard view.

    Single source of truth. creators.views must call this, not
    re-define its own copy — a local duplicate caused the sidebar
    counters to drift silently (the local copy hardcoded
    unread_messages_count to 0 while this one queried a real table).

    pending_dispatch_count counts lines where the artisan has a
    pending action:

      * physical shipments awaiting a tracking number
      * CUSTOM digital files awaiting upload / admin approval

    INSTANT digital and voucher lines auto-fulfil at payment time and
    are excluded — the artisan has nothing left to do on those.

    unread_messages_count is currently a placeholder. It will be
    wired to the future ArtisanChatMessage model. Do not repoint it
    to ChatMessage — that model is the member↔admin channel and is
    not the artisan's own inbox.
    """
    profile = request.user.creator_profile

    pending_dispatch = OrderProduct.objects.filter(
        fulfilled_by=profile,
        is_dispatched=False,
    ).filter(
        Q(product__is_physical=True)
        | Q(product__is_digital=True, product__digital_fulfillment_type="CUSTOM")
    ).count()

    return {
        "profile": profile,
        "pending_dispatch_count": pending_dispatch,
        # Placeholder until ArtisanChatMessage ships (Option A in the
        # messages design; see next session's shape memo).
        "unread_messages_count": 0,
    }