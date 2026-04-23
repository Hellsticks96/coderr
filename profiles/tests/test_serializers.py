from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from profiles.api.serializers import UserProfileSerializer

User = get_user_model()


def create_test_user(user_type, username):
    """
    Helper to create a test user.

    Args:
        user_type (str): The user type, either 'customer' or 'business'.
        username (str): A unique identifier appended to the generated username and email.
    """
    return User.objects.create_user(
        username=f"test_{username}_{user_type}",
        email=f"test_{username}_{user_type}@test.com",
        password="testpass123",
        type=user_type,
    )


class UserProfileSerializerTests(APITestCase):
    """Tests for UserProfileSerializer"""

    def setUp(self):
        self.user = create_test_user("customer", "user")

    def test_contains_expected_fields(self):
        serializer = UserProfileSerializer(instance=self.user)
        expected_fields = {
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
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_user_field_returns_id(self):
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(serializer.data["user"], self.user.id)

    def test_created_at_is_read_only(self):
        serializer = UserProfileSerializer(
            instance=self.user,
            data={"created_at": "2000-01-01T00:00:00Z"},
            partial=True,
        )
        serializer.is_valid()
        updated_user = serializer.save()
        self.assertNotEqual(str(updated_user.created_at), "2000-01-01T00:00:00Z")
