from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Core utilities"

    def ready(self):
        # Register signal handlers
        from . import signals  # noqa: F401
        from . import file_cleanup  # orphan file cleanup

