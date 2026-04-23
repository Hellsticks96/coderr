from rest_framework.test import APITestCase

from profiles.api.serializers import UserProfileSerializer
from tests.utils import create_test_user


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
