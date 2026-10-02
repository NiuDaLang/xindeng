# blog.context_processors.py
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from taggit.models import Tag
from .models import Post


def blog_sidebar(request):
    # 1. Tag Cloud Logic
    tags = Tag.objects.annotate(
        post_count=Count('post', filter=Q(post__status='Published', post__creator__isnull=True))
    ).filter(post_count__gt=0).order_by('-post_count')

    # 2. Monthly Archive Logic
    archives = Post.objects.filter(status='Published', creator__isnull=True) \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(post_count=Count('id')) \
        .order_by('-month')

    return {
        'sidebar_tags': tags,
        'sidebar_archives': archives,
    }


def blog_review_count(request):
    """
    Provide the pending-blog-review count to any template render.
    Only queries the DB for authenticated superusers — safe for all pages.
    """
    if not request.user.is_authenticated:
        return {}
    if not getattr(request.user, "is_superadmin", False):
        return {}

    return {
        "pending_blog_count": Post.objects.filter(status="Pending").count(),
    }