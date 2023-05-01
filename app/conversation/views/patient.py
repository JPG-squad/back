from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import PatientModel
from conversation.serializers import PatientSerializer


class PatientView(GenericAPIView):
    """Get all patients of the authenticated user and create a new patient for the user."""

    serializer_class = PatientSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get all patients of the authenticated user."""
        queryset = PatientModel.objects.filter(user_id=request.user.id)
        serializer = PatientSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request):
        """Create a new patient."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class PatientDetailView(GenericAPIView):
    """View for getting, updating, and deleting a specific patient of the authenticated user."""

    serializer_class = PatientSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        """Get a specific patient of the authenticated user."""
        queryset = PatientModel.objects.filter(user_id=request.user.id, id=patient_id)
        serializer = PatientSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, patient_id):
        """Delete a patient of the authenticated user."""
        patient_to_delete = PatientModel.objects.filter(user_id=request.user.id, id=patient_id)
        if patient_to_delete.exists():
            patient_to_delete.delete()
            return Response(status=status.HTTP_200_OK, data={"message": "Patient deleted."})
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, patient_id):
        """Update a patient of the authenticated user."""
        patient_to_update = PatientModel.objects.filter(user_id=request.user.id, id=patient_id)
        if patient_to_update.exists():
            patient_to_update.update(**request.data)
            return Response(status=status.HTTP_200_OK, data={"message": "Patient updated."})
        return Response(status=status.HTTP_404_NOT_FOUND)
