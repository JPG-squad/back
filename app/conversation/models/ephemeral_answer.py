from django.db import models

from .conversation import ConversationModel


class EphemeralAnswerModel(models.Model):
    question = models.TextField()
    answer = models.TextField()
    conversation = models.ForeignKey(
        ConversationModel, related_name="ephemeral_answers", on_delete=models.CASCADE, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("updated_at",)
        verbose_name_plural = "Ephemeral Answers"

    def __str__(self):
        return "Question: " + self.question + " - Answer: " + self.answer
