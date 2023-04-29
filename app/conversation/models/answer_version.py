from django.db import models
from .relevant_point import RelevantPointModel


class AnswerVersionModel(models.Model):
    text = models.TextField()
    relevant_point = models.ForeignKey(
        RelevantPointModel, related_name="relevant_point", on_delete=models.CASCADE, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Answer Versions"

    def __str__(self):
        return self.text
