import json
import logging

from channels.generic.websocket import WebsocketConsumer

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

    def receive(self, text_data=None, bytes_data=None):
        logger.info(f"We are in the conversation: {self.scope['url_route']['kwargs']['conversation_id']}")
        logger.info("Received message")
        logger.info(bytes_data)
        self.send('recieved')
