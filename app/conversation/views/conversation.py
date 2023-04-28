from rest_framework.generics import GenericAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status, authentication, permissions

from conversation.models import ConversationModel
from conversation.serializers import ConversationSerializer


class ConversationView(GenericAPIView):

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = ConversationModel.objects.all()
        serializer = ConversationSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
