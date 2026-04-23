from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

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


class UserProfileListViewTests(APITestCase):
    """Tests for GET /api/profiles/"""

    def setUp(self):
        self.base_url = "/api/profiles/"
        self.user = create_test_user("customer", "user_1")
        self.client.force_authenticate(user=self.user)

    def test_list_users_authenticated_returns_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileDetailViewTests(APITestCase):
    """Tests for GET/PATCH/DELETE /api/profiles/<pk>/"""

    def setUp(self):
        self.base_url = "/api/profiles"
        self.user = create_test_user("customer", "user_1")
        self.other_user = create_test_user("customer", "user_2")
        self.client.force_authenticate(user=self.user)

    def test_retrieve_own_profile_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_other_profile_returns_200(self):
        # Any authenticated user can view any profile
        response = self.client.get(f"{self.base_url}/{self.other_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_profile_returns_200(self):
        response = self.client.patch(
            f"{self.base_url}/{self.user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_profile_returns_403(self):
        response = self.client.patch(
            f"{self.base_url}/{self.other_user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_profile_returns_204(self):
        response = self.client.delete(f"{self.base_url}/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_profile_returns_403(self):
        response = self.client.delete(f"{self.base_url}/{self.other_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_nonexistent_profile_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_password_not_returned_in_response(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertNotIn("password", response.data)


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

    def test_missing_username_and_email_returns_400(self):
        response = self.client.post(
            self.base_url,
            {"password": "testPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
