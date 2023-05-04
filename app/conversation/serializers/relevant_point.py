from rest_framework import serializers

from conversation.models import RelevantPointModel


class RelevantPointSerializer(serializers.ModelSerializer):
    """Serializer for the Relevant Point object."""

    class Meta:
        model = RelevantPointModel
        fields = ["id", "text", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RelevantPointChecklistSerializer(serializers.Serializer):
    """
    Serializer for the endpoint that receives a context and returns the checklist
    to the relevant points of a patient.
    """

    context = serializers.CharField(required=True)
