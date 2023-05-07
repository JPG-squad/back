import logging

from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.models import AnswerModel, ConversationModel, PatientModel
from conversation.serializers import PatientSerializer, PatientSheetSerializer


logger = logging.getLogger(LOGGER_NAME)


class PatientView(GenericAPIView):
    """Get all patients of the authenticated user and create a new patient for the user."""

    serializer_class = PatientSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get all patients of the authenticated user."""
        queryset = PatientModel.objects.filter(user_id=request.user.id)
        serializer = PatientSerializer(queryset, many=True)
        for patient in serializer.data:
            n_conversations = ConversationModel.objects.filter(patient_id=patient["id"]).count()
            patient["n_conversations"] = n_conversations
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
        return Response(status=status.HTTP_200_OK, data=serializer.data[0])

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


class PatientSheetView(GenericAPIView):
    """
    View that returns all the answers of the relevant points of a patient.
    """

    serializer_class = PatientSheetSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        """Get a specific patient of the authenticated user."""
        answers = AnswerModel.objects.filter(patient_id=patient_id)
        all_answers = []
        for answer in answers:
            if not answer.resolved:
                answer_to_return = ""
            else:
                answer_to_return = answer.text
            a = {
                "id": answer.id,
                "question": answer.relevant_point.text,
                "answer": answer_to_return,
                "category": answer.relevant_point.category,
            }
            all_answers.append(a)
        answers_groupd_by_category = {}
        for answer in all_answers:
            category = answer["category"]
            if category not in answers_groupd_by_category:
                answers_groupd_by_category[category] = []
            answers_groupd_by_category[category].append(answer)
        return Response(status=status.HTTP_200_OK, data=answers_groupd_by_category)

    def post(self, request, patient_id):
        """Bulk update the sheet of a patient."""
        answers = request.data.get("answers")
        for answer in answers:
            answer_to_update = AnswerModel.objects.get(id=answer["id"])
            answer_to_update.text = answer["answer"]
            answer_to_update.resolved = True
            answer_to_update.save()
        return Response(status=status.HTTP_200_OK, data={"message": "Sheet updated."})
