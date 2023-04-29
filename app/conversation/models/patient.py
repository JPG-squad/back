from django.db import models


class PatientModel(models.Model):
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Patients"

    def __str__(self) -> str:
        return self.name
