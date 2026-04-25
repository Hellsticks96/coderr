from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from tests.utils import create_test_user
from user_auth_app.api.serializers import (
    CustomAuthTokenSerializer,
    RegistrationSerializer,
)

User = get_user_model()


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
        # Not in spec, but a critical security invariant: passwords must never
        # be stored in plain text.
        serializer = RegistrationSerializer(data=self.valid_data)
        serializer.is_valid()
        user = serializer.save()
        self.assertTrue(user.check_password("testPass123"))

    def test_repeated_password_not_saved_on_user(self):
        # Not in spec, but ensures the confirmation field is never persisted
        # to the user model.
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
        # Email login is not in the spec but is supported by the implementation.
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
        # Email login is not in the spec but is supported by the implementation.
        serializer = CustomAuthTokenSerializer(
            data={"email": "nobody@test.com", "password": "testPass123"}
        )
        self.assertFalse(serializer.is_valid())

    def test_missing_password(self):
        serializer = CustomAuthTokenSerializer(data={"username": self.user.username})
        self.assertFalse(serializer.is_valid())

    def test_missing_username_returns_invalid(self):
        serializer = CustomAuthTokenSerializer(data={"password": "testPass123"})
        self.assertFalse(serializer.is_valid())
