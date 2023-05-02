import asyncio
import json
import logging

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from app.settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                print(alt.transcript)


async def basic_transcribe(audio_data):
    # Set up our client with your chosen Region
    client = TranscribeStreamingClient(region="eu-west-1")

    # Start transcription to generate async stream
    stream = await client.start_stream_transcription(
        language_code="es-US",
        media_sample_rate_hz=16000,
        media_encoding="ogg-opus",
    )

    async def write_chunks():
        await stream.input_stream.send_audio_event(audio_chunk=audio_data)
        await stream.input_stream.end_stream()

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())


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

        async def transcribe_audio(audio_data):
            transcript = await basic_transcribe(audio_data)
            print(transcript)

        async_to_sync(transcribe_audio)(bytes_data)
        self.send('recieved')
