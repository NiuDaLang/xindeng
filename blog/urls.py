from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.all_posts, name="all_posts"),
    path("post/", views.post, name="post"),
]
