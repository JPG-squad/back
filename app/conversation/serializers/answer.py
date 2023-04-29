from rest_framework import serializers

from conversation.models import AnswerModel

class AnswerSerializer(serializers.ModelSerializer):
    """Serializaer for the answer object."""

    class Meta:
        model = AnswerModel
        fields = ["id", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
