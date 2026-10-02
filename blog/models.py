# blog/models.py
from django.db import models
from accounts.models import Account
from django_ckeditor_5.fields import CKEditor5Field
from taggit_selectize.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.urls import reverse
from creators.utils import clean_blog_body
from django.utils.text import slugify


# Create your models here.
POST_CATEGORY = (
    ("Art", "Art｜繪畫"),
    ("Photography", "Photography｜攝影"),
    ("Design", "Design｜設計"),
    ("Music", "Music｜音樂"),
    ("Spirituality", "Spirituality｜靈性"),
    ("Healing", "Healing｜療癒"),
    ("Promotion", "Promotion｜活動"),
    ("Other", "Other｜其他"),
)
POST_TYPE = (
    ("Blog", "Blog｜隨筆"),
    ("News", "News｜資訊"),
)
STATUS_CHOICES = (
    ("Draft",       "Draft｜草稿"),
    ("Pending",     "Pending Review｜待審核"),
    ("Published",   "Published｜已發布"),
    ("Rejected",    "Rejected｜未通過"),
    ("Unpublished", "Unpublished｜已下架"),
)


class Post(models.Model):
    title               = models.CharField(max_length=100)
    slug                = models.SlugField(max_length=150, unique=True, blank=True, allow_unicode=True)
    short_description   = models.TextField(max_length=500)
    post_category       = models.CharField(max_length=100, choices=POST_CATEGORY, default="Other")
    author              = models.ForeignKey(
                            Account, on_delete=models.CASCADE, related_name='author'
                          )
    creator             = models.ForeignKey(
                            'creators.CreatorProfile',
                            on_delete=models.SET_NULL,
                            null=True, blank=True,
                            related_name='posts',
                          )
    location            = models.CharField(max_length=100, blank=True)
    featured_image      = models.ImageField(upload_to='blog/featured_images/%Y/%m/%d', blank=True, null=True, help_text=("Required before submitting for review; optional for drafts. ""｜提交審核前為必填；草稿可留空。"))
    blog_body           = CKEditor5Field(config_name='extends', blank=True, null=True)
    post_type           = models.CharField(max_length=100, choices=POST_TYPE, default="Blog")
    is_featured         = models.BooleanField(default=False)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    bg_color            = models.CharField(
                            max_length=7, default="#f7f5f5", blank=True,
                            validators=[RegexValidator(
                                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                                message='Enter a valid hex color code (e.g., #FFFFFF)',
                            )]
                          )
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    tags                = TaggableManager()
    comments            = GenericRelation('reviews.Comment', related_query_name='post')

    # blog/models.py — inside class Post
    is_deleted          = models.BooleanField(
                                default=False,
                                help_text="Soft delete flag. Deleted posts are hidden from artisan and public views but preserved for audit.",
                            )

    def __str__(self):
        return self.title

    @property
    def has_been_edited(self):
        return self.created_at.replace(microsecond=0) != self.updated_at.replace(microsecond=0)

    def get_url(self):
        return reverse("post", args=[self.slug])

    # ── Helper: is this post currently in review?
    @property
    def is_under_review(self):
        return self.status == "Pending"

    # ── Helper: latest review note (for the artisan to see)
    @property
    def latest_review_log(self):
        return self.review_logs.order_by('-created_at').first()

    @property
    def can_be_deleted_by_artisan(self):
        """Artisans may only soft-delete Drafts, Rejected, or Unpublished posts."""
        return self.status in ("Draft", "Rejected", "Unpublished")

    @property
    def is_editable_by_artisan(self):
        return self.status in ("Draft", "Rejected", "Unpublished")

    @property
    def image_dimensions(self):
        if not self.featured_image:
            return None
        from core.image_utils import get_image_dimensions
        return get_image_dimensions(self.featured_image.name)

    @property
    def is_portrait(self):
        dims = self.image_dimensions
        return bool(dims and dims[1] > dims[0])

    @property
    def is_landscape(self):
        dims = self.image_dimensions
        return bool(dims and dims[0] > dims[1])

    @property
    def is_square(self):
        dims = self.image_dimensions
        return bool(dims and dims[0] == dims[1])

    @property
    def hero_container_style(self):
        """
        Inline style for the hero container.
        
        Returns something like 'aspect-ratio: 1600 / 900;' — matching the
        source image's natural ratio, but clamped to [4/5, 16/9] so no
        single image can distort the layout.
        """
        dims = self.image_dimensions
        if not dims:
            return "aspect-ratio: 4 / 3;"
        
        w, h = dims
        ratio = w / h
        
        # Clamp
        if ratio > 16 / 9:
            return "aspect-ratio: 16 / 9;"
        if ratio < 1 / 2:                   # was 4/5
            return "aspect-ratio: 1 / 2;"
        
        return f"aspect-ratio: {w} / {h};"

    def _generate_unique_slug(self):
        base = slugify(self.title, allow_unicode=True) or "post"
        base = base[:150]
        slug = base
        n = 1
        while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            suffix = f"-{n}"
            slug = f"{base[:150 - len(suffix)]}{suffix}"
            n += 1
        return slug

    def save(self, *args, **kwargs):
        if self.blog_body:
            self.blog_body = clean_blog_body(self.blog_body)
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


class BlogPostReviewLog(models.Model):
    """
    Audit trail for every state change of a Post.
    Both the artisan and the admin can see this on the post's detail page.
    """
    ACTION_CHOICES = (
        ("submitted", "Submitted for Review｜提交審核"),
        ("approved",  "Approved｜審核通過"),
        ("rejected",  "Rejected｜審核未通過"),
        ("withdrawn", "Withdrawn｜作者撤回"),
        ("published", "Published Directly｜直接發布"),  # 管理員操作
        ("deleted_by_author", "Deleted by Author｜作者刪除"),
        ("unpublished", "Unpublished｜下架"),
    )

    post        = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='review_logs')
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    actor       = models.ForeignKey(
                    Account, on_delete=models.SET_NULL,
                    null=True, blank=True, related_name='review_actions'
                  )
    note        = models.TextField(blank=True, help_text="Optional comment for this action.")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blog Post Review Log'
        verbose_name_plural = 'Blog Post Review Logs'

    def __str__(self):
        return f"{self.post.title} — {self.get_action_display()} @ {self.created_at:%Y-%m-%d %H:%M}"
