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
from conversation.services import ChatGPTService

bucket_name = environ.get("BUCKET_NAME")
logger = logging.getLogger(LOGGER_NAME)


def update_speaker_names(conversation_json, employee_speaker_id, employee_name, patient_name):
    for i, speaker in enumerate(conversation_json["speakers"]):
        if speaker == employee_speaker_id:
            conversation_json["speakers"][i] = employee_name
        else:
            conversation_json["speakers"][i] = patient_name
    for i, item in enumerate(conversation_json["conversation"]):
        if item["speaker"] == employee_speaker_id:
            conversation_json["conversation"][i]["speaker"] = employee_name
        else:
            conversation_json["conversation"][i]["speaker"] = patient_name
    return conversation_json


def parse_transcribe_conversation(transcription_result):
    parsed_conversation = {"conversation": [], "speakers": []}
    speaker_set = set()
    for speaker in transcription_result["results"]["speaker_labels"]["segments"]:
        speaker_set.add(speaker["speaker_label"])
    parsed_conversation["speakers"] = list(speaker_set)

    speaker = None
    text = ""
    for item in transcription_result["results"]["items"]:
        if speaker is not None:
            if speaker != item["speaker_label"]:
                parsed_conversation["conversation"].append({'speaker': speaker, 'text': text})
                text = ""
            text += item["alternatives"][0]["content"] + " "
        else:
            text = item["alternatives"][0]["content"] + " "
        speaker = item["speaker_label"]
    parsed_conversation["conversation"].append({'speaker': speaker, 'text': text})
    return parsed_conversation


def start_job(
    job_name,
    bucket_name,
    file_name,
    media_format,
    language_code,
    transcribe_client,
    vocabulary_name=None,
):
    """Start an asynchronous transcription job."""
    media_uri = f"s3://{bucket_name}/{file_name}"
    try:
        job_args = {
            "TranscriptionJobName": job_name,
            "Media": {"MediaFileUri": media_uri},
            "MediaFormat": media_format,
            "LanguageCode": language_code,
            "OutputBucketName": bucket_name,
            "OutputKey": file_name.replace(".wav", ".json"),
            "Settings": {"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
        }
        logger.info("Starting transcription job with arguments: %s", json.dumps(job_args))
        response = transcribe_client.start_transcription_job(**job_args)
        job = response["TranscriptionJob"]
        print(f"Started transcription job {job_name}.")
    except Exception:
        print(f"Couldn't start transcription job {job_name}")
        raise
    else:
        return job


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

        s3 = boto3.client("s3")
        transcribe = boto3.client("transcribe")

        serializer = ConversationUploadSerializer(data=request.data)
        patient = PatientModel.objects.get(id=patient_id)

        if serializer.is_valid() and patient is not None:
            file = request.FILES["conversation_file"]
            file_name = file.name
            logger.info("Uploading file %s to bucket %s", file_name, bucket_name)
            s3.upload_fileobj(file, bucket_name, file_name)
            job_name = "transcribe-job-" + file_name

            if execute_transcribe:
                # Start transcription job
                start_job(
                    job_name=job_name,
                    bucket_name=bucket_name,
                    file_name=file_name,
                    media_format="wav",
                    language_code="es-ES",
                    transcribe_client=transcribe,
                )

                job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
                    "TranscriptionJobStatus"
                ]
                logger.debug("Transcription job status: %s", job_status)
                # wait for the transcription job to complete
                while job_status == "IN_PROGRESS":
                    job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
                        "TranscriptionJobStatus"
                    ]
                    logger.debug("Transcription job status: %s", job_status)
                # if the job completed successfully, retrieve the transcription result and store it in S3
                if job_status == "COMPLETED":
                    response = s3.get_object(Bucket=bucket_name, Key=file_name.replace(".wav", ".json"))
                    transcription_json = json.loads(response["Body"].read().decode("utf-8"))
                    logger.debug("Transcription job response: %s", transcription_json)
                else:
                    logger.error("Transcription job failed with status: %s", job_status)
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            else:
                response = s3.get_object(Bucket=bucket_name, Key=file_name.replace(".wav", ".json"))
                transcription_json = json.loads(response["Body"].read().decode("utf-8"))

            conversation_json = parse_transcribe_conversation(transcription_json)
            question = '''Can you improve the conversation json as it can have some litte errors,
                        if so return me the json improved without aditional text.'''
            logger.info("Conversation json: %s", conversation_json)

            ChatGPTService.ask(json.dumps(conversation_json), question)
            logger.info("Conversation json improved: %s", conversation_json)

            question = '''Can you identify which speaker is the employee, it must had said somethink like:
            "Das tu consentimiento que esta conversacion va ser grabada?"
            Respond with the speaker identifier only'''
            employee_speaker_id = ChatGPTService.ask(json.dumps(conversation_json), question)
            logger.info("Employee speaker id: %s", employee_speaker_id)

            patient_name = patient.name
            employee_name = request.user.name
            conversation_json = update_speaker_names(
                conversation_json, employee_speaker_id, employee_name, patient_name
            )
            logger.info("Conversation json with speaker names: %s", conversation_json)

            # Pillar chat i automeoplenar els answers

            transcription_result = transcription_json["results"]["transcripts"][0]["transcript"]
            title_question = "Crea un titulo para esta conversacion de maximo 7 palabras."
            title = ChatGPTService.ask(transcription_result, title_question)
            description_question = "Crea un resumen de esta conversacion de maximo 30 palabras."
            description = ChatGPTService.ask(transcription_result, description_question)

            ConversationModel.objects.create(
                patient=patient,
                title=title,
                description=description,
                wav_file_s3_path=file_name,
                transcribed_file_s3_path=file_name.replace(".wav", ".json"),
                conversation=json.dumps(conversation_json),
            )

            # We update the user updated_at attribute so it goes to the top of the list when sorted in the frontend
            user = request.user
            user.updated_at = datetime.now()
            user.save()

            return Response(status=status.HTTP_200_OK, data={"title": title, "description": description})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
