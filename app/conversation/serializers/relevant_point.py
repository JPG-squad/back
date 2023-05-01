from rest_framework import serializers

from conversation.models import RelevantPointModel


class RelevantPointSerializer(serializers.ModelSerializer):
    """Serializer for the Relevant Point object."""

    class Meta:
        model = RelevantPointModel
        fields = ["id", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
