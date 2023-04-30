import json
import logging

import boto3

from .chatgpt import ChatGPTService
from app.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class EnchancedWhisperService:
    def __init__(self, file):
        self.file = file

    def get_transcription(self):
        return

    def get_duration(self):
        return

    def transcribe(self):
        return

    def _improve_transcription(self, transcription):
        return
