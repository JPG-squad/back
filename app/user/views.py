"""
Views for the user API.
"""
from rest_framework import status
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from user.serializers import UserSerializer, AuthTokenSerializer

# The CreateAPIView it's a view designed to handle http post requests
# Abstracts a lot of the logic, we simply have to indicate a serializer class to handle it


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


# We are inheriting for ObtainAuthToken, which is a view provided already by django for this purpose
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # We are overwritting the default behaivour
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user


class LogoutView(generics.ListAPIView):
    """Logout the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Remove the token from the user that made the request."""
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK, data={"message": "Logout successful."})
