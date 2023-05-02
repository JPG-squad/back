"""
Serializers for the user API View.
"""

from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext as _
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    # Here we are overwritting the default create model for ModelSerializer
    # This is called after validation (this is why it receives validated_data)
    # By default, it would simply have created a user
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        # pop retrieves the value and removes it from validated_data
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    # Here we are overwritting the default function in django serializers,
    # Which is called to validate the input (which is what serializers do). We receive attrs as a parameter
    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        # authenticate is a built in function of django auth, we have to pass the request too
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            # We raise a ValidationError, which is the standard way of doing it
            # A validation error in serializers will return the error and create an http response with a 400 bad request
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        # If we authenticate correctly, we return the user in the attributes
        attrs["user"] = user
        # In validate method, we have to reutrn the attrs
        return attrs
