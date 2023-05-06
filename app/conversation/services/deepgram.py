import io
import json
import logging

from aiohttp import FormData
import boto3
from deepgram import Deepgram

from .chatgpt import ChatGPTService
from app.settings import DEEPGRAM_API_KEY, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class DeepgramService:
    def __init__(self, bucket_name, file, file_name):
        self.dg_client = Deepgram(DEEPGRAM_API_KEY)
        self.file = file
        self.s3 = boto3.client("s3")
        self.options = {
            'punctuate': True,
            'diarize': True,
            'language': 'es',
            #'paragraphs': True,
            #'smart_format': True,
            'model': 'general-enhanced',
            'tier': 'enhanced',
        }
        self.bucket_name = bucket_name
        self.file_name = file_name
        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)
        logger.info("File uploaded successfully")

    def get_raw_transcription(self):
        self.s3.download_file(self.bucket_name, self.file_name, "recordings/" + self.file_name)
        with open("recordings/" + self.file_name, "rb") as f:
            source = {"buffer": f, "mimetype": 'audio/wav'}
            logger.info("Sending file to transcribe to Deepgram...")
            response = self.dg_client.transcription.sync_prerecorded(source, self.options)
            logger.info(response)
            logger.info("Transcription received successfully!")
            return response

    def get_duration(self):
        pass

    def transcribe(self):
        return self.get_raw_transcription()

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
