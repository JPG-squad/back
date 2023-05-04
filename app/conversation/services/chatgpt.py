import logging

import openai
from openai import Completion

from app.settings import LOGGER_NAME, OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY

logger = logging.getLogger(LOGGER_NAME)


class ChatGPTService:
    @staticmethod
    def ask(context, question):
        logger.info("Asking to chatgpt: %s", question)
        response = Completion.create(
            engine="text-davinci-003",
            prompt=f"{context + question}",
            temperature=0.5,
            max_tokens=1000,
            n=1,
            stop=None,
            timeout=10,
            frequency_penalty=0,
            presence_penalty=0,
        )

        answer = response.choices[0].text.strip()
        logger.info("Answer from chatgpt: %s", answer)
        return answer
