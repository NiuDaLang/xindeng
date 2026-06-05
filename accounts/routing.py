from django.urls import re_path
from . import members

websocket_urlpatterns = [
    # Using re_path is standard for WebSockets to handle trailing slashes better
    re_path(r'ws/solar/?$', members.Solar.as_asgi()),
    re_path(r'ws/chat_notifications/?$', members.ChatNotification.as_asgi()),
]