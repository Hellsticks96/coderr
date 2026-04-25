from rest_framework import status
from rest_framework.test import APITestCase

from reviews.models import Review
from tests.utils import create_test_review, create_test_user


class ReviewListViewGetTests(APITestCase):
    """Tests for GET /api/reviews/"""

    def setUp(self):
        self.base_url = "/api/reviews/"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.review = create_test_review(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_returns_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_existing_reviews(self):
        response = self.client.get(self.base_url)
        self.assertEqual(len(response.data), 1)

    def test_list_contains_expected_fields(self):
        response = self.client.get(self.base_url)
        expected_fields = {
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(response.data[0].keys()), expected_fields)

    def test_filter_by_business_user_id_returns_matching_reviews(self):
        other_business = create_test_user("business", "seller_2")
        other_customer = create_test_user("customer", "buyer_2")
        create_test_review(other_customer, other_business)
        response = self.client.get(
            self.base_url, {"business_user_id": self.business_user.pk}
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business_user.pk)

    def test_filter_by_reviewer_id_returns_matching_reviews(self):
        other_customer = create_test_user("customer", "buyer_2")
        other_business = create_test_user("business", "seller_2")
        create_test_review(other_customer, other_business)
        response = self.client.get(
            self.base_url, {"reviewer_id": self.customer_user.pk}
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reviewer"], self.customer_user.pk)

    def test_ordering_by_rating_ascending(self):
        other_customer = create_test_user("customer", "buyer_2")
        other_business = create_test_user("business", "seller_2")
        create_test_review(other_customer, other_business, rating=1)
        response = self.client.get(self.base_url, {"ordering": "rating"})
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings))

    def test_ordering_by_rating_descending(self):
        other_customer = create_test_user("customer", "buyer_2")
        other_business = create_test_user("business", "seller_2")
        create_test_review(other_customer, other_business, rating=1)
        response = self.client.get(self.base_url, {"ordering": "-rating"})
        ratings = [r["rating"] for r in response.data]
        self.assertEqual(ratings, sorted(ratings, reverse=True))


class ReviewListViewPostTests(APITestCase):
    """Tests for POST /api/reviews/"""

    def setUp(self):
        self.base_url = "/api/reviews/"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.valid_payload = {
            "business_user": self.business_user.pk,
            "rating": 5,
            "description": "Excellent work!",
        }
        self.client.force_authenticate(user=self.customer_user)

    def test_customer_can_create_review_returns_201(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_business_user_cannot_create_review_returns_403(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_missing_business_user_returns_400(self):
        payload = {"rating": 5}
        response = self.client.post(self.base_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_assigns_reviewer_from_request_user(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.data["reviewer"], self.customer_user.pk)

    def test_create_response_contains_expected_fields(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        expected_fields = {
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_duplicate_review_returns_400(self):
        create_test_review(self.customer_user, self.business_user)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReviewDetailViewGetTests(APITestCase):
    """Tests for GET /api/reviews/<pk>/"""

    def setUp(self):
        self.base_url = "/api/reviews"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.review = create_test_review(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_reviewer_can_retrieve_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_reviewer_returns_403(self):
        other_user = create_test_user("customer", "buyer_2")
        self.client.force_authenticate(user=other_user)
        response = self.client.get(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_review_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_contains_expected_fields(self):
        response = self.client.get(f"{self.base_url}/{self.review.pk}/")
        expected_fields = {
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)


class ReviewDetailViewPatchTests(APITestCase):
    """Tests for PATCH /api/reviews/<pk>/"""

    def setUp(self):
        self.base_url = "/api/reviews"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.review = create_test_review(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_reviewer_can_update_returns_200(self):
        response = self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"rating": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_reviewer_returns_403(self):
        other_user = create_test_user("customer", "buyer_2")
        self.client.force_authenticate(user=other_user)
        response = self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"rating": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"rating": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_rating_persists(self):
        self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"rating": 2},
            format="json",
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 2)

    def test_update_description_persists(self):
        self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"description": "Updated description"},
            format="json",
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.description, "Updated description")

    def test_update_response_contains_expected_fields(self):
        response = self.client.patch(
            f"{self.base_url}/{self.review.pk}/",
            {"rating": 3},
            format="json",
        )
        expected_fields = {
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_update_nonexistent_review_returns_404(self):
        response = self.client.patch(
            f"{self.base_url}/99999/",
            {"rating": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReviewDetailViewDeleteTests(APITestCase):
    """Tests for DELETE /api/reviews/<pk>/"""

    def setUp(self):
        self.base_url = "/api/reviews"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.review = create_test_review(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_reviewer_can_delete_returns_204(self):
        response = self.client.delete(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_removes_from_db(self):
        pk = self.review.pk
        self.client.delete(f"{self.base_url}/{pk}/")
        self.assertFalse(Review.objects.filter(pk=pk).exists())

    def test_non_reviewer_returns_403(self):
        other_user = create_test_user("customer", "buyer_2")
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"{self.base_url}/{self.review.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_review_returns_404(self):
        response = self.client.delete(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
