import datetime
import json
import logging
import re

import boto3
import requests

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME, TRANSCRIPTION_BUCKET_NAME, TRANSCRIPTION_REGION


logger = logging.getLogger(LOGGER_NAME)


class EnchancedWhisperService:
    def __init__(self, file, pacient_id, user_id):
        self.file = file
        self.s3 = boto3.client("s3", region_name=TRANSCRIPTION_REGION)
        self.bucket_name = TRANSCRIPTION_BUCKET_NAME

        now = datetime.datetime.now()
        now_str = now.strftime('%Y_%m_%d_%H_%M_%S_%f')

        self.file_name = f"{pacient_id}_{user_id}_{now_str}_{file.name}"

        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)

    def get_transcription(self):
        return self.transcription

    def get_duration(self):
        return self.duration

    def transcribe(self):
        # set the URL of the endpoint
        url = 'http://ia:80/ia/transcribe-deprecated'

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
        self.transcription = response.json()
        logger.info(self.transcription)
        self.duration = self.transcription[-1]["end"]
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

        # replace duplicated speakers followed elements in transcription
        final_transcription = []
        speaker = ""
        speaker_text = ""
        for item in enumerate(transcription):
            if speaker == item["speaker"]:
                speaker_text += item["text"]
            else:
                if speaker_text != "":
                    final_transcription.append({"speaker": speaker, "text": speaker_text})
                speaker = item["speaker"]
                speaker_text = item["text"]

        transcription_formatted = {
            "conversation": final_transcription,
            "speakers": speakers_changed,
        }
        return transcription_formatted
