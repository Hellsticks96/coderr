from rest_framework import status
from rest_framework.test import APITestCase

from orders.models import Order
from tests.utils import create_test_order, create_test_package, create_test_user


class OrderListViewGetTests(APITestCase):
    """Tests for GET /api/orders/"""

    def setUp(self):
        self.base_url = "/api/orders/"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.order = create_test_order(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_customer_list_returns_200(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_business_list_returns_200(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_sees_only_their_orders(self):
        other_customer = create_test_user("customer", "buyer_2")
        create_test_order(other_customer, self.business_user)
        response = self.client.get(self.base_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["customer_user"], self.customer_user.pk)

    def test_business_sees_only_their_orders(self):
        other_business = create_test_user("business", "seller_2")
        create_test_order(self.customer_user, other_business)
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(self.base_url)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["business_user"], self.business_user.pk)

    def test_list_contains_expected_fields(self):
        response = self.client.get(self.base_url)
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
        self.assertEqual(set(response.data[0].keys()), expected_fields)


class OrderListViewPostTests(APITestCase):
    """Tests for POST /api/orders/"""

    def setUp(self):
        self.base_url = "/api/orders/"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.package = create_test_package(self.business_user)
        self.detail = self.package.details.first()
        self.valid_payload = {"offer_detail_id": self.detail.pk}
        self.client.force_authenticate(user=self.customer_user)

    def test_customer_can_create_order_returns_201(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_business_user_cannot_create_order_returns_403(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_response_contains_expected_fields(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
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
        self.assertEqual(set(response.data.keys()), expected_fields)

    def test_create_copies_detail_fields_to_order(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.data["title"], self.detail.title)
        self.assertEqual(response.data["price"], self.detail.price)
        self.assertEqual(response.data["offer_type"], self.detail.offer_type)

    def test_create_assigns_correct_users(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.data["customer_user"], self.customer_user.pk)
        self.assertEqual(response.data["business_user"], self.business_user.pk)

    def test_create_sets_status_to_in_progress(self):
        response = self.client.post(self.base_url, self.valid_payload, format="json")
        self.assertEqual(response.data["status"], "in_progress")

    def test_create_missing_offer_detail_id_returns_400(self):
        response = self.client.post(self.base_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_nonexistent_offer_detail_returns_404(self):
        response = self.client.post(
            self.base_url, {"offer_detail_id": 99999}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderDetailViewGetTests(APITestCase):
    """Tests for GET /api/orders/<pk>/

    Not explicitly in the spec, but implemented as a side effect of DRF's
    RetrieveUpdateDestroyAPIView which backs the PATCH and DELETE endpoints.
    """

    def setUp(self):
        self.base_url = "/api/orders"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.order = create_test_order(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.customer_user)

    def test_retrieve_as_customer_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_as_business_returns_200(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.get(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_order_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_order_contains_expected_fields(self):
        response = self.client.get(f"{self.base_url}/{self.order.pk}/")
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
        self.assertEqual(set(response.data.keys()), expected_fields)


class OrderDetailViewPatchTests(APITestCase):
    """Tests for PATCH /api/orders/<pk>/"""

    def setUp(self):
        self.base_url = "/api/orders"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.order = create_test_order(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.business_user)

    def test_business_user_can_update_status_returns_200(self):
        response = self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_update_order_returns_403(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_status_to_completed_persists(self):
        self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "completed"},
            format="json",
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "completed")

    def test_update_status_to_cancelled_persists(self):
        self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "cancelled"},
            format="json",
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")

    def test_update_nonexistent_order_returns_404(self):
        response = self.client.patch(
            f"{self.base_url}/99999/",
            {"status": "completed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_response_contains_expected_fields(self):
        response = self.client.patch(
            f"{self.base_url}/{self.order.pk}/",
            {"status": "completed"},
            format="json",
        )
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
        self.assertEqual(set(response.data.keys()), expected_fields)


class OrderDetailViewDeleteTests(APITestCase):
    """Tests for DELETE /api/orders/<pk>/"""

    def setUp(self):
        self.base_url = "/api/orders"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        self.admin_user = create_test_user("customer", "admin_1")
        self.admin_user.is_staff = True
        self.admin_user.save()
        self.order = create_test_order(self.customer_user, self.business_user)
        self.client.force_authenticate(user=self.admin_user)

    def test_admin_can_delete_order_returns_204(self):
        response = self.client.delete(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_delete_removes_from_db(self):
        pk = self.order.pk
        self.client.delete(f"{self.base_url}/{pk}/")
        self.assertFalse(Order.objects.filter(pk=pk).exists())

    def test_business_user_cannot_delete_returns_403(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.delete(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_delete_returns_403(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.delete(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.delete(f"{self.base_url}/{self.order.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_nonexistent_order_returns_404(self):
        response = self.client.delete(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CompletedOrderCountViewTests(APITestCase):
    """Tests for GET /api/completed-order-count/<pk>/"""

    def setUp(self):
        self.base_url = "/api/completed-order-count"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        create_test_order(self.customer_user, self.business_user, status="completed")
        create_test_order(self.customer_user, self.business_user, status="completed")
        create_test_order(self.customer_user, self.business_user, status="in_progress")
        self.client.force_authenticate(user=self.customer_user)

    def test_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_correct_completed_count(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.data["completed_order_count"], 2)

    def test_returns_zero_when_no_completed_orders(self):
        other_business = create_test_user("business", "seller_2")
        response = self.client.get(f"{self.base_url}/{other_business.pk}/")
        self.assertEqual(response.data["completed_order_count"], 0)

    def test_response_contains_expected_field(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertIn("completed_order_count", response.data)


class OrderInProgressViewTests(APITestCase):
    """Tests for GET /api/order-count/<pk>/"""

    def setUp(self):
        self.base_url = "/api/order-count"
        self.customer_user = create_test_user("customer", "buyer_1")
        self.business_user = create_test_user("business", "seller_1")
        create_test_order(self.customer_user, self.business_user, status="in_progress")
        create_test_order(self.customer_user, self.business_user, status="in_progress")
        create_test_order(self.customer_user, self.business_user, status="completed")
        self.client.force_authenticate(user=self.customer_user)

    def test_returns_200(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_nonexistent_user_returns_404(self):
        response = self.client.get(f"{self.base_url}/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_correct_in_progress_count(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertEqual(response.data["order_count"], 2)

    def test_returns_zero_when_no_in_progress_orders(self):
        other_business = create_test_user("business", "seller_2")
        response = self.client.get(f"{self.base_url}/{other_business.pk}/")
        self.assertEqual(response.data["order_count"], 0)

    def test_response_contains_expected_field(self):
        response = self.client.get(f"{self.base_url}/{self.business_user.pk}/")
        self.assertIn("order_count", response.data)
