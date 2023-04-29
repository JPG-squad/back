from django.db import models
from app.settings import AUTH_USER_MODEL
from .patient import PatientModel


class ConversationModel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, related_name="conversations", on_delete=models.CASCADE)
    patient = models.ForeignKey(PatientModel, related_name="patients", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wav_file_s3_path = models.CharField(max_length=255, null=False, blank=False)
    transcribed_file_s3_path = models.CharField(max_length=255, null=False, blank=False)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)

    class Meta:
        ordering = ("created_at",)
