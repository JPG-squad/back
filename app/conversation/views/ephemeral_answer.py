from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import ConversationModel, EphemeralAnswerModel
from conversation.serializers import EphemeralAnswerSerializer
from conversation.services import ChatGPTService


class EphemeralAnswerView(GenericAPIView):
    """Create and retrieve ephemeral answers for a conversation."""

    serializer_class = EphemeralAnswerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        """Get all the ephemeral answers for a conversation."""
        queryset = EphemeralAnswerModel.objects.filter(conversation_id=conversation_id)
        serializer = EphemeralAnswerSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request, conversation_id):
        """Create a new ephemeral answer for a conversation."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            conversation_transcript = ConversationModel.objects.get(id=conversation_id).conversation
            context = (
                """A continuación te voy a pasar una transcripción de una conversación,
                dónde las frases estan separadas en objectos json según quién las dijo:\n"""
                + conversation_transcript
            )
            question_text = "\n\nA partir de la conversación anterior, contesta a la siguiente pregunta: "
            question = question_text + serializer.validated_data["question"]
            answer = ChatGPTService.ask(context=context, question=question)
            serializer.save(conversation_id=conversation_id, answer=answer)
            return Response(status=status.HTTP_201_CREATED, data={"status": "Ephemeral answer created."})
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
