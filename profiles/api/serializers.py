from rest_framework import serializers

from user_auth_app.models import User


#Serializer for profile views. Get list of all users, get all customer users, get all business users or patch user.
class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]