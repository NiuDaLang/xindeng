# settlements/tasks.py
from celery import shared_task
from django.core.management import call_command

@shared_task
def audit_missing_settlement_lines_task():
    call_command('audit_missing_settlement_lines')