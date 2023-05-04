import json

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
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConversationDetailSerializer(serializers.ModelSerializer):
    conversation = serializers.JSONField()

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
            "status",
            "draft",
            "conversation",
            "duration",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def to_representation(self, instance):
        """Convert `conversation` string field to JSON object"""
        representation = super().to_representation(instance)
        conversation = representation['conversation']
        representation['conversation'] = json.loads(conversation)["conversation"]
        return representation


class ConversationUploadDraftSerializer(serializers.ModelSerializer):
    draft = serializers.CharField(write_only=True)

    class Meta:
        model = ConversationModel
        fields = [
            "id",
            "created_at",
            "draft",
            "updated_at",
            "title",
            "description",
            "status",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "title",
            "description",
            "status",
        ]


class ConversationUploadSerializer(serializers.Serializer):
    conversation_file = serializers.FileField(write_only=True)

    def validate(self, data):
        data.pop("conversation_file")
        return data


class ConversatioDownloadSerializer(serializers.Serializer):
    conversation_file = serializers.FileField(write_only=True)

    def validate(self, data):
        data.pop("conversation_file")
        return data


class ConversationDownloadSerializer(serializers.Serializer):
    ...
