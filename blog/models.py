from django.db import models
from accounts.models import Account
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import RegexValidator
from django.urls import reverse


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
    ("Draft", "Draft"),
    ("Published", "Published")
)


class Post(models.Model):
    title               = models.CharField(max_length=100)
    slug                = models.SlugField(max_length=150, unique=True, blank=True)
    short_description   = models.TextField(max_length=500)
    post_category       = models.CharField(max_length=100, choices=POST_CATEGORY, default="Other")
    author              = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='author')
    location            = models.CharField(max_length=100, blank=True)
    featured_image      = models.ImageField(upload_to='blog/featured_images/%Y/%m/%d')
    blog_body           = CKEditor5Field(config_name='extends', blank=True, null=True)
    post_type           = models.CharField(max_length=100, choices=POST_TYPE, default="Blog")  
    is_featured         = models.BooleanField(default=False)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    bg_color            = models.CharField(max_length=7, default="#f7f5f5", blank=True, validators=[RegexValidator(
                                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                                message='Enter a valid hex color code (e.g., #FFFFFF)',
                            ),])
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    tags                = TaggableManager()

    comments            = GenericRelation('reviews.Comment', related_query_name='post')

    def __str__(self):
        return self.title
    
    @property
    def has_been_edited(self):
        """
        Returns True if the updated_at timestamp is significantly different 
        from the created_at timestamp (i.e., beyond microsecond variance).
        from django.urls import reverse
        """
        # Truncate microseconds for comparison
        return self.created_at.replace(microsecond=0) != self.updated_at.replace(microsecond=0)
    

    def get_url(self):
        return reverse("post", args=[self.slug])
