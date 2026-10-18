# core/models.py
"""
Site-level singletons and shared configuration models.

Models in this app are cross-cutting settings, not user-domain data.
The first is SiteConfig, a singleton holding runtime flags that an
admin can flip without a deploy (currently only DDP availability).
"""

from django.db import models


class SiteConfig(models.Model):
    """
    Singleton row holding site-wide runtime flags.

    Exactly one row exists (pk=1), enforced by save(). Read via
    core.settings_helpers.is_ddp_enabled(), which caches the value;
    do not query SiteConfig.objects directly from hot paths.
    """

    ddp_enabled = models.BooleanField(
        default=False,
        help_text=(
            "When True, checkout shows the DDP (duties-prepaid) notice "
            "and the tax estimator in carts/tax.py is consulted. When "
            "False (default), checkout shows the DAP (duties-at-"
            "destination) notice and tax estimates are not surfaced. "
            "See docs/物流方案討論稿 for the policy decision this flag "
            "gates."
        ),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site configuration"
        verbose_name_plural = "Site configuration"

    def __str__(self):
        return f"SiteConfig (ddp_enabled={self.ddp_enabled})"

    def save(self, *args, **kwargs):
        # Force the singleton. pk is always 1.
        self.pk = 1
        super().save(*args, **kwargs)
        # Invalidate the read-through cache so admin flips take effect
        # immediately, not after the TTL.
        from django.core.cache import cache
        cache.delete("site_config:ddp_enabled")

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj