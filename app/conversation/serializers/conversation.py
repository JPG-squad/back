from rest_framework import serializers

from conversation.models import ConversationModel


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = ["user", "pacient"]
