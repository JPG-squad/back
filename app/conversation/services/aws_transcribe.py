import json
import logging
import re

import boto3

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME, TRANSCRIPTION_BUCKET_NAME, TRANSCRIPTION_REGION


logger = logging.getLogger(LOGGER_NAME)


class AWSTranscribeService:
    def __init__(self, file, file_name, employee_name, patient_name):
        self.transcribe_client = boto3.client("transcribe", region_name=TRANSCRIPTION_REGION)
        self.s3 = boto3.client("s3", region_name=TRANSCRIPTION_REGION)
        self.bucket_name = TRANSCRIPTION_BUCKET_NAME
        self.file_name = file_name
        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)
        self.employee_name = employee_name
        self.patient_name = patient_name
        self.file_extension = self.file_name.split(".")[-1]

    def get_duration(self):
        response = self.s3.get_object(
            Bucket=self.bucket_name, Key=self.file_name.replace(f".{self.file_extension}", ".json")
        )
        transcription_json = json.loads(response["Body"].read().decode("utf-8"))
        return transcription_json["results"]["speaker_labels"]["segments"][-1]["end_time"]

    def transcribe(self):
        job_name = "transcribe-job-" + self.file_name
        self._start_job(
            job_name=job_name,
            media_format=self.file_extension,
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
            logger.error("Transcription job failed with status: %s", job_status)
        # self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
        response = self.s3.get_object(
            Bucket=self.bucket_name, Key=self.file_name.replace(f".{self.file_extension}", ".json")
        )
        transcription_json = json.loads(response["Body"].read().decode("utf-8"))
        parsed_conversation_json = self._parse_transcribe_conversation(transcription_json)
        improved_transcript = self._improve_transcription(parsed_conversation_json)
        transcription_with_speakers = self.update_speaker_names(improved_transcript)
        return transcription_with_speakers

    def _improve_transcription(self, transcription):
        question = '''\n\nEn la conversacion en formato json que te acabo de pasar puede ser que haya algunos errores de
        quién ha hablado (en cada objecto json habla una persona distinta de las 2, intercaladamente). Tu objectivo es
        arreglarlo para que conversacion tenga sentido. Esto puede significar que tengas que cambiar dónde se ha dicho
        algo porque realmente lo ha dicho otra persona. No invetes nada del texto, solo arregla quién ha dicho qué.
        Devuelveme un JSON valido en formato UTF8:\n'''
        conversation_json = json.loads(ChatGPTService.ask(str(transcription), question).replace("'", '"'))
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
                "OutputKey": self.file_name.replace(f".{self.file_extension}", ".json"),
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
        parsed_conversation = {"conversation": []}
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

    def update_speaker_names(self, transcription):
        for i, item in enumerate(transcription["conversation"]):
            if item["speaker"] == "spk_0":
                transcription["conversation"][i]["speaker"] = self.employee_name
            else:
                transcription["conversation"][i]["speaker"] = self.patient_name
        return transcription
