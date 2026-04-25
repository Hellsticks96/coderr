from rest_framework import status
from rest_framework.test import APITestCase

from tests.utils import create_test_package, create_test_review, create_test_user


class StatsViewTests(APITestCase):
    """Tests for GET /api/base-info/"""

    def setUp(self):
        self.base_url = "/api/base-info/"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.client.force_authenticate(user=self.customer_user)

    def test_returns_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_200(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_contains_expected_fields(self):
        response = self.client.get(self.base_url)
        expected_fields = {
            "review_count",
            "average_rating",
            "business_profile_count",
            "offer_count",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_review_count_is_correct(self):
        create_test_review(self.customer_user, self.business_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["review_count"], 1)

    def test_average_rating_is_correct(self):
        create_test_review(self.customer_user, self.business_user, rating=4)
        other_customer = create_test_user("customer", "buyer_2")
        other_business = create_test_user("business", "seller_2")
        create_test_review(other_customer, other_business, rating=2)
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["average_rating"], 3.0)

    def test_average_rating_is_rounded_to_one_decimal(self):
        create_test_review(self.customer_user, self.business_user, rating=5)
        other_customer = create_test_user("customer", "buyer_2")
        other_business = create_test_user("business", "seller_2")
        create_test_review(other_customer, other_business, rating=4)
        third_customer = create_test_user("customer", "buyer_3")
        third_business = create_test_user("business", "seller_3")
        create_test_review(third_customer, third_business, rating=4)
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["average_rating"], 4.3)

    def test_business_profile_count_is_correct(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["business_profile_count"], 1)

    def test_offer_count_is_correct(self):
        create_test_package(self.business_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["offer_count"], 1)

    def test_returns_zero_when_no_reviews(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.data["review_count"], 0)
        self.assertEqual(response.data["average_rating"], 0)
