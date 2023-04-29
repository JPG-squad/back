from rest_framework import serializers

from conversation.models import ConversationModel


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = ["id", "user", "patient", "created_at", "updated_at", "wav_file_s3_path", "transcribed_file_s3_path"]


class ConversationUploadSerializer(serializers.Serializer):
    conversation_file = serializers.FileField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    patient_id = serializers.IntegerField(write_only=True)

    def validate(self, data):
        # Remove the file from the validated data,
        # as we will handle it separately in the view
        data.pop("conversation_file")
        return data
