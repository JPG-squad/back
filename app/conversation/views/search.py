import json
import logging
from operator import is_

from django.http import JsonResponse
from rest_framework import authentication, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.settings import LOGGER_NAME
from conversation.serializers import SearchSerializer
from conversation.services.opensearch import open_search_service


logger = logging.getLogger(LOGGER_NAME)


class SearchView(GenericAPIView):
    """Search conversations."""

    serializer_class = SearchSerializer
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Search conversations."""
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.data["text"]
            logger.info("Searching for: %s", text)
            response = open_search_service.search_conversation(text)

            return JsonResponse(data=response, safe=False, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
