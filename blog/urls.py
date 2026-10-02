# blog/urls.py

from django.urls import path, re_path
from . import views


urlpatterns = [
    path("posts/", views.all_posts, name="all_posts"),
    path("posts/all_posts/<category>", views.all_posts_display, name="all_posts_display"),

    # Unicode-aware slug pattern — matches ASCII AND CJK slugs like 用中文的標題
    re_path(
        r"^post/(?P<post_slug>[-\w]+)$",
        views.post,
        name="post",
    ),

    path('tag/<str:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('post/archive/<int:year>/<int:month>/', views.post_archive_view, name='post_archive_view'),

    path("admin/review/<int:post_id>/approve/", views.review_blog_post_approve, name="review_blog_post_approve"),
    path("admin/review/<int:post_id>/reject/", views.review_blog_post_reject, name="review_blog_post_reject"),
]