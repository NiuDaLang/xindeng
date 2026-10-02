# blog.views.py

from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from .models import Post
from django.contrib.contenttypes.models import ContentType
from reviews.forms import CommentForm
from django.core.paginator import Paginator
import random
from django.http import Http404
from taggit.models import Tag
from accounts.models import UserProfile
from reviews.models import Comment
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Post, BlogPostReviewLog
from .tasks import send_blog_review_result_email_task
from creators.models import CreatorProfile
from accounts.decorators import superuser_required


def all_posts(request):
    # 1. Base query for all published logs
    all_published_posts = Post.objects.filter(status="Published", creator__isnull=True, is_deleted=False).order_by("-created_at")

    # 🌟 NEW: separate query for the artisan tab
    artisan_posts = Post.objects.filter(status='Published', creator__isnull=False, creator__is_verified=True, is_deleted=False).select_related('creator').order_by('-created_at')[:5]
    # 2. Intercept Sidebar & Search Filters (Tag, Month, and Keyword Search)
    search_query = request.GET.get('q')
    tag_slug = request.GET.get('tag')
    month_query = request.GET.get('month') # Expects format 'YYYY-MM'

    if search_query:
        all_published_posts = all_published_posts.filter(
            Q(title__icontains=search_query) | 
            Q(short_description__icontains=search_query)
        )
    if tag_slug:
        all_published_posts = all_published_posts.filter(tags__slug=tag_slug)
    if month_query:
        try:
            year, month = month_query.split('-')
            all_published_posts = all_published_posts.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            pass # Ignore malformed query strings gracefully

    # 3. Dynamic Arrays for Tab-2 and Tab-3 (Filtered dynamically based on sidebar selections too!)
    blog_posts = all_published_posts.filter(post_type="Blog")
    news_posts = all_published_posts.filter(post_type="News")

    # 4. Standard Paginator loop logic (5 logs per layout track block)
    paginator = Paginator(all_published_posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 🌟 FIX: Extract the first 5 records out of the ACTIVE filtered queryset for Tab-1 display
    latest_five_posts = all_published_posts[:5]

    # 5. Sidebar Static Queries (These always query the global published pool so they remain visible)
    global_published = Post.objects.filter(status="Published", creator__isnull=True, is_deleted=False)
   
    popular_posts = global_published.filter(is_featured=True)[:5]
    if not popular_posts.exists():
        popular_posts = global_published.order_by("-created_at")[:5]

    tags_with_counts = Post.tags.filter(
        post__status="Published"
    ).annotate(
        post_count=Count('post')
    ).order_by('-post_count')[:12]

    archive_dates = global_published.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        post_count=Count('id')
    ).order_by('-month')

    context = {
        "page_title": "Art Blog｜心燈筆記",
        "page_obj": page_obj,
        "latest_five_posts": latest_five_posts,  # 🌟 RESTORED: Feeds perfectly back into Tab-1 loop
        "popular_posts": popular_posts,
        "tags_with_counts": tags_with_counts,
        "archive_dates": archive_dates,
        "blog_posts": blog_posts,
        "news_posts": news_posts,
        "artisan_posts": artisan_posts,
    }

    return render(request, 'blog/all_posts.html', context)


def all_posts_display(request, category):
    if category == 'Published':
        all_posts = Post.objects.filter(
            status="Published", creator__isnull=True, is_deleted=False
        ).order_by("-created_at")
    else:
        all_posts = Post.objects.filter(
            status="Published", post_type=category, creator__isnull=True, is_deleted=False
        ).order_by("-created_at")

    # pagination
    paginator = Paginator(all_posts, 10)
    page = request.GET.get("page")
    paged_posts = paginator.get_page(page)

    context = {
        "page_title": "All Posts｜所有筆記",
        "main_title": "All Posts｜所有筆記",
        "sub_title_1": "Digital Montage｜心燈蒙太奇",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Blog｜筆記",
        "bread_crumb_3": "All Posts｜所有筆記",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "bread_crumb_3_url": "/blog/posts/all_posts",
        "available_posts": paged_posts,
    }

    return render(request, "blog/all_posts_display.html", context)


def post(request, post_slug):
    # Retrieve the primary target blog entry record safely
    if request.user.is_authenticated and getattr(request.user, "is_superadmin", False):
        current_post = get_object_or_404(Post, slug=post_slug, is_deleted=False)
    else:
        current_post = get_object_or_404(Post, slug=post_slug, status="Published", is_deleted=False)
    
    # 🌟 RESTORED/FIXED STORYBOARD NAVIGATIONS: Chronological lookup replaces fragile paginator subsets
    same_stream = Post.objects.filter(status="Published", creator__isnull=(current_post.creator_id is None), is_deleted=False)
    previous_post = same_stream.filter(created_at__lt=current_post.created_at).order_by('-created_at').first()
    next_post = same_stream.filter(created_at__gt=current_post.created_at).order_by('created_at').first()
    
    has_prev = previous_post is not None
    has_next = next_post is not None

    # Sidebar Highlights Panel: Pulls a dynamic subset from other published records
    # sidebar_highlights = Post.objects.filter(status="Published").exclude(id=current_post.id).order_by('?')[:3]
    sidebar_highlights = same_stream.exclude(id=current_post.id).order_by('?')[:3]

    # 🌟 NEW MULTI-FRONT DATA MAPPING: Fetches comments securely using your GenericRelation path properties
    comments_list = current_post.comments.filter(is_approved=True, parent_comment__isnull=True)
    post_content_type = ContentType.objects.get_for_model(current_post)

    if request.user.is_authenticated:
        # Enforce profile structure instantiation to prevent NoneType rendering crashes on the card images
        UserProfile.objects.get_or_create(user=request.user)

    # Maintain your baseline randomized background asset index mappings
    random_img_num = random.randint(0, 4)
    random_img_path = f"/static/images/post/img_{random_img_num}.JPG"

    if current_post.creator:
        artisan_related_posts = (
            Post.objects
            .filter(creator=current_post.creator, status="Published", is_deleted=False)
            .exclude(id=current_post.id)
            .order_by("-created_at")[:5]
        )
        # also other artisans
        other_artisans = (
            CreatorProfile.objects
            .filter(is_verified=True)
            .exclude(id=current_post.creator.id)
            .order_by("-is_premium", "-created_at")[:4]
        )
    else:
        artisan_related_posts = []
        other_artisans = []

    context = {
        "main_title": "店主筆記｜Notes",
        "sub_title_1": current_post.title,
        "bread_crumb_1": "首頁｜Home",
        "bread_crumb_2": "筆記｜Notes",
        "bread_crumb_4": current_post.title,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        
        "post": current_post,
        "posts": sidebar_highlights, 
        "artisan_related_posts": artisan_related_posts,
        "other_artisans": other_artisans,
        
        "has_prev": has_prev,
        "previous_post": previous_post,
        "has_next": has_next,
        "next_post": next_post,
        "random_img_path": random_img_path,
        
        # Discussion Module Attributes Injections
        "comments_list": comments_list,
        "post_content_type_id": post_content_type.id,
    }

    return render(request, 'blog/post.html', context)


def posts_by_tag(request, tag_slug):
    # Fetch the tag object or return 404
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    # Filter published posts that contain this specific tag
    posts = Post.objects.filter(
        status='Published',
        creator__isnull=True,
        tags__in=[tag],
        is_deleted=False
    ).distinct().order_by('-created_at')

    # pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get("page")
    paged_posts = paginator.get_page(page)
    
    context = {
        "page_title": f"Tag｜標籤 - #{tag_slug}",
        "main_title": f"Tag｜標籤 - #{tag_slug}",
        "sub_title_1": "Keyword Spotlight｜思緒拾遺 ",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Blog｜筆記",
        "bread_crumb_3": "Tag｜標籤 #{tag_slug}",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "bread_crumb_3_url": f"/blog/tag/{tag_slug}/",
        "available_posts": paged_posts,
    }
    
    return render(request, 'blog/all_posts_display.html', context)


def post_archive_view(request, year, month):
    posts = Post.objects.filter(
        status='Published',
        creator__isnull=True,
        created_at__year=year,
        created_at__month=month,
        is_deleted=False
    ).order_by('-created_at')
    
    # Optional: Throw 404 if no posts exist for that month
    if not posts.exists():
        raise Http404("No posts found for this period.")
    
    # pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get("page")
    paged_posts = paginator.get_page(page)
    
    context = {
        "page_title": f"{year}-{month}",
        "main_title": f"{year}-{month}",
        "sub_title_1": "Traces of Time｜歲月留痕 ",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Blog｜筆記",
        "bread_crumb_3": f"{year}-{month}",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "bread_crumb_3_url": f"/blog/post/archive/{year}/{month}/",
        "available_posts": paged_posts,
    }

    return render(request, 'blog/all_posts_display.html', context)


@require_POST
@superuser_required
def review_blog_post_approve(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.status != "Pending":
        messages.error(request, "此筆記不在待審核狀態。｜Post is not pending review.")
        return redirect("dashboard", subpage="blog_review")

    with transaction.atomic():
        post.status = "Published"
        post.save(update_fields=["status"])

        BlogPostReviewLog.objects.create(
            post=post,
            action="approved",
            actor=request.user,
            note="",
        )

    # Stage C: email hook
    transaction.on_commit(
        lambda: send_blog_review_result_email_task.delay(post.id, True, "")
    )
    messages.success(request, f"已通過：{post.title}｜Approved.")
    return redirect("dashboard", subpage="blog_review")


@require_POST
@superuser_required
def review_blog_post_reject(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.status != "Pending":
        messages.error(request, "此筆記不在待審核狀態。｜Post is not pending review.")
        return redirect("dashboard", subpage="blog_review")

    note = request.POST.get("note", "").strip()
    if not note:
        messages.error(request, "拒絕時必須填寫理由。｜A reason is required when rejecting.")
        return redirect("dashboard", subpage="blog_review")

    with transaction.atomic():
        post.status = "Rejected"
        post.save(update_fields=["status"])

        BlogPostReviewLog.objects.create(
            post=post,
            action="rejected",
            actor=request.user,
            note=note,
        )

    # Stage C: email hook
    transaction.on_commit(
        lambda: send_blog_review_result_email_task.delay(post.id, False, note)
    )
    messages.success(request, f"已拒絕：{post.title}｜Rejected.")
    return redirect("dashboard", subpage="blog_review")


