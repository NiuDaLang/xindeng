# creators.models.py
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit_selectize.managers import TaggableManager
from accounts.data import DESTINATIONS_MAINLAND_CHINA
from pypinyin import slug as pinyin_slug  # add at top

# creators/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from accounts.data import DESTINATIONS_MAINLAND_CHINA


class CraftType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'label']

    def __str__(self):
        return self.label


class CreatorProfile(models.Model):
    user            = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='creator_profile',
    )
    display_name    = models.CharField(max_length=100)
    slug            = models.SlugField(max_length=150, unique=True, blank=True)
    tagline         = models.CharField(max_length=200, blank=True)
    bio             = models.TextField(blank=True)

    province        = models.CharField(
                        max_length=50,
                        choices=DESTINATIONS_MAINLAND_CHINA,
                        blank=True,
                      )
    city            = models.CharField(max_length=50, blank=True)

    craft_types     = models.ManyToManyField(CraftType, blank=True, related_name='artisans')

    avatar          = models.ImageField(upload_to='creators/avatars/', blank=True, null=True)
    banner          = models.ImageField(upload_to='creators/banners/', blank=True, null=True)

    is_verified     = models.BooleanField(default=False)
    is_premium      = models.BooleanField(default=False)

    # 🌟 NEW: Layout selection
    PAGE_TEMPLATE_CHOICES = [
        ('A', 'Banner-Led｜橫幅主導'),
        ('B', 'Portrait-Led｜肖像主導'),
        ('C', 'Text-Led｜文本主導'),      # default
        ('D', 'Custom Premium｜客製精選'),  # admin only, requires is_premium=True
    ]
    page_template   = models.CharField(
                        max_length=2,
                        choices=PAGE_TEMPLATE_CHOICES,
                        default='C',
                        help_text="Which layout template renders this artisan's public page.",
                      )

    # 🌟 NEW: Premium custom-page metadata
    premium_page_slug       = models.SlugField(
                                max_length=80,
                                blank=True,
                                help_text="Human-readable alias for the custom premium template "
                                        "(e.g., 'atelier-lumiere'). The actual template file is "
                                        "named by pk: '<pk>_premium_page.html'.",
                              )
    premium_page_published  = models.BooleanField(
                                default=False,
                                help_text="Only render the custom premium template when True. "
                                        "Otherwise, fall back to the standard layout.",
                              )

    website         = models.URLField(blank=True)
    instagram       = models.CharField(max_length=100, blank=True)
    wechat_qr       = models.ImageField(
                        upload_to='creators/wechat_qr/',
                        blank=True,
                        null=True,
                        help_text="Upload your WeChat QR code image.｜上傳您的微信二維碼圖片。",
                      )

    dispatch_address        = models.ForeignKey(
                                'accounts.Address',
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='dispatch_for_creators',
                                help_text="Default address from which this artisan dispatches items.",
                              )

    tags = TaggableManager(blank=True)

    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_premium', 'display_name']

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.display_name) or pinyin_slug(self.display_name) or "artisan"
            self.slug = self._unique_slug(base)
        super().save(*args, **kwargs)

    def _unique_slug(self, base):
        """
        Ensure slug uniqueness. First tries `base`; on collision appends
        `-{pk}` if available, else `-{n}` counter.
        """
        base = base[:140]  # leave room for suffix
        qs = CreatorProfile.objects.filter(slug=base)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if not qs.exists():
            return base

        # Collision — use PK if we have one, else numeric counter
        if self.pk:
            return f"{base}-{self.pk}"

        n = 2
        while CreatorProfile.objects.filter(slug=f"{base}-{n}").exists():
            n += 1
        return f"{base}-{n}"

    def clean(self):
        """Model-level validation — enforced by Django admin forms."""
        super().clean()

        # Option D is reserved for premium artisans
        if self.page_template == 'D' and not self.is_premium:
            raise ValidationError({
                'page_template': "Custom layout (D) is reserved for premium artisans. "
                                 "Set 'is_premium' to True, or choose a standard layout."
            })

        # If page_template is NOT D, clear premium_page fields
        # (keeps the model tidy — flags reflect current state)
        if self.page_template != 'D':
            self.premium_page_published = False

    def get_absolute_url(self):
        return reverse('artisan_detail', kwargs={'slug': self.slug})