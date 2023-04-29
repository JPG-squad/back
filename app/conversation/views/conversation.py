import json
from os import environ

import boto3
import openai
from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import AUTH_USER_MODEL
from conversation.models import ConversationModel, PatientModel
from conversation.serializers import ConversationDetailSerializer, ConversationSerializer, ConversationUploadSerializer

bucket_name = environ.get("BUCKET_NAME")


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


def ask_question(context, question):
    prompt = f"Q: {question}\nA:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=context + prompt,
        temperature=0.5,
        max_tokens=1000,
        n=1,
        stop=None,
        timeout=10,
        frequency_penalty=0,
        presence_penalty=0,
    )

    answer = response.choices[0].text.strip()
    return answer


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
            serializer = ConversationDetailSerializer(conversation)
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

                # wait for the transcription job to complete
                while job_status == "IN_PROGRESS":
                    job_status = transcribe.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
                        "TranscriptionJobStatus"
                    ]
                # if the job completed successfully, retrieve the transcription result and store it in S3
                if job_status == "COMPLETED":
                    response = s3.get_object(Bucket=bucket_name, Key=file_name.replace(".wav", ".json"))
                    transcription_json = json.loads(response["Body"].read().decode("utf-8"))
                else:
                    print(f"Transcription job failed with status: {job_status}")
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
            else:
                response = s3.get_object(Bucket=bucket_name, Key=file_name.replace(".wav", ".json"))
                transcription_json = json.loads(response["Body"].read().decode("utf-8"))

            conversation_json = parse_transcribe_conversation(transcription_json)
            question = '''Can you improve the conversation json as it can have some litte errors,
                        if so return me the json improved without aditional text.'''
            ask_question(json.dumps(conversation_json), question)

            question = '''Can you identify which speaker is the employee, it must had said somethink like:
            "Das tu consentimiento que esta conversacion va ser grabada?"
            Respond with the speaker identifier only'''
            employee_speaker_id = ask_question(json.dumps(conversation_json), question)

            patient_name = patient.name
            employee_name = request.user.name
            conversation_json = update_speaker_names(
                conversation_json, employee_speaker_id, employee_name, patient_name
            )

            # Pillar chat i automeoplenar els answers

            transcription_result = transcription_json["results"]["transcripts"][0]["transcript"]
            title_question = "Create a title for this conversation of maximum 7 words."
            title = ask_question(transcription_result, title_question)
            description_question = "Create a one paragraph summary of this conversation of maximum 30 words."
            description = ask_question(transcription_result, description_question)

            ConversationModel.objects.create(
                patient=patient,
                title=title,
                description=description,
                wav_file_s3_path=file_name,
                transcribed_file_s3_path=file_name.replace(".wav", ".json"),
                conversation=json.dumps(conversation_json),
            )
            return Response(status=status.HTTP_200_OK, data={"title": title, "description": description})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
