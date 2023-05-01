from django.db import models

from app.settings import AUTH_USER_MODEL

class PatientModel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, related_name="patients", on_delete=models.CASCADE, null=False)
    email = models.EmailField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Patients"

    def __str__(self) -> str:
        return self.name
