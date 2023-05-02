from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import RelevantPointModel
from conversation.serializers import RelevantPointSerializer


class RelevantPointView(GenericAPIView):
    """Get all the relevant points and create a new relevant point."""

    serializer_class = RelevantPointSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get all the relevant points."""
        queryset = RelevantPointModel.objects.all()
        serializer = RelevantPointSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def post(self, request):
        """Create a new relevant point."""
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class RelevantPointDetailView(GenericAPIView):
    """View for getting, updating, and deleting a specific relevant point."""

    serializer_class = RelevantPointSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, relevant_point_id):
        """Get a specific relevant point."""
        relevant_point = RelevantPointModel.objects.get(id=relevant_point_id)
        serializer = RelevantPointSerializer(relevant_point)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def delete(self, request, relevant_point_id):
        """Delete a relevant point."""
        relevant_point_to_delete = RelevantPointModel.objects.filter(id=relevant_point_id)
        if relevant_point_to_delete.exists():
            relevant_point_to_delete.delete()
            return Response(status=status.HTTP_200_OK, data={"message": "Relevant Point deleted."})
        return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, relevant_point_id):
        """Update a relevant point."""
        relevant_point_to_udpate = RelevantPointModel.objects.filter(id=relevant_point_id)
        if relevant_point_to_udpate.exists():
            relevant_point_to_udpate.update(**request.data)
            return Response(status=status.HTTP_200_OK, data={"message": "Relevant Point updated."})
        return Response(status=status.HTTP_404_NOT_FOUND)
