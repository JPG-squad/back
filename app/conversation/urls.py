"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import ConversationDetailView, ConversationUploadView, ConversationView, CreatePatientView

app_name = "conversation"

urlpatterns = [
    # Patients
    path("patient/", CreatePatientView.as_view(), name="patient"),
    path("patient/<int:patient_id>/conversation/", ConversationView.as_view(), name="patient-conversations"),
    path(
        "patient/<int:patient_id>/conversation/<int:conversation_id>/",
        ConversationDetailView.as_view(),
        name="patient-conversation-detail",
    ),
    path(
        "patient/<int:patient_id>/conversation/upload/",
        ConversationUploadView.as_view(),
        name="patient-conversation-upload",
    ),
]
