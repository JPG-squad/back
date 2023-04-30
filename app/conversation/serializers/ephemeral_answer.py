from rest_framework import serializers

from conversation.models import EphemeralAnswerModel

class EphemeralAnswerSerializer(serializers.ModelSerializer):
    """Serializaer for the Ephemeral Answer object."""

    class Meta:
        model = EphemeralAnswerModel
        fields = ["id", "question", "answer", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "answer", "updated_at"]
