from rest_framework import serializers

from conversation.models import PatientModel

class PatientSerializer(serializers.ModelSerializer):
    """Serializaer for the patient object."""

    class Meta:
        model = PatientModel
        fields = ["id", "email", "name", "phone_number", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
