"""
ASGI config for xindeng project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack # For user sessions
from channels.sessions import SessionMiddlewareStack # Required for guest session tracking


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xindeng.settings")

# 1. Initialize Django core application first
django_asgi_app = get_asgi_application()

# 2. Safely import app routing lists after Django setup is ready
import accounts.routing
import carts.routing

# 3. Combine bath pattern tables into a unified collection list
combined_websocket_routes = accounts.routing.websocket_urlpatterns + carts.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    # Handle WebSocket connections
    "websocket": SessionMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(
                combined_websocket_routes
            )
        )
    )
})