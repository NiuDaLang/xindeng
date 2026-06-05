from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import Account
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Comment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="user_comments")
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ip = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=True)
     # Threading: Allows comments to reply to other comments (e.g., forum style)
    parent_comment = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    # Product-Specific Field (Nullable) Star rating (1-5). Only applicable to Product reviews.
    rating = models.FloatField()
    # Generic Relationship Fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment/Review"
        verbose_name_plural = "Comments & Reviews"

    def __str__(self):
        parent_type = self.content_type.model.capitalize()
        return f"Comment by {self.user.username} on {parent_type} - ID: {self.object_id} - {self.content_type}"
    
    @property
    def is_review(self):
        return self.rating is not None
