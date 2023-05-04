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
    # pre_context_prompt = """
    #     Eres un trabajador que tiene que rellenar un formulario con una serie de preguntas.
    #     Estas entrevistando a un usuario en una primera toma de contacto. Tu serás el que hace
    #     las preguntas en el contexto, y el usuario será el que las responda.
    #     Te voy a proporcionar el contexto y una pregunta o campo que debes rellenar.
    #     Solo debes responder con informacion del usuario.
    #     Si no sabes responder a esa pregunta/campo, contesta solamente con un '0'.
    #     Si sabes la respuesta a la pregunta o al campo que debes rellenar,
    #     no vuelvas a escribir la pregunta o el nombre del campo, simplemente contesta con el valor. \n
    #     Contexto:
    # """
    pre_context_prompt = """
        Te voy a mandar un trozo de una conversacion a un usuario que ha venido a buscar ayuda en la Cruz Roja.
        También te mandaré una pregunta o un campo el cual quiero que me digas si con el trozo de la conversación
        que te he mandado se ha contestado. Solo quiero que me contestes con '1' (si es que si) o '0' (Si es que no).
        La conversacion ha sido la siguiente.
    """

    def post(self, request, patient_id):
        """Get the answers to the relevant points of a patient."""
        rps = RelevantPointModel.objects.all()

        all_answers = []
        for rp in rps:
            question = rp.text
            current_anwer_object = AnswerModel.objects.filter(patient_id=patient_id, relevant_point_id=rp.id).first()
            if not current_anwer_object:
                current_anwer_object = AnswerModel(patient_id=patient_id, relevant_point_id=rp.id, resolved=False)
                current_anwer_object.save()
            rt_context = request.data.get("context")

            if (not current_anwer_object.resolved) and (rt_context != ""):
                context = self.pre_context_prompt + " " + rt_context + " \\Queremos saber si se ha hablado de: "
                question_to_chat = question + '. Contesta solo con 1 o 0'
                answer = ChatGPTService.ask(context, question_to_chat)
                if "1" in answer:
                    current_anwer_object.resolved = True
                    current_anwer_object.save()
            all_answers.append(
                {"question": question, "resolved": current_anwer_object.resolved, "category": rp.category}
            )
        answers_groupd_by_category = {}
        for answer in all_answers:
            category = answer["category"]
            if category not in answers_groupd_by_category:
                answers_groupd_by_category[category] = []
            answers_groupd_by_category[category].append(answer)

        return Response(status=status.HTTP_200_OK, data=answers_groupd_by_category)
