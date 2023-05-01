import json
import logging

import boto3

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class AWSTranscribeService:
    def __init__(self, bucket_name, file):
        self.transcribe_client = boto3.client("transcribe")
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name
        self.file_name = file.name
        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)

    def get_transcription(self):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name.replace(".wav", ".json"))
        transcription_json = json.loads(response["Body"].read().decode("utf-8"))
        parsed_conversation_json = self._parse_transcribe_conversation(transcription_json)
        return self._improve_transcription(parsed_conversation_json)

    def get_duration(self):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name.replace(".wav", ".json"))
        transcription_json = json.loads(response["Body"].read().decode("utf-8"))
        return transcription_json["results"]["speaker_labels"]["segments"][-1]["end_time"]

    def transcribe(self):
        job_name = "transcribe-job-" + self.file_name
        error = False
        self._start_job(
            job_name=job_name,
            media_format="wav",
            language_code="es-ES",
        )
        job_status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)["TranscriptionJob"][
            "TranscriptionJobStatus"
        ]
        logger.debug("Transcription job status: %s", job_status)
        # wait for the transcription job to complete
        while job_status == "IN_PROGRESS":
            job_status = self.transcribe_client.get_transcription_job(TranscriptionJobName=job_name)[
                "TranscriptionJob"
            ]["TranscriptionJobStatus"]
            logger.debug("Transcription job status: %s", job_status)
        if job_status == "COMPLETED":
            logger.debug("Transcription job has ended")
        else:
            error = True
            logger.error("Transcription job failed with status: %s", job_status)
        self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        return error

    def _improve_transcription(self, transcription):
        question = '''Aqui tienes una respuesta en JSON de AWS transcribe, corrige el JSON y mejora la
            respuesta. Quiero que arregles las frases sin sentido, las preguntas que hace un speaker y
            la respuesta que da otro aveces salen en el mismo elemento.Tu objetivo principal es arreglar
            el output de AWS transcribe.Devuelveme un JSON valido en formato UTF8:\n'''
        conversation_json = json.loads(ChatGPTService.ask(str(transcription), question).replace("'", '"'))
        logger.info("Conversation json improved: %s", conversation_json)

        question = '''En la siguiente conversacion hay errores donde uno pregunta y la respuesta del otro
        esta en el mismo elemento del json y deberia estar en el siguiente elemento como respuesta, arreglalo.
        Devuelveme un JSON valido en formato UTF8:\n'''
        logger.info("Conversation json: %s", conversation_json)
        conversation_json = json.loads(ChatGPTService.ask(str(conversation_json), question).replace("'", '"'))
        logger.info("Conversation json improved: %s", conversation_json)

        return conversation_json

    def _start_job(self, job_name, media_format, language_code):
        media_uri = f"s3://{self.bucket_name}/{self.file_name}"
        try:
            job_args = {
                "TranscriptionJobName": job_name,
                "Media": {"MediaFileUri": media_uri},
                "MediaFormat": media_format,
                "LanguageCode": language_code,
                "OutputBucketName": self.bucket_name,
                "OutputKey": self.file_name.replace(".wav", ".json"),
                "Settings": {"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
            }
            logger.info("Starting transcription job with arguments: %s", json.dumps(job_args))
            response = self.transcribe_client.start_transcription_job(**job_args)
            job = response["TranscriptionJob"]
            print(f"Started transcription job {job_name}.")
        except Exception:
            print(f"Couldn't start transcription job {job_name}")
            raise
        else:
            return job

    def _parse_transcribe_conversation(self, transcription):
        parsed_conversation = {"conversation": [], "speakers": []}
        speaker_set = set()
        for speaker in transcription["results"]["speaker_labels"]["segments"]:
            speaker_set.add(speaker["speaker_label"])
        parsed_conversation["speakers"] = list(speaker_set)

        speaker = None
        text = ""
        for item in transcription["results"]["items"]:
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

    def update_speaker_names(self, transcription, employee_name, patient_name):
        question = '''Can you identify which speaker is the employee, it must had said somethink like:
        "Das tu consentimiento que esta conversacion va ser grabada?"
        Respond with the speaker identifier only'''
        employee_speaker_id = ChatGPTService.ask(json.dumps(transcription), question)
        logger.info("Employee speaker id: %s", employee_speaker_id)

        for i, speaker in enumerate(transcription["speakers"]):
            if speaker == employee_speaker_id:
                transcription["speakers"][i] = employee_name
            else:
                transcription["speakers"][i] = patient_name
        for i, item in enumerate(transcription["conversation"]):
            if item["speaker"] == employee_speaker_id:
                transcription["conversation"][i]["speaker"] = employee_name
            else:
                transcription["conversation"][i]["speaker"] = patient_name
        return transcription
