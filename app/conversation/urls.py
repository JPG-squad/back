"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import TranscribeConversationFileView
from conversation.views import ConversationView

app_name = "conversation"

urlpatterns = [
    path("upload/", TranscribeConversationFileView.as_view(), name="upload"),
    path("", ConversationView.as_view(), name="conversation"),
]
