from datetime import datetime
import json
import logging
from os import environ

import boto3
from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.models import ConversationModel, PatientModel
from conversation.serializers import ConversationDetailSerializer, ConversationSerializer, ConversationUploadSerializer
from conversation.services import AWSTranscribeService, ChatGPTService, EnchancedWhisperService

bucket_name = environ.get("BUCKET_NAME")
logger = logging.getLogger(LOGGER_NAME)


class ConversationView(GenericAPIView):
    serializer_class = ConversationSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        conversations = ConversationModel.objects.filter(patient_id=patient_id, patient_id__user_id=request.user.id)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ConversationDetailView(GenericAPIView):
    serializer_class = ConversationDetailSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id, conversation_id):
        conversation = ConversationModel.objects.filter(
            id=conversation_id, patient_id=patient_id, patient_id__user_id=request.user.id
        )
        if conversation.exists():
            serializer = ConversationDetailSerializer(conversation[0])
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ConversationUploadView(GenericAPIView):
    """View for transcribing a conversation file (a wav file)"""

    serializer_class = ConversationUploadSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        execute_transcribe = True

        boto3.client("s3")

        serializer = ConversationUploadSerializer(data=request.data)
        patient = PatientModel.objects.get(id=patient_id)

        if serializer.is_valid() and patient is not None:
            file = request.FILES["conversation_file"]
            file_name = file.name

            # if engine == aws use AWS service otherwise use the other service
            # transcribe_service = AWSTranscribeService(bucket_name, file)
            transcribe_service = EnchancedWhisperService(bucket_name, file, patient_id, request.user.id)

            if execute_transcribe:
                error = transcribe_service.transcribe()
                return Response(status=status.HTTP_200_OK, data={})
                if error:
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                transcription = transcribe_service.get_transcription()
                duration = transcribe_service.get_duration()

                patient_name = patient.name
                employee_name = request.user.name
                transcription = transcribe_service.update_speaker_names(transcription, employee_name, patient_name)
                logger.info("Transcription with speaker names: %s", transcription)

                # Pillar chat i automeoplenar els answers

                title_question = "Crea un titulo para esta conversacion de maximo 7 palabras."
                title = ChatGPTService.ask(str(transcription), title_question)
                description_question = "Crea un resumen de esta conversacion de maximo 30 palabras."
                description = ChatGPTService.ask(str(transcription), description_question)

                ConversationModel.objects.create(
                    patient=patient,
                    title=title,
                    description=description,
                    wav_file_s3_path=file_name,
                    transcribed_file_s3_path=file_name.replace(".wav", ".json"),
                    conversation=json.dumps(transcription),
                    duration=duration,
                )

                # We update the user updated_at attribute so it goes to the top of the list when sorted in the frontend
                user = request.user
                user.updated_at = datetime.now()
                user.save()

                return Response(status=status.HTTP_200_OK, data={"title": title, "description": description})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
