# core/tasks.py
"""
Celery tasks for deferred image optimisation.
"""

from __future__ import annotations

import logging

from celery import shared_task
from django.apps import apps

from .image_utils import (
    is_already_optimized,
    is_skippable,
    optimize_image,
    save_optimized_to_field,
)

logger = logging.getLogger(__name__)


@shared_task(
    name="core.optimize_image_task",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
)
def optimize_image_task(self, model_label, pk, field_name, opts=None):
    opts = opts or {}

    try:
        app_label, model_name = model_label.split(".", 1)
        model = apps.get_model(app_label, model_name)
    except (ValueError, LookupError):
        logger.warning("optimize_image_task: unknown model label %r", model_label)
        return

    instance = model.objects.filter(pk=pk).first()
    if instance is None:
        logger.info("optimize_image_task: %s pk=%s no longer exists", model_label, pk)
        return

    field_file = getattr(instance, field_name, None)
    if is_skippable(field_file) or is_already_optimized(field_file):
        return

    result = optimize_image(field_file, **opts)
    if result is None:
        return

    content, new_name = result
    save_optimized_to_field(instance, field_name, content, new_name)

    logger.info(
        "optimize_image_task: optimised %s.%s pk=%s -> %s",
        model_label, field_name, pk, new_name,
    )