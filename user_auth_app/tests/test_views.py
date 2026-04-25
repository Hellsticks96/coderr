from rest_framework import status
from rest_framework.test import APITestCase

from tests.utils import create_test_user


class RegistrationViewTests(APITestCase):
    """Tests for POST /api/registration/"""

    def setUp(self):
        self.base_url = "/api/registration/"
        self.valid_payload = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "testPass123",
            "repeated_password": "testPass123",
            "type": "customer",
        }

    def test_valid_registration_returns_201(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_valid_registration_returns_token(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertIn("token", response.data)

    def test_valid_registration_returns_user_data(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.data["username"], "newuser")
        self.assertEqual(response.data["email"], "new@test.com")
        self.assertIn("user_id", response.data)

    def test_password_not_returned_in_response(self):
        # Security: password must never be exposed in the response, even though
        # it is not explicitly listed as excluded in the spec.
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertNotIn("password", response.data)

    def test_password_mismatch_returns_400(self):
        payload = {**self.valid_payload, "repeated_password": "wrongpass"}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        self.client.post(self.base_url, self.valid_payload, format="json")
        payload = {**self.valid_payload, "username": "anotheruser"}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_username_returns_400(self):
        self.client.post(self.base_url, self.valid_payload, format="json")
        payload = {**self.valid_payload, "email": "another@test.com"}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields_returns_400(self):
        response = self.client.post(self.base_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_type_returns_400(self):
        payload = {**self.valid_payload, "type": "invalidtype"}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomLoginViewTests(APITestCase):
    """Tests for POST /api/login/"""

    def setUp(self):
        self.base_url = "/api/login/"
        self.user = create_test_user("customer", "user_1")

    def test_login_with_username_returns_200(self):
        response = self.client.post(
            self.base_url,
            {"username": self.user.username, "password": "testPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_returns_token(self):
        response = self.client.post(
            self.base_url,
            {"username": self.user.username, "password": "testPass123"},
            format="json",
        )
        self.assertIn("token", response.data)

    def test_login_returns_user_data(self):
        response = self.client.post(
            self.base_url,
            {"username": self.user.username, "password": "testPass123"},
            format="json",
        )
        self.assertEqual(response.data["username"], "test_user_1_customer")
        self.assertEqual(response.data["email"], "test_user_1_customer@test.com")
        self.assertIn("user_id", response.data)

    def test_wrong_password_returns_400(self):
        response = self.client.post(
            self.base_url,
            {"username": self.user.username, "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_user_returns_400(self):
        response = self.client.post(
            self.base_url,
            {"username": "nobody", "password": "testPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_password_returns_400(self):
        response = self.client.post(
            self.base_url,
            {"username": self.user.username},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_username_returns_400(self):
        response = self.client.post(
            self.base_url,
            {"password": "testPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
