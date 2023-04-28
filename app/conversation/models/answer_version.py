from django.db import models


class AnswerVersionModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)
