from django.apps import AppConfig


class CreatorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'creators'
    verbose_name = 'Artisans｜匠人'

    def ready(self):
        from . import signals  # noqa: F401  (registers the post_save handler)