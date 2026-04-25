from rest_framework.test import APIRequestFactory, APITestCase

from offers.api.serializers import (
    DetailSerializer,
    PackageCreateSerializer,
    PackageListSerializer,
    PackageSerializer,
)
from offers.models import Package
from tests.utils import VALID_DETAILS, create_test_package, create_test_user


class DetailSerializerTests(APITestCase):
    """Tests for DetailSerializer"""

    def setUp(self):
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.detail = self.package.details.first()

    def test_contains_expected_fields(self):
        serializer = DetailSerializer(instance=self.detail)
        expected_fields = {
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)


class PackageSerializerTests(APITestCase):
    """Tests for PackageSerializer"""

    def setUp(self):
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.request = APIRequestFactory().get("/")

    def test_contains_expected_fields(self):
        serializer = PackageSerializer(
            instance=self.package, context={"request": self.request}
        )
        expected_fields = {
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_list_serializer_contains_user_details(self):
        serializer = PackageListSerializer(
            instance=self.package, context={"request": self.request}
        )
        self.assertIn("user_details", serializer.data)
        self.assertIn("username", serializer.data["user_details"])

    def test_min_price_returns_lowest_detail_price(self):
        serializer = PackageSerializer(
            instance=self.package, context={"request": self.request}
        )
        self.assertEqual(serializer.data["min_price"], 99.99)

    def test_min_delivery_time_returns_shortest_delivery_time(self):
        serializer = PackageSerializer(
            instance=self.package, context={"request": self.request}
        )
        self.assertEqual(serializer.data["min_delivery_time"], 3)

    def test_min_price_is_none_when_no_details(self):
        empty_package = Package.objects.create(
            user=self.business_user,
            title="Empty",
            description="No details",
        )
        serializer = PackageSerializer(
            instance=empty_package, context={"request": self.request}
        )
        self.assertIsNone(serializer.data["min_price"])

    def test_min_delivery_time_is_none_when_no_details(self):
        empty_package = Package.objects.create(
            user=self.business_user,
            title="Empty",
            description="No details",
        )
        serializer = PackageSerializer(
            instance=empty_package, context={"request": self.request}
        )
        self.assertIsNone(serializer.data["min_delivery_time"])

    def test_details_is_a_list(self):
        serializer = PackageSerializer(
            instance=self.package, context={"request": self.request}
        )
        self.assertIsInstance(serializer.data["details"], list)


class PackageCreateSerializerTests(APITestCase):
    """Tests for PackageCreateSerializer"""

    def setUp(self):
        self.business_user = create_test_user("business", "seller_1")
        self.valid_data = {
            "title": "My Offer",
            "description": "An offer",
            "details": VALID_DETAILS,
        }

    def test_valid_data_is_valid(self):
        serializer = PackageCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_missing_title_is_invalid(self):
        data = {**self.valid_data, "title": ""}
        serializer = PackageCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_missing_details_is_invalid(self):
        data = {"title": "My Offer", "description": "An offer"}
        serializer = PackageCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("details", serializer.errors)

    def test_fewer_than_three_details_is_invalid(self):
        data = {**self.valid_data, "details": [VALID_DETAILS[0]]}
        serializer = PackageCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_detail_missing_required_field_is_invalid(self):
        incomplete_detail = {k: v for k, v in VALID_DETAILS[0].items() if k != "price"}
        data = {
            **self.valid_data,
            "details": [incomplete_detail, VALID_DETAILS[1], VALID_DETAILS[2]],
        }
        serializer = PackageCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_saves_package_with_details(self):
        serializer = PackageCreateSerializer(data=self.valid_data)
        serializer.is_valid()
        package = serializer.save(user=self.business_user)
        self.assertEqual(package.title, "My Offer")
        self.assertEqual(package.details.count(), 3)

    def test_update_preserves_detail_ids(self):
        # Spec: detail IDs must not change when patching — details are updated
        # in place, not deleted and recreated.
        package = create_test_package(self.business_user)
        original_id = package.details.first().pk
        updated_basic = {**VALID_DETAILS[0], "price": 199.99}
        serializer = PackageCreateSerializer(
            instance=package,
            data={"details": [updated_basic]},
            partial=True,
        )
        serializer.is_valid()
        serializer.save()
        self.assertTrue(package.details.filter(pk=original_id).exists())
