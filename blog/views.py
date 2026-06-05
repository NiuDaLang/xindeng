from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import Post
from django.contrib.contenttypes.models import ContentType
from reviews.forms import CommentForm
from django.core.paginator import Paginator
import random
from django.http import Http404
from taggit.models import Tag


# Create your views here.
def all_posts(request):
    all_posts = Post.objects.filter(status="Published").order_by("-created_at")
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    latest_five_posts = all_posts[:5]
    blog_posts = all_posts.filter(post_type="Blog")
    news_posts = all_posts.filter(post_type="News")

    context = {
        "page_title": "Blog｜筆記",
        "main_title": "Blog｜筆記",
        "sub_title_1": "Life's fleeting moments are but stars that coalesce into a dazzling night",
        "sub_title_2": "生活的點點滴滴，就像星空點點，匯聚成燦爛的夜空",
        "bread_crumb_1": "Home｜首頁",
        "bread_crumb_2": "Blog｜筆記",
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "posts": all_posts,
        "page_obj": page_obj,
        "latest_five_posts": latest_five_posts,
        "blog_posts": blog_posts,
        "news_posts": news_posts
    }

    return render(request, 'blog/all_posts.html', context)

def all_posts_display(request, category):
    if category=='Published':
        all_posts = Post.objects.filter(status="Published").order_by("-created_at")
    else:
        all_posts = Post.objects.filter(status="Published", post_type=category).order_by("-created_at")

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


# def post(request, slug):
def post(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    posts = Post.objects.filter(status="Published").order_by('?')[:3]
    paginator = Paginator(posts, 1)
    page_range = paginator.page_range
    has_prev = False
    previous_post = None
    has_next = False
    next_post = None
    page_num = 0
    for i in page_range:
        page = paginator.page(i)
        if page.object_list[0].slug == post_slug:
            page_num = i
            if page.has_previous():
                has_prev = True
                previous_page_number = i - 1
                previous_post = paginator.page(previous_page_number).object_list[0]
            if page.has_next():
                has_next = True
                next_page_number = i + 1
                next_post = paginator.page(next_page_number).object_list[0]
        
    form = CommentForm(request.POST or None, initial={
        "content_type": ContentType.objects.get_for_model(post).id,
        "object_id": post.id
    })

    random_img_num = random.randint(0, 4)
    random_img_path = f"/static/images/post/img_{random_img_num}.JPG"

    context = {
        "main_title": "店主筆記",
        "sub_title_1": post.title,
        "bread_crumb_1": "首頁",
        "bread_crumb_2": "筆記",
        "bread_crumb_3": post.title,
        "bread_crumb_1_url": "/",
        "bread_crumb_2_url": "/blog/posts",
        "bread_crumb_3_url": f"/blog/post/{post.slug}",
        "post":post,
        "posts": posts,
        "form":form,
        "page_num": page_num,
        "has_prev": has_prev,
        "previous_post": previous_post,
        "has_next": has_next,
        "next_post": next_post,
        "random_img_path": random_img_path,
    }

    return render(request, 'blog/post.html', context)


def posts_by_tag(request, tag_slug):
    # Fetch the tag object or return 404
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    # Filter published posts that contain this specific tag
    posts = Post.objects.filter(
        status='Published',
        tags__in=[tag]
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
        created_at__year=year,
        created_at__month=month
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