from django.db import models

class RelevantPointModel(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Relevant Points"

    def __str__(self) -> str:
        return self.text
