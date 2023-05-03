import logging

from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.models import AnswerModel, RelevantPointModel
from conversation.serializers import RelevantPointAnswerSerializer, RelevantPointSerializer
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


class RelevantPointAnswerView(GenericAPIView):
    """
    View for the endpoint that receives a context and returns the answers
    to the relevant points of a patient.
    """

    serializer_class = RelevantPointAnswerSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pre_context_prompt = """
        A continuacion te voy a pasar una transcripcion de una conversacion
        en tiempo real entre dos personas como contexto: \n\n
    """
    post_context_prompt = """
        \n\n Responde a la pregunta que te voy a hacer. Si no sabes o no se menciona la respuesta
        en el contexto, responde con "0". Si sí que lo sabes, respon solo con la información
        que se te pide. La pregunta es la siguiente: \n\n
    """

    def post(self, request, patient_id):
        """Get the answers to the relevant points of a patient."""
        rps = RelevantPointModel.objects.all()

        all_answers = []
        for rp in rps:
            question = rp.text
            current_anwer_object = AnswerModel.objects.filter(patient_id=patient_id, relevant_point_id=rp.id).first()
            if not current_anwer_object:
                answer = "0"
                new_answer_object = AnswerModel(patient_id=patient_id, relevant_point_id=rp.id, text=answer)
                new_answer_object.save()
            else:
                rt_context = request.data.get("context")
                if rt_context == "":
                    answer = current_anwer_object.text
                else:
                    context = self.pre_context_prompt + rt_context + self.post_context_prompt
                    answer = ChatGPTService.ask(context, question)
                    if answer != "0":
                        current_anwer_object.text = answer
                        current_anwer_object.save()
            all_answers.append({"question": question, "answer": answer})

        return Response(status=status.HTTP_200_OK, data=all_answers)
