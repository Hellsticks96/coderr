from rest_framework import status
from rest_framework.test import APITestCase

from tests.utils import create_test_user


class ProfileViewTests(APITestCase):
    """Tests for GET/PATCH /api/profile/<pk>/"""

    def setUp(self):
        self.user = create_test_user("customer", "user_1")
        self.other_user = create_test_user("customer", "other_1")
        self.client.force_authenticate(user=self.user)

    def test_retrieve_own_profile_returns_200(self):
        response = self.client.get(f"/api/profile/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_other_profile_returns_200(self):
        response = self.client.get(f"/api/profile/{self.other_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_profile_returns_correct_fields(self):
        response = self.client.get(f"/api/profile/{self.user.pk}/")
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
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_update_own_profile_returns_200(self):
        response = self.client.patch(
            f"/api/profile/{self.user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_profile_persists_changes(self):
        self.client.patch(
            f"/api/profile/{self.user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.location, "Berlin")

    def test_update_other_profile_returns_403(self):
        response = self.client.patch(
            f"/api/profile/{self.other_user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_nonexistent_profile_returns_404(self):
        response = self.client.get("/api/profile/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"/api/profile/{self.user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"/api/profile/{self.user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_nonexistent_profile_returns_404(self):
        response = self.client.patch(
            "/api/profile/99999/",
            {"location": "Berlin"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_response_contains_expected_fields(self):
        response = self.client.patch(
            f"/api/profile/{self.user.pk}/",
            {"location": "Berlin"},
            format="json",
        )
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
        self.assertEqual(set(response.data.keys()), expected_fields)


class CustomerListViewTests(APITestCase):
    """Tests for GET /api/profiles/customer/"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "user_1")
        self.business_user = create_test_user("business", "user_2")
        self.client.force_authenticate(user=self.customer_user)

    def test_returns_200(self):
        response = self.client.get("/api/profiles/customer/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_only_customers(self):
        response = self.client.get("/api/profiles/customer/")
        for profile in response.data:
            self.assertEqual(profile["type"], "customer")

    def test_does_not_return_business_users(self):
        response = self.client.get("/api/profiles/customer/")
        usernames = [profile["username"] for profile in response.data]
        self.assertNotIn(self.business_user.username, usernames)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/profiles/customer/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BusinessListViewTests(APITestCase):
    """Tests for GET /api/profiles/business/"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "user_2")
        self.business_user = create_test_user("business", "user_1")
        self.client.force_authenticate(user=self.business_user)

    def test_returns_200(self):
        response = self.client.get("/api/profiles/business/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_only_business_users(self):
        response = self.client.get("/api/profiles/business/")
        for profile in response.data:
            self.assertEqual(profile["type"], "business")

    def test_does_not_return_customer_users(self):
        response = self.client.get("/api/profiles/business/")
        usernames = [profile["username"] for profile in response.data]
        self.assertNotIn(self.customer_user.username, usernames)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/profiles/business/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
