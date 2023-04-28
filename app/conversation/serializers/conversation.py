from rest_framework import serializers
from rest_framework.fields import FileField

from conversation.models import ConversationModel


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = ["user", "patient"]


class ConversationUploadSerializer(serializers.ModelSerializer):

    # conversation_file = FileField()

    def validate(self, data):
        # Remove the file from the validated data,
        # as we will handle it separately in the view
        data.pop("conversation_file")
        return data

    class Meta:
        model = ConversationModel
        fields = ["user", "patient", "conversation_file"]
