# store/tasks.py
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_product_submission_email_task(product_id):
    from emails.utils import send_product_submission_notification
    send_product_submission_notification(product_id)


@shared_task
def send_product_review_result_email_task(product_id, approved, note=''):
    from emails.utils import send_product_review_result_notification
    send_product_review_result_notification(product_id, approved, note)


@shared_task
def send_product_deactivation_request_email_task(product_id):
    from emails.utils import send_product_deactivation_request_notification
    send_product_deactivation_request_notification(product_id)


@shared_task(name="tasks.send_vault_upload_pending_email_task")
def send_vault_upload_pending_email_task(upload_id):
    """Notify the admin that an artisan staged a digital file for review."""
    from emails.utils import send_vault_upload_pending_notification
    from store.models import ArtisanVaultUpload

    try:
        upload = ArtisanVaultUpload.objects.get(id=upload_id)
    except ArtisanVaultUpload.DoesNotExist:
        return f"Upload {upload_id} not found; notification skipped."

    # Only notify for rows that are still awaiting review. If the row
    # was already reviewed (unlikely given the on_commit dispatch
    # timing, but possible if a Celery worker was offline for a while),
    # skip the notification rather than telling the admin to look at
    # something that's already settled.
    if upload.status != "PENDING":
        return (
            f"Upload {upload_id} is {upload.status}, not PENDING; "
            f"notification skipped."
        )

    send_vault_upload_pending_notification(upload_id)
    return f"Vault upload notification sent for {upload_id}."