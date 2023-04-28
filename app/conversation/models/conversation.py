from django.db import models
from app.settings import AUTH_USER_MODEL
from .pacient import PacientModel


class ConversationModel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, related_name="conversations", on_delete=models.CASCADE)
    pacient = models.ForeignKey(PacientModel, related_name="pacients", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wav_file_s3_path = models.CharField(max_length=255, null=True, blank=True)
    transcribed_file_s3_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
