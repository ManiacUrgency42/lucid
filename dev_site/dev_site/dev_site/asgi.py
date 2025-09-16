"""
ASGI config for test_site project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from video_chat import consumers

from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dev_site.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    
    "websocket": AllowedHostsOriginValidator( #Ensures the Host header (and the WebSocket Origin) matches one of your ALLOWED_HOSTS.
        AuthMiddlewareStack( #Injects Django’s session and authentication into the connection scope.
            URLRouter([
                path("ws/signaling/<room_name>/", consumers.SignalingConsumer.as_asgi())
            ])
        )
    )
}) 
