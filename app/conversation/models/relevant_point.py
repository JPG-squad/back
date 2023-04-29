from django.db import models
from .answer_version import AnswerVersionModel


class RelevantPointModel(models.Model):
    text = models.TextField()
    answer_versions = models.ForeignKey(AnswerVersionModel, related_name="answer_versions", on_delete=models.CASCADE)
