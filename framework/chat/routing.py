from django.urls import re_path
from . import consumers

## URL patterns for WebSocket routing.
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<thread_id>[\w-]+)/$", consumers.ChatConsumer.as_asgi()),
]
