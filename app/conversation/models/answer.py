from django.db import models

from .patient import PatientModel
from .relevant_point import RelevantPointModel


class AnswerModel(models.Model):
    text = models.TextField(null=False, default="")
    patient = models.ForeignKey(PatientModel, related_name="answers", on_delete=models.CASCADE, null=False)
    relevant_point = models.ForeignKey(RelevantPointModel, related_name="answers", on_delete=models.CASCADE, null=False)
    resolved = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Answers"
        unique_together = (
            'patient',
            'relevant_point',
        )

    def __str__(self):
        return self.text
