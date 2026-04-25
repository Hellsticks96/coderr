from rest_framework.test import APIRequestFactory, APITestCase

from reviews.api.serializers import ReviewSerializer
from tests.utils import create_test_review, create_test_user


class ReviewSerializerTests(APITestCase):
    """Tests for ReviewSerializer"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.review = create_test_review(self.customer_user, self.business_user)
        self.request = APIRequestFactory().post("/")
        self.request.user = self.customer_user

    def test_contains_expected_fields(self):
        serializer = ReviewSerializer(
            instance=self.review, context={"request": self.request}
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
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_reviewer_is_read_only(self):
        other_user = create_test_user("customer", "buyer_2")
        serializer = ReviewSerializer(
            instance=self.review,
            data={"reviewer": other_user.pk},
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid()
        updated = serializer.save()
        self.assertEqual(updated.reviewer, self.customer_user)

    def test_created_at_is_read_only(self):
        serializer = ReviewSerializer(
            instance=self.review,
            data={"created_at": "2000-01-01T00:00:00Z"},
            partial=True,
            context={"request": self.request},
        )
        serializer.is_valid()
        updated = serializer.save()
        self.assertNotEqual(str(updated.created_at), "2000-01-01T00:00:00Z")

    def test_duplicate_review_is_invalid(self):
        second_request = APIRequestFactory().post("/")
        second_request.user = self.customer_user
        data = {"business_user": self.business_user.pk, "rating": 4}
        serializer = ReviewSerializer(data=data, context={"request": second_request})
        self.assertFalse(serializer.is_valid())
