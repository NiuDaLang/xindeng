from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from taggit.models import Tag
from .models import Post

def blog_sidebar(request):
    # 1. Tag Cloud Logic
    tags = Tag.objects.annotate(
        post_count=Count('post', filter=Q(post__status='Published'))
    ).filter(post_count__gt=0).order_by('-post_count')

    # 2. Monthly Archive Logic
    archives = Post.objects.filter(status='Published') \
        .annotate(month=TruncMonth('created_at')) \
        .values('month') \
        .annotate(post_count=Count('id')) \
        .order_by('-month')

    return {
        'sidebar_tags': tags,
        'sidebar_archives': archives,
    }