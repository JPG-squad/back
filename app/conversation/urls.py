"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import (
    ConversationDetailView,
    ConversationUploadView,
    ConversationView,
    PatientDetailView,
    PatientView,
)

app_name = "conversation"

urlpatterns = [
    # Patients
    path("patient/", PatientView.as_view(), name="patient"),
    path("patient/<int:patient_id>", PatientDetailView.as_view(), name="patient-detail"),
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
