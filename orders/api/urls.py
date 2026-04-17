from django.urls import path

from .views import (
    CompletedOrderCountView,
    OrderDetailView,
    OrderInProgressView,
    OrderListCreateView,
)

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('completed-order-count/<int:pk>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('order-count/<int:pk>/', OrderInProgressView.as_view(), name="total-order-count")
]
