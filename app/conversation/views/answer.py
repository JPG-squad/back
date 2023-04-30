from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from conversation.models import AnswerModel, PatientModel, RelevantPointModel
from conversation.serializers import AnswerSerializer

class AnswerView(GenericAPIView):
    """Get all the answers for a patient and the relevant points of these answers."""

    serializer_class = AnswerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # def get(self, request, patient_id, conversation_id):
    #     """Get all the answers a patient has given and the relevant points of these answers."""
    #     queryset = AnswerModel.objects.filter(patient_id=patient_id, conversation_id=conversation_id)
    #     if queryset.exists():
    #         serializer = AnswerSerializer(queryset, many=True)
    #         items = []
    #         for answer in serializer.data:
    #             print(answer)
    #             item = {}
    #             item["question"] = AnswerModel.objects.get(id=answer["id"]).relevant_point.text
    #             item["answer"] = answer["text"]
    #             items.append(item)
    #         return Response(status=status.HTTP_200_OK, data=items)
    #     return Response(status=status.HTTP_200_OK, data=[])
