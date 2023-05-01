from django.urls import re_path

from .consumers.rt_transcribe import TranscribeConsumer

websocket_urlpatterns = [
    re_path(r"ws/conversation/(?P<conversation_id>\w+)/$", TranscribeConsumer.as_asgi()),
]
