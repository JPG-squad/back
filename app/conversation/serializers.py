from rest_framework.serializers import Serializer, FileField


# Serializer for transcribing a file
class TranscribeConversationFileSerializer(Serializer):
    conversation_file = FileField()

    def validate(self, data):
        # Remove the file from the validated data,
        # as we will handle it separately in the view
        data.pop("conversation_file")
        return data
