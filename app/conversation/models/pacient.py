from django.db import models
from .relevant_point import RelevantPointModel


class PacientModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    relevant_points = models.ManyToManyField(RelevantPointModel)

    class Meta:
        ordering = ("created_at",)
