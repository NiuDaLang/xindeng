from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/cart-sync/", consumers.CartSyncConsumer.as_asgi()),
]