import datetime
import json
import logging

import boto3
import requests

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class EnchancedWhisperService:
    def __init__(self, bucket_name, file, pacient_id, user_id):
        self.file = file
        self.s3 = boto3.client("s3")
        self.bucket_name = bucket_name

        now = datetime.datetime.now()
        now_str = now.strftime('%Y_%m_%d_%H_%M_%S_%f')

        self.file_name = f"{pacient_id}_{user_id}_{now_str}_{file.name}"

        logger.info("Uploading file %s to bucket %s", self.file_name, self.bucket_name)
        self.s3.upload_fileobj(file, self.bucket_name, self.file_name)

    def get_transcription(self):
        return

    def get_duration(self):
        return

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
        return

    def _improve_transcription(self, transcription):
        return
