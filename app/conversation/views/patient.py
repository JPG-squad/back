from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import PatientModel
from conversation.serializers import PatientSerializer


class PatientView(GenericAPIView):
    serializer_class = PatientSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = PatientModel.objects.all()
        serializer = PatientSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
