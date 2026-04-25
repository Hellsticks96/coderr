from rest_framework.test import APIRequestFactory, APITestCase

from orders.api.serializers import (
    OrderCountSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderSerializer,
    OrderTotalCountSerializer,
)
from tests.utils import create_test_order, create_test_package, create_test_user


class OrderSerializerTests(APITestCase):
    """Tests for OrderSerializer"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.order = create_test_order(self.customer_user, self.business_user)

    def test_contains_expected_fields(self):
        serializer = OrderSerializer(instance=self.order)
        expected_fields = {
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)


class OrderCreateSerializerTests(APITestCase):
    """Tests for OrderCreateSerializer"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.detail = self.package.details.first()
        request = APIRequestFactory().post("/")
        request.user = self.customer_user
        self.context = {"request": request}

    def test_valid_data_is_valid(self):
        serializer = OrderCreateSerializer(
            data={"offer_detail_id": self.detail.pk},
            context=self.context,
        )
        self.assertTrue(serializer.is_valid())

    def test_invalid_offer_detail_id_type_is_invalid(self):
        serializer = OrderCreateSerializer(
            data={"offer_detail_id": "not-an-integer"},
            context=self.context,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("offer_detail_id", serializer.errors)

    def test_create_copies_detail_fields(self):
        serializer = OrderCreateSerializer(
            data={"offer_detail_id": self.detail.pk},
            context=self.context,
        )
        serializer.is_valid()
        order = serializer.save()
        self.assertEqual(order.title, self.detail.title)
        self.assertEqual(order.price, self.detail.price)
        self.assertEqual(order.offer_type, self.detail.offer_type)

    def test_create_assigns_customer_from_request(self):
        serializer = OrderCreateSerializer(
            data={"offer_detail_id": self.detail.pk},
            context=self.context,
        )
        serializer.is_valid()
        order = serializer.save()
        self.assertEqual(order.customer_user, self.customer_user)

    def test_create_assigns_business_user_from_package(self):
        serializer = OrderCreateSerializer(
            data={"offer_detail_id": self.detail.pk},
            context=self.context,
        )
        serializer.is_valid()
        order = serializer.save()
        self.assertEqual(order.business_user, self.business_user)


class OrderDetailSerializerTests(APITestCase):
    """Tests for OrderDetailSerializer"""

    def setUp(self):
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.order = create_test_order(self.customer_user, self.business_user)

    def test_contains_expected_fields(self):
        serializer = OrderDetailSerializer(instance=self.order)
        expected_fields = {
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)

    def test_status_is_writable(self):
        serializer = OrderDetailSerializer(
            instance=self.order,
            data={"status": "completed"},
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.status, "completed")

    def test_title_is_read_only(self):
        original_title = self.order.title
        serializer = OrderDetailSerializer(
            instance=self.order,
            data={"title": "Overwritten Title"},
            partial=True,
        )
        serializer.is_valid()
        order = serializer.save()
        self.assertEqual(order.title, original_title)


class OrderCountSerializerTests(APITestCase):
    """Tests for OrderCountSerializer"""

    def test_contains_expected_field(self):
        serializer = OrderCountSerializer({"completed_order_count": 5})
        self.assertIn("completed_order_count", serializer.data)


class OrderTotalCountSerializerTests(APITestCase):
    """Tests for OrderTotalCountSerializer"""

    def test_contains_expected_field(self):
        serializer = OrderTotalCountSerializer({"order_count": 3})
        self.assertIn("order_count", serializer.data)
