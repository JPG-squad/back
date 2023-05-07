"""
Views for the user API.
"""
from rest_framework import authentication, generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from conversation.models import ConversationModel, PatientModel
from user.serializers import AuthTokenSerializer, UserConversationsSerializer, UserSerializer


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


class UserConversationsView(generics.GenericAPIView):
    """View to return the user conversations."""

    serializer_class = UserConversationsSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # We are overwritting the default behaivour
    def get(self, request):
        """Retrieve and return the conversations of a user."""
        patients = PatientModel.objects.filter(user_id=request.user.id)
        # Retrieve all the conversations where the patient is in the list of patients
        conversations = ConversationModel.objects.filter(patient__in=patients)
        array_to_return = []
        for conversation in conversations:
            array_to_return.append(
                {
                    "id": conversation.id,
                    "title": conversation.title,
                    "patient_id": conversation.patient_id,
                }
            )
        return Response(status=status.HTTP_200_OK, data=array_to_return)


class LogoutView(generics.ListAPIView):
    """Logout the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Remove the token from the user that made the request."""
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK, data={"message": "Logout successful."})
