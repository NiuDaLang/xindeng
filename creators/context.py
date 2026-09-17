# creators/context.py
from datetime import date
from django.conf import settings
from orders.models import OrderProduct
from accounts.models import ChatMessage


def artisan_dashboard_context(request):
    """
    Shared context for every artisan dashboard view.
    Call this from each dashboard view and merge into the context dict.
    """
    profile = request.user.creator_profile

    pending_dispatch = OrderProduct.objects.filter(
        fulfilled_by=profile,
        is_dispatched=False,
    ).count()

    unread_messages = ChatMessage.objects.filter(
        receiver=request.user,
        is_read=False,
    ).count()

    return {
        'profile': profile,
        'pending_dispatch_count': pending_dispatch,
        'unread_messages_count': unread_messages,
        # ... any other sidebar-wide data ...
    }