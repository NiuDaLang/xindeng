# blog.tasks.py
import requests
import logging
from celery import shared_task


logger = logging.getLogger(__name__)


@shared_task
def send_blog_submission_email_task(post_id):
    from emails.utils import send_blog_submission_notification
    send_blog_submission_notification(post_id)


@shared_task
def send_blog_review_result_email_task(post_id, approved, note=''):
    from emails.utils import send_blog_review_result_notification
    send_blog_review_result_notification(post_id, approved, note)