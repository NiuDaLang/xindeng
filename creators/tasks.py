# creators/tasks.py
"""
Thin Celery wrappers for the creators app.

All heavy lifting lives in emails.utils. The wrappers exist so the
call site can fire-and-forget via transaction.on_commit without
importing the email module at view-module import time (which would
create a cycle through emails.utils → creators.models).
"""

from celery import shared_task
import logging

from emails.utils import send_artisan_admin_message_email

logger = logging.getLogger(__name__)


@shared_task(name="creators.tasks.send_artisan_admin_message_email_task")
def send_artisan_admin_message_email_task(message_id):
    """
    Celery wrapper: dispatch the artisan-ward admin-message
    notification email.

    Thin — all rendering and delivery lives in
    emails.utils.send_artisan_admin_message_email.
    """
    try:
        sent = send_artisan_admin_message_email(message_id)
        if sent:
            return f"Artisan admin-message notification sent (message={message_id})."
        return f"No artisan to notify (message={message_id})."
    except Exception as exc:
        logger.exception(
            f"💥 Artisan admin-message email failed (message={message_id}): {exc}"
        )
        raise