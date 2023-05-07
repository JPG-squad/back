import datetime

from django.db import models

from .patient import PatientModel
from .relevant_point import RelevantPointModel


class AnswerModel(models.Model):
    text = models.TextField(null=False, default="")
    patient = models.ForeignKey(PatientModel, related_name="answers", on_delete=models.CASCADE, null=False)
    relevant_point = models.ForeignKey(RelevantPointModel, related_name="answers", on_delete=models.CASCADE, null=False)
    resolved = models.BooleanField(null=False, default=False)
    created_at = models.DateTimeField(editable=False, null=False, blank=False, default=datetime.datetime.now())
    updated_at = models.DateTimeField(null=False, blank=False, default=datetime.datetime.now())

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        return super(AnswerModel, self).save(*args, **kwargs)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Answers"
        unique_together = (
            'patient',
            'relevant_point',
        )

    def __str__(self):
        return f"Relevant Point: {self.relevant_point.text} - Patient: {self.patient.name} - Answer: {self.text}"
