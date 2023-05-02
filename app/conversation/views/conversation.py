from datetime import datetime
import json
import logging
from os import environ

import boto3
from django.http import HttpResponse
from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.models import ConversationModel, PatientModel
from conversation.serializers import (
    ConversationDetailSerializer,
    ConversationDownloadSerializer,
    ConversationSerializer,
    ConversationUploadSerializer,
)
from conversation.services import ChatGPTService, WhisperService


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

        serializer = ConversationUploadSerializer(data=request.data)
        patient = PatientModel.objects.get(id=patient_id)

        if serializer.is_valid() and patient is not None:
            file = request.FILES["conversation_file"]

            now = datetime.now()
            now_str = now.strftime('%Y_%m_%d_%H_%M_%S_%f')

            file_name = f"{patient_id}_{request.user.id}_{now_str}_{file.name}"

            # if engine == aws use AWS service otherwise use the other service
            # transcribe_service = AWSTranscribeService(bucket_name, file)
            transcribe_service = WhisperService(bucket_name, file, file_name)
            logger.info("1")
            if execute_transcribe:
                error = transcribe_service.transcribe()
                logger.error(error)
                if error:
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                logger.info("2")
                transcription = transcribe_service.get_transcription()
                duration = transcribe_service.get_duration()
                logger.info("3")
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
                patient = PatientModel.objects.get(id=patient_id)
                patient.updated_at = datetime.now()
                patient.save()

                return Response(status=status.HTTP_200_OK, data={"title": title, "description": description})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConversationDownloadView(GenericAPIView):
    serializer_class = ConversationDownloadSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id, conversation_id):
        conversation = ConversationModel.objects.filter(
            id=conversation_id, patient_id=patient_id, patient_id__user_id=request.user.id
        )
        if conversation.exists():
            s3_file_path = conversation[0].wav_file_s3_path
            s3_response = boto3.client("s3").get_object(Bucket=bucket_name, Key=s3_file_path)
            content = s3_response['Body'].read()
            response = HttpResponse(status=status.HTTP_200_OK, content=content, content_type=s3_response['ContentType'])
            response['Content-Disposition'] = f'attachment; filename="{s3_file_path}"'
            return response
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
