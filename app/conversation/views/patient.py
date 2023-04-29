from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import PatientModel
from conversation.serializers import PatientSerializer

class CreatePatientView(GenericAPIView):
    """Create a new patient in the system"""

    serializer_class = PatientSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Create a new patient."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    def get(self, request):
        """Get all patients of the authenticated user."""
        queryset = PatientModel.objects.filter(user_id=request.user.id)
        serializer = PatientSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
