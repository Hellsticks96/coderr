from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from user_auth_app.api.serializers import (
    CustomAuthTokenSerializer,
    RegistrationSerializer,
    UserProfileSerializer,
)

User = get_user_model()


def create_test_user(user_type, username):
    """
    Helper to create a standard user

    Args:

    type (User.type): the user type of the instance to be created.

    """
    return User.objects.create_user(
        username=f"test_{username}_{user_type}",
        email=f"test_{username}_{user_type}@test.com",
        password="testPass123",
        type=user_type,
    )


class UserProfileSerializerTests(APITestCase):
    """Tests for UserProfileSerializer"""

    def setUp(self):
        self.user = create_test_user("customer", "user_1")

    def test_contains_expected_fields(self):
        serializer = UserProfileSerializer(instance=self.user)
        self.assertEqual(
            set(serializer.data.keys()), {"username", "email", "password", "type"}
        )


class RegistrationSerializerTests(APITestCase):
    """Tests for RegistrationSerializer"""

    def setUp(self):
        self.valid_data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "testPass123",
            "repeated_password": "testPass123",
            "type": "customer",
        }

    def test_valid_data_is_valid(self):
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch_is_invalid(self):
        data = {**self.valid_data, "repeated_password": "wrongpass"}
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("repeated_password", serializer.errors)

    def test_duplicate_email_is_invalid(self):
        User.objects.create_user(
            username="existing",
            email="new@test.com",
            password="testPass123",
        )
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_duplicate_username_is_invalid(self):
        User.objects.create_user(
            username="newuser",
            email="other@test.com",
            password="testPass123",
        )
        serializer = RegistrationSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_invalid_type_is_invalid(self):
        data = {**self.valid_data, "type": "invalidtype"}
        serializer = RegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("type", serializer.errors)

    def test_create_hashes_password(self):
        serializer = RegistrationSerializer(data=self.valid_data)
        serializer.is_valid()
        user = serializer.save()
        self.assertTrue(user.check_password("testPass123"))

    def test_repeated_password_not_saved_on_user(self):
        serializer = RegistrationSerializer(data=self.valid_data)
        serializer.is_valid()
        user = serializer.save()
        self.assertFalse(hasattr(user, "repeated_password"))


class CustomAuthTokenSerializerTests(APITestCase):
    """Tests for CustomAuthTokenSerializer"""

    def setUp(self):
        self.user = create_test_user("customer", "user_1")

    def test_valid_with_username(self):
        serializer = CustomAuthTokenSerializer(
            data={"username": self.user.username, "password": "testPass123"}
        )
        self.assertTrue(serializer.is_valid())

    def test_valid_with_email(self):
        serializer = CustomAuthTokenSerializer(
            data={"email": self.user.email, "password": "testPass123"}
        )
        self.assertTrue(serializer.is_valid())

    def test_invalid_password(self):
        serializer = CustomAuthTokenSerializer(
            data={"username": self.user.username, "password": "wrongpass"}
        )
        self.assertFalse(serializer.is_valid())

    def test_nonexistent_email(self):
        serializer = CustomAuthTokenSerializer(
            data={"email": "nobody@test.com", "password": "testPass123"}
        )
        self.assertFalse(serializer.is_valid())

    def test_missing_password(self):
        serializer = CustomAuthTokenSerializer(data={"username": self.user.username})
        self.assertFalse(serializer.is_valid())

    def test_missing_username_and_email(self):
        serializer = CustomAuthTokenSerializer(data={"password": "testPass123"})
        self.assertFalse(serializer.is_valid())

    def test_returns_user_in_validated_data(self):
        serializer = CustomAuthTokenSerializer(
            data={"username": self.user.username, "password": "testPass123"}
        )
        serializer.is_valid()
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)
