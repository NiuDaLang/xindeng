from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.all_posts, name="all_posts"),
    path("posts/all_posts/<category>", views.all_posts_display, name="all_posts_display"),
    path("post/<slug:post_slug>", views.post, name="post"),
    path('tag/<str:tag_slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('post/archive/<int:year>/<int:month>/', views.post_archive_view, name='post_archive_view'),
]
