from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ai_stream/$', consumers.AIStreamConsumer.as_asgi()),
]
