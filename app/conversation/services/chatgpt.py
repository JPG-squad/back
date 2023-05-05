import logging

import openai
from openai import Completion

from app.settings import LOGGER_NAME, OPENAI_API_KEY
from conversation.models import AnswerModel, RelevantPointModel


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

    @staticmethod
    def ask_for_relevant_points(input_context, patient_id):
        pre_context_prompt = """
            Eres un trabajador que tiene que rellenar un formulario con una serie de preguntas.
            Estas entrevistando a un usuario en una primera toma de contacto. Tu serás el que hace
            las preguntas en el contexto, y el usuario será el que las responda.
            Te voy a proporcionar el contexto y una pregunta o campo que debes rellenar.
            Solo debes responder con informacion del usuario.
            Si no sabes responder a esa pregunta/campo, contesta solamente con un '0'.
            Si sabes la respuesta a la pregunta o al campo que debes rellenar,
            no vuelvas a escribir la pregunta o el nombre del campo, simplemente contesta con el valor. \n
            El contexto es el siguiente: \n
        """
        context = pre_context_prompt + input_context + " \n\nQueremos saber la respuesta a: "
        rps = RelevantPointModel.objects.all()
        for rp in rps:
            question = rp.text
            current_anwer_object = AnswerModel.objects.filter(patient_id=patient_id, relevant_point_id=rp.id).first()
            if current_anwer_object.resolved:
                question_to_chat = question + '\nContesta solo con informacion que se te pide.'
                answer = ChatGPTService.ask(context, question_to_chat)
                current_anwer_object.text = answer
                current_anwer_object.save()
