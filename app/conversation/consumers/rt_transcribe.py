import asyncio
import base64
from io import BytesIO
import json
import logging

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# import pyaudio
# from pydub import AudioSegment
from app.settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)

stream_client = TranscribeStreamingClient(region="eu-west-1")


class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        logger.info("I am being called!")
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        results = transcript_event.transcript.results
        for result in results:
            for alt in result.alternatives:
                logger.info(alt.transcript)


# async def transcribe(audio_stream):
#     client = TranscribeStreamingClient(region="eu-west-1")
#     stream = await client.start_stream_transcription(
#         language_code="es-US", media_sample_rate_hz=16000, media_encoding="ogg-opus"
#     )
#     handler = MyEventHandler(stream.output_stream)

#     # Signal end of audio stream
#     await stream.input_stream.end_stream()

#     async def write_chunks():
#         for chunk in audio_stream:
#             await stream.input_stream.send_audio_event(audio_chunk=chunk)

#     await asyncio.gather(write_chunks(), handler.handle_events())


# async def basic_transcribe(audio_data):
#     # Set up our client with your chosen Region
#     client = TranscribeStreamingClient(region="eu-west-1")

#     # Start transcription to generate async stream
#     stream = await client.start_stream_transcription(
#         language_code="es-US",
#         media_sample_rate_hz=16000,
#         media_encoding="ogg-opus",
#     )

#     async def write_chunks():
#         await stream.input_stream.send_audio_event(audio_chunk=audio_data)
#         await stream.input_stream.end_stream()

#     # Instantiate our handler and start processing events
#     handler = MyEventHandler(stream.output_stream)
#     await asyncio.gather(write_chunks(), handler.handle_events())


class TranscribeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            logger.warning("Anonymous user tried to connect to websocket, access denied.")
            await self.close()
        else:
            logger.info(
                f"User with id: {self.scope['user'].id} and email: {self.scope['user'].email} connected to websocket!"
            )
            await self.accept()
            self.input_queue = asyncio.Queue()
            await self.send(text_data="Connection established!")
            self.loop = asyncio.get_event_loop()
            self.stream = await self.loop.create_task(
                stream_client.start_stream_transcription(
                    language_code="es-US",
                    media_sample_rate_hz=16000,
                    media_encoding="ogg-opus",
                )
            )

            print('Hola Pau')
            self.handler = MyEventHandler(self.stream.output_stream)

    async def disconnect(self, close_code):
        await self.stream.input_stream.end_stream()

    async def transcribe(self):
        async def write_chunks():
            logger.info("Writing chunks...")
            async for chunk in websocket_stream(self.input_queue):
                await self.stream.input_stream.send_audio_event(audio_chunk=chunk)
            await self.stream.input_stream.end_stream()

        await asyncio.gather(write_chunks(), self.handler.handle_events())

    async def receive(self, text_data=None, bytes_data=None):
        logger.info(f"We are in the conversation: {self.scope['url_route']['kwargs']['conversation_id']}")
        logger.info("Received message")
        self.loop.call_soon_threadsafe(self.input_queue.put_nowait, bytes_data)
        logger.info("We have reached here")
        self.loop.run_until_complete(self.transcribe())
        self.loop.close()


async def websocket_stream(queue):
    while True:
        indata = await queue.get()
        yield indata
