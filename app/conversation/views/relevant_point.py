import logging

from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.models import AnswerModel, RelevantPointModel
from conversation.serializers import (
    RelevantPointChecklistDiscardSerializer,
    RelevantPointChecklistSerializer,
    RelevantPointSerializer,
)
from conversation.services import ChatGPTService


logger = logging.getLogger(LOGGER_NAME)


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


class RelevantPointChecklistView(GenericAPIView):
    """
    View for the endpoint that receives a context and returns the checklist
    to the relevant points of a patient.
    """

    serializer_class = RelevantPointChecklistSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        """Get the answers to the relevant points of a patient."""
        answers_groupd_by_category = ChatGPTService.ask_for_relevant_points_checklist(
            request.data.get("context"), patient_id
        )
        return Response(status=status.HTTP_200_OK, data=answers_groupd_by_category)


class RelevantPointChecklistDiscardView(GenericAPIView):
    """
    View for discarting the relevant points checked during the last ongoing conversation.
    """

    serializer_class = RelevantPointChecklistDiscardSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        """Discart the relevant points checked during the last ongoing conversation."""
        conversation_start_datetime = request.data.get("datetime")
        answers_to_discard = AnswerModel.objects.filter(
            patient_id=patient_id, resolved=True, updated_at__gt=conversation_start_datetime
        )
        for a in answers_to_discard:
            a.resolved = False
            a.save()
        return Response(status=status.HTTP_200_OK, data="Checklist discarded.")
