# accounts/tasks.py
import datetime
from celery import shared_task
from .utils import get_current_solar_term_period
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import opencc
from .data import SOLAR
from datetime import timedelta
from django.utils import timezone
from .models import AdminTrapHit

import logging
logger = logging.getLogger(__name__)


def get_solar_term():
    today = datetime.date.today()
    current_term, start_date = get_current_solar_term_period(today)
    term_en = SOLAR[current_term]
    trad_term = None
    if current_term:
        translator = opencc.OpenCC('s2t.json')
        trad_term = translator.convert(current_term)
    return trad_term, term_en

@shared_task
def update_solar_term_broadcast():
    term, term_en = get_solar_term()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "solar_updates", 
        {"type": "solar_message", "term": term, "term_en": term_en}
    )

@shared_task
def purge_old_admin_trap_hits(days=90):
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = AdminTrapHit.objects.filter(created_at__lt=cutoff).delete()
    return deleted

@shared_task
def purge_old_login_events(days=180):
    from .models import LoginEvent
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = LoginEvent.objects.filter(created_at__lt=cutoff).delete()
    return deleted


@shared_task(name="accounts.tasks.send_campaign_announcement_email_task")
def send_campaign_announcement_email_task(announcement_id):
    """
    Resolve the recipient set for a CampaignAnnouncement and dispatch
    the email to each recipient.

    Recipient resolution is at the top of this task rather than in
    the admin action so:
      * the admin action stays trivially fast (one row queued per
        announcement),
      * a slow recipient lookup can't block the admin request,
      * any change to the scope predicate is a one-file change
        (this task) rather than a two-file change.

    Blind re-send: every invocation resolves the CURRENT recipient
    set and dispatches to all of them. No receipt tracking. An
    announcement run twice will send twice; that is the "edit and
    re-send" workflow's contract.
    """
    from accounts.models import CampaignAnnouncement
    from creators.models import CreatorProfile
    from store.models import Product
    from django.db.models import Q
    from emails.utils import send_campaign_announcement_email

    try:
        announcement = CampaignAnnouncement.objects.select_related(
            'perk',
        ).get(id=announcement_id)
    except CampaignAnnouncement.DoesNotExist:
        return f"Announcement {announcement_id} not found."

    if not announcement.perk.is_active:
        return (
            f"Announcement {announcement_id} skipped: parent perk "
            f"{announcement.perk.code} is inactive."
        )

    if announcement.recipient_scope == CampaignAnnouncement.RecipientScope.ALL_VERIFIED_ARTISANS:
        artisan_user_ids = list(
            CreatorProfile.objects
            .filter(is_verified=True)
            .values_list('user_id', flat=True)
        )
    else:
        # ELIGIBLE_ARTISANS — an artisan is eligible if they own at least
        # one variation that would clear line_participates_in_platform_perk
        # minus the enrolment check (the announcement is what prompts the
        # enrolment, so enrolment status is irrelevant to recipient
        # selection).
        artisan_user_ids = list(
            CreatorProfile.objects
            .filter(
                is_verified=True,
                products__status='Published',
                products__is_deleted=False,
                products__is_active=True,
                products__variations__is_available=True,
                products__variations__platform_commission_pct__gt=0,
            )
            .filter(
                Q(products__variations__original_price__isnull=True)
                | Q(products__variations__price__gte=F('products__variations__original_price'))
            )
            .values_list('user_id', flat=True)
            .distinct()
        )

    # Dispatch one email per recipient. Failure on one recipient
    # (bad address, transient SMTP) should not abort the batch.
    sent = 0
    failed = 0
    for user_id in artisan_user_ids:
        try:
            ok = send_campaign_announcement_email(announcement.id, user_id)
            if ok:
                sent += 1
            else:
                failed += 1
        except Exception as exc:
            logger.exception(
                "send_campaign_announcement_email_task: recipient %s failed: %s",
                user_id, exc,
            )
            failed += 1

    # Stamp the announcement row. This is what "send_count" means —
    # successes, not attempts. A retry after a partial failure will
    # increment further; the number tells the admin "how many emails
    # have gone out for this announcement," which is the useful
    # quantity.
    announcement.send_count = F('send_count') + sent
    announcement.last_sent_at = timezone.now()
    announcement.save(update_fields=['send_count', 'last_sent_at'])

    return (
        f"Announcement {announcement_id} dispatched: "
        f"{sent} sent, {failed} failed."
    )