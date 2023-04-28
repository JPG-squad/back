"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import ConversationView, ConversationUploadView

app_name = "conversation"

urlpatterns = [
    path("upload/", ConversationUploadView.as_view(), name="upload"),
    path("", ConversationView.as_view(), name="conversation"),
]
