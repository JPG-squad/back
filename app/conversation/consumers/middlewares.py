import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token

from app.settings import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


@database_sync_to_async
def return_user(token_string):
    try:
        user = Token.objects.get(key=token_string).user
    except Exception as e:
        logger.exception(e)
        user = AnonymousUser()
    return user


class TokenAuthMiddleWare:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope["query_string"]
        query_params = query_string.decode()
        query_dict = parse_qs(query_params)
        token = query_dict["token"][0]
        user = await return_user(token)
        scope["user"] = user
        return await self.app(scope, receive, send)
