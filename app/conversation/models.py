from django.db import models
from app.settings import AUTH_USER_MODEL


# Create your models here.
class Conversation(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, related_name="conversations", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    wav_file_s3_path = models.CharField(max_length=255, null=True, blank=True)
    transcribed_file_s3_path = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ("created_at",)
