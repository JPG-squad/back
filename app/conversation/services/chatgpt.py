import logging

from openai import Completion

from app.settings import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class ChatGPTService:
    @staticmethod
    def ask(context, question):
        prompt = f"Q: {question}\nA:"
        logger.info("Asking to chatgpt: %s", prompt)
        response = Completion.create(
            engine="text-davinci-003",
            prompt=context + prompt,
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
