from rest_framework import serializers


class SearchSerializer(serializers.Serializer):
    """Serializaer for the Search."""

    text = serializers.CharField()

    class Meta:
        fields = ["text"]
