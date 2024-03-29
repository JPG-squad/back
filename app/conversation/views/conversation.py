from datetime import datetime
import json
import logging
from math import e
from os import environ

import boto3
from django.http import HttpResponse
from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME, TRANSCRIPTION_BUCKET_NAME, TRANSCRIPTION_REGION
from conversation.models import ConversationModel, PatientModel, Status
from conversation.serializers import (
    ConversationDetailSerializer,
    ConversationDownloadSerializer,
    ConversationSerializer,
    ConversationUploadDraftSerializer,
    ConversationUploadSerializer,
)
from conversation.services import AWSTranscribeService, ChatGPTService, DeepgramService
from conversation.services.opensearch import open_search_service


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


class ConversationUploadDraftView(GenericAPIView):
    serializer_class = ConversationUploadDraftSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        draft = request.data.get("draft")
        draft_question = "Q: Mejorame la sintaxis i formato de este texto, que quede bien escrito. A:"
        draft_improved = ChatGPTService.ask(str(draft), draft_question)
        title_question = "Q: Crea un titulo para esta conversacion de maximo 7 palabras. A:"
        title = ChatGPTService.ask(str(draft_improved), title_question)
        description_question = "Q: Crea un resumen de esta conversacion de maximo 30 palabras. A:"
        description = ChatGPTService.ask(str(draft_improved), description_question)
        new_conversation = ConversationModel(
            patient_id=patient_id, draft=draft_improved, title=title, description=description, status=Status.DRAFT.value
        )
        new_conversation.save()
        ChatGPTService.ask_for_relevant_points_answers(draft_improved, patient_id)
        serializer = ConversationUploadDraftSerializer(new_conversation)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ConversationUploadView(GenericAPIView):
    """View for transcribing a conversation file (a wav file)"""

    serializer_class = ConversationUploadSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, patient_id):
        execute_transcribe = True
        transcribe_engine = request.GET.get('engine', 'aws_transcribe')

        serializer = ConversationUploadSerializer(data=request.data)
        patient = PatientModel.objects.get(id=patient_id)

        if serializer.is_valid() and patient is not None:
            file = request.FILES["conversation_file"]

            now = datetime.now()
            now_str = now.strftime('%Y_%m_%d_%H_%M_%S_%f')

            file_name = f"{patient_id}_{request.user.id}_{now_str}_{file.name}"
            file_extension = file_name.split(".")[-1]
            patient_name = patient.name
            employee_name = request.user.name

            if transcribe_engine == "aws_transcribe":
                transcribe_service = AWSTranscribeService(file, file_name, employee_name, patient_name)
            elif transcribe_engine == "deepgram":
                transcribe_service = DeepgramService(file, file_name, employee_name, patient_name)

            if execute_transcribe:
                transcription = transcribe_service.transcribe()

                duration = transcribe_service.get_duration()

                title_question = "Q: Crea un titulo para esta conversacion de maximo 7 palabras. A:"
                title = ChatGPTService.ask(str(transcription), title_question)
                description_question = "Q: Crea un resumen de esta conversacion de maximo 30 palabras. A:"
                description = ChatGPTService.ask(str(transcription), description_question)

                conversation = ConversationModel.objects.create(
                    patient=patient,
                    title=title,
                    description=description,
                    wav_file_s3_path=file_name,
                    transcribed_file_s3_path=file_name.replace(f".{file_extension}", ".json"),
                    conversation=json.dumps(transcription),
                    duration=duration,
                )
                logger.info("conversastion:", conversation)
                open_search_service.index_conversation(conversation)
                ChatGPTService.ask_for_relevant_points_checklist(str(transcription), patient_id)
                ChatGPTService.ask_for_relevant_points_answers(str(transcription), patient_id)

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
            s3_response = boto3.client("s3", region_name=TRANSCRIPTION_REGION).get_object(
                Bucket=TRANSCRIPTION_BUCKET_NAME, Key=s3_file_path
            )
            content = s3_response['Body'].read()
            response = HttpResponse(status=status.HTTP_200_OK, content=content, content_type=s3_response['ContentType'])
            response['Content-Disposition'] = f'attachment; filename="{s3_file_path}"'
            return response
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
