from django.test import SimpleTestCase
from django.urls import resolve, reverse

from orders.api.views import (
    CompletedOrderCountView,
    OrderDetailView,
    OrderInProgressView,
    OrderListCreateView,
)


class OrderUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_orders_list_url_resolves(self):
        url = reverse("orders-list")
        self.assertEqual(resolve(url).func.view_class, OrderListCreateView)

    def test_order_detail_url_resolves(self):
        url = reverse("order-detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, OrderDetailView)

    def test_completed_order_count_url_resolves(self):
        url = reverse("completed-order-count", args=[1])
        self.assertEqual(resolve(url).func.view_class, CompletedOrderCountView)

    def test_order_in_progress_url_resolves(self):
        url = reverse("total-order-count", args=[1])
        self.assertEqual(resolve(url).func.view_class, OrderInProgressView)
