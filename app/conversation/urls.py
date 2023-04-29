"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import ConversationDetailView, ConversationUploadView, ConversationView, PatientView

app_name = "conversation"

urlpatterns = [
    # Conversations
    path("conversation/", ConversationView.as_view(), name="conversation"),
    path("conversation/<int:id>/", ConversationDetailView.as_view(), name="conversation"),
    path("conversation/upload/", ConversationUploadView.as_view(), name="upload"),
    # Patients
    path("patient/", PatientView.as_view(), name="patient"),
]
