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
    PatientSheetView,
    PatientView,
    RelevantPointChecklistDiscardView,
    RelevantPointChecklistView,
    RelevantPointDetailView,
    RelevantPointView,
    SearchView,
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
    path("patient/<int:patient_id>/sheet/", PatientSheetView.as_view(), name="patient-sheet"),
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
        "patient/<int:patient_id>/relevant-point/checklist/",
        RelevantPointChecklistView.as_view(),
        name="patient-relevant-point-checklist",
    ),
    path(
        "patient/<int:patient_id>/relevant-point/checklist/discard/",
        RelevantPointChecklistDiscardView.as_view(),
        name="patient-relevant-point-checklist-discard",
    ),
    path("relevant-point/", RelevantPointView.as_view(), name="relevant-point"),
    path("relevant-point/<int:relevant_point_id>", RelevantPointDetailView.as_view(), name="relevant-point-detail"),
    path("search/", SearchView.as_view(), name="search"),
]
