import io
import json
import logging
import os

from aiohttp import FormData
import boto3
from deepgram import Deepgram

from .chatgpt import ChatGPTService
from app.settings import DEEPGRAM_API_KEY, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class DeepgramService:
    def __init__(self, bucket_name, file, file_name, employee_name, patient_name):
        self.dg_client = Deepgram(DEEPGRAM_API_KEY)
        self.file = file
        self.s3 = boto3.client("s3", region_name="eu-west-1")
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
        self.duration = 0
        self.patient_name = patient_name
        self.employee_name = employee_name

    def get_raw_transcription(self):
        self.s3.download_file(self.bucket_name, self.file_name, "recordings/" + self.file_name)
        with open("recordings/" + self.file_name, "rb") as f:
            source = {"buffer": f, "mimetype": 'audio/wav'}
            logger.info("Sending file to transcribe to Deepgram...")
            response = self.dg_client.transcription.sync_prerecorded(source, self.options)
            logger.info("Transcription received successfully!")
            os.remove("recordings/" + self.file_name)
            return response

    def get_duration(self):
        return self.duration

    def transcribe(self):
        raw_transcript = self.get_raw_transcription()
        words = raw_transcript["results"]["channels"][0]["alternatives"][0]["words"]
        self.duration = words[-1]["end"]
        current_speaker = 0
        current_transcript = ""
        final_transcript = []
        for word in words:
            if word["speaker"] != current_speaker:
                final_transcript.append({"speaker": current_speaker, "text": current_transcript})
                current_transcript = ""
                current_speaker = word["speaker"]
                current_transcript += word["punctuated_word"]
            else:
                current_transcript += " " + word["punctuated_word"]
        final_transcript.append({"speaker": current_speaker, "text": current_transcript})
        transcript_to_return = {"conversation": final_transcript}
        improved_transcript = self._improve_transcription(transcript_to_return)
        transcript_with_speaker_names = self.update_speaker_names(improved_transcript)
        return transcript_with_speaker_names

    def _improve_transcription(self, transcription):
        pre_context = '''
        A continuación te voy a pasar un json que es una conversación transcrita.
        Como vas a ver, en cada objecto hay un el texto y quien lo ha dicho: \n\n
        '''
        question = '''
        \n
        En el json anterion, puede ser que haya palabras que se hayan esten mal
        y que realmente las haya dicho las siguiente persona en hablar.
        Podrias arrreglarlo? Devuelveme un JSON igual que el que te he pasado yo,
        valido en formato UTF8:\n
        '''
        conversation_json = json.loads(ChatGPTService.ask(pre_context + str(transcription), question).replace("'", '"'))
        return conversation_json

    def update_speaker_names(self, transcription):
        for i, item in enumerate(transcription["conversation"]):
            if item["speaker"] == 0:
                transcription["conversation"][i]["speaker"] = self.employee_name
            else:
                transcription["conversation"][i]["speaker"] = self.patient_name
        return transcription
