from enum import Enum

from django.db import models

from .patient import PatientModel


class Status(Enum):
    DRAFT = 'draft'
    CONSOLIDATED = 'consolidated'


class ConversationModel(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    patient = models.ForeignKey(PatientModel, related_name="conversations", on_delete=models.CASCADE)
    wav_file_s3_path = models.CharField(max_length=255, null=False, blank=False)
    transcribed_file_s3_path = models.CharField(max_length=255, null=False, blank=False)
    status = models.CharField(
        max_length=20, choices=[(status.name, status.value) for status in Status], default=Status.DRAFT.value
    )
    draft = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    conversation = models.JSONField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Conversations"

    def __str__(self):
        return self.title
