from django.urls import path
from .views import OrderListCreateView, OrderDetailView, CompletedOrderCountView, TotalOrderView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('completed-order-count/<int:pk>/', CompletedOrderCountView.as_view(), name='completed-order-count'),
    path('order-count/<int:pk>/', TotalOrderView.as_view(), name="total-order-count")
]
