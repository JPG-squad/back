from rest_framework import serializers

from conversation.models import ConversationModel

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = [
            "id",
            "created_at",
            "updated_at",
            "wav_file_s3_path",
            "transcribed_file_s3_path",
            "title",
            "description",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = [
            "id",
            "created_at",
            "updated_at",
            "wav_file_s3_path",
            "transcribed_file_s3_path",
            "title",
            "description",
            "conversation",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConversationUploadSerializer(serializers.Serializer):
    conversation_file = serializers.FileField(write_only=True)

    def validate(self, data):
        data.pop("conversation_file")
        return data
