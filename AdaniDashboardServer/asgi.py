"""
ASGI config for AdaniDashboardServer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from .auth_middleware import JwtAuthMiddlewareStack
from django.core.asgi import get_asgi_application
from dashboard.consumers import UnitDataConsumer
from django.urls import path


os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'AdaniDashboardServer.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': JwtAuthMiddlewareStack(
        URLRouter([
            path('unit_data/', UnitDataConsumer.as_asgi()),
        ])
    )
})
