from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from user_auth_app.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password", "type"]


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Validates unique username/email, ensures password confirmation,
    and creates a new User instance with a hashed password.
    """

    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        allow_null=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Email already registered"
            )
        ],
    )
    username = serializers.CharField(
        required=True,
        allow_blank=False,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(), message="Username already taken"
            )
        ],
    )
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)
    repeated_password = serializers.CharField(
        write_only=True, required=True, allow_blank=False
    )
    type = serializers.ChoiceField(
        choices=User.USER_TYPE_CHOICES, write_only=True, required=True
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError(
                {"repeated_password": "Passwords don't match"}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password", None)
        user = User(
            username=validated_data["username"],
            email=validated_data["email"],
            type=validated_data["type"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomAuthTokenSerializer(serializers.Serializer):
    """
    Custom authentication serializer supporting login via username or email.

    Validates credentials and resolves email-based login to username
    before authenticating the user.
    """

    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not password:
            raise serializers.ValidationError({"detail": ["Password required."]})

        if not username and not email:
            raise serializers.ValidationError(
                {"detail": ["Must include either 'username' or 'email'."]}
            )

        if email:
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist as err:
                raise serializers.ValidationError(
                    {"detail": ["Invalid email or password."]}
                ) from err

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError({"detail": ["Invalid credentials."]})

        attrs["user"] = user
        return attrs
