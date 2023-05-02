import datetime
import json
import logging

import boto3
import requests

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class WhisperService:
    def __init__(self, bucket_name, file, file_name):
        self.file = file
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name
        self.file_name = file_name

        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)
        logger.info("File uploaded successfully")

    def get_transcription(self):
        return self.transcription

    def get_duration(self):
        return self.duration

    def transcribe(self):
        # set the URL of the endpoint
        url = 'http://ia:80/ia/transcribe'

        # set the parameters for the request
        params = {
            'file_name': self.file_name,
            'bucket_name': self.bucket_name,
        }
        logger.info(str(params))
        # make the request
        response = requests.post(url, json=params)
        logger.info(response.status_code)
        logger.info(response.json())
        self.transcription = response.json()["segments"]
        self.duration = response.json()["segments"][-1]["end"]
        transcription_formatted = []
        for _i, item in enumerate(self.transcription):
            if _i % 2 == 0:
                speaker_turn = "speaker_0"
            else:
                speaker_turn = "speaker_1"
            transcription_formatted.append({"speaker": speaker_turn, "text": item["text"]})
        self.transcription = transcription_formatted
        logger.info(self.transcription)
        return False

    def update_speaker_names(self, transcription, employee_name, patient_name):
        question = '''Can you identify which speaker is the employee, it must had said somethink like:
        "Das tu consentimiento que esta conversacion va ser grabada?"
        Respond with the speaker identifier only'''
        logger.info(f"Conversation json: {transcription}")
        employee_speaker_id = ChatGPTService.ask(json.dumps(transcription), question)
        logger.info("Employee speaker id: %s", employee_speaker_id)

        for i, item in enumerate(transcription):
            if item["speaker"] == employee_speaker_id:
                transcription[i]["speaker"] = employee_name
            else:
                transcription[i]["speaker"] = patient_name

        speakers_changed = []
        for item in transcription:
            if item["speaker"] not in speakers_changed:
                speakers_changed.append(item["speaker"])

        transcription_formatted = {
            "conversation": transcription,
            "speakers": speakers_changed,
        }
        return transcription_formatted
