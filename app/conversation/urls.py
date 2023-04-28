"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation import views

app_name = "conversation"

urlpatterns = [
    path("transcribe/", views.TranscribeConversationFileView.as_view(), name="transcribe"),
]
