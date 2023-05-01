import json
import logging

from channels.generic.websocket import WebsocketConsumer
from rest_framework import authentication, permissions

from app.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class TranscribeConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope["user"].is_anonymous:
            logger.warning("Anonymous user tried to connect to websocket, access denied.")
            self.close()
        else:
            logger.info(
                f"User with id: {self.scope['user'].id} and email: {self.scope['user'].email} connected to websocket!"
            )
            self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        logger.info(F"Received message: {text_data}")
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
