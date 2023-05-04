"""
URL mappings for the conversation API.
"""
from django.urls import path

from conversation.views import (
    AnswerView,
    ConversationDetailView,
    ConversationDownloadView,
    ConversationUploadDraftView,
    ConversationUploadView,
    ConversationView,
    EphemeralAnswerView,
    PatientDetailView,
    PatientView,
    RelevantPointAnswerView,
    RelevantPointDetailView,
    RelevantPointView,
)


app_name = "conversation"

urlpatterns = [
    path(
        "conversation/<int:conversation_id>/ephemeral-answer/",
        EphemeralAnswerView.as_view(),
        name="conversation-ephemeral-answer",
    ),
    path("patient/", PatientView.as_view(), name="patient"),
    path("patient/<int:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("patient/<int:patient_id>/conversation/", ConversationView.as_view(), name="patient-conversations"),
    path(
        "patient/<int:patient_id>/conversation/<int:conversation_id>/",
        ConversationDetailView.as_view(),
        name="patient-conversation-detail",
    ),
    path(
        "patient/<int:patient_id>/conversation/upload-draft/",
        ConversationUploadDraftView.as_view(),
        name="patient-conversation-upload-draft",
    ),
    path(
        "patient/<int:patient_id>/conversation/upload/",
        ConversationUploadView.as_view(),
        name="patient-conversation-upload",
    ),
    path(
        "patient/<int:patient_id>/conversation/<int:conversation_id>/download/",
        ConversationDownloadView.as_view(),
        name="patient-conversation-download",
    ),
    path(
        "patient/<int:patient_id>/conversation/<int:conversation_id>/answer/",
        AnswerView.as_view(),
        name="patient-conversation-answer",
    ),
    path(
        "patient/<int:patient_id>/relevant-point/answer/",
        RelevantPointAnswerView.as_view(),
        name="patient-relevant-point-answer",
    ),
    path("relevant-point/", RelevantPointView.as_view(), name="relevant-point"),
    path("relevant-point/<int:relevant_point_id>", RelevantPointDetailView.as_view(), name="relevant-point-detail"),
]
