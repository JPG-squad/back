from rest_framework import serializers

from conversation.models import PatientModel

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientModel
        fields = ["id", "created_at", "updated_at", "name", "phone_number"]
