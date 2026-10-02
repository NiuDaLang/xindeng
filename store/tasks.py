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