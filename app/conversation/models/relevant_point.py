from enum import Enum

from django.db import models


class Category(Enum):
    PERSONAL = 'Personal'
    ECONOMICO = 'Económico'
    LABORAL = 'Laboral'
    FAMILIAR = 'Familiar'
    AMBIENTAL_VIVIENDA = 'Ambiental y de Vivienda'
    SALUD = 'de la Salud'
    SOCIAL = 'Social'


class RelevantPointModel(models.Model):
    text = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=[(category.name, category.value) for category in Category],
        default=Category.PERSONAL.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Relevant Points"

    def __str__(self) -> str:
        return self.text
