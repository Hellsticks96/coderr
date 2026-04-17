from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .permissions import IsAdminUser, IsBusinessUser, IsCustomerUser
from .serializers import (
    OrderCountSerializer,
    OrderCreateSerializer,
    OrderDetailSerializer,
    OrderSerializer,
    OrderTotalCountSerializer,
)


class OrderListCreateView(generics.ListCreateAPIView):
    """
    Handles listing orders for the authenticated user and creating new orders.

    Customers see only their own orders as buyers.
    Business users see orders assigned to them as sellers.
    """

    queryset = Order.objects.all().select_related(
        'customer_user', 'business_user', 'detail'
    )

    def get_serializer_class(self):
        """
        Returns serializer based on request method.

        Returns:
            Serializer class for listing or creating orders.
        """
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Filters orders based on the authenticated user's role.

        Returns:
            QuerySet: Filtered orders for customer or business users.
        """
        user = self.request.user

        if user.type == "customer":
            return self.queryset.filter(customer_user=user)
        elif user.type == "business":
            return self.queryset.filter(business_user=user)

        return Order.objects.none()

    def get_permissions(self):
        """
        Assigns permissions based on request method.

        Returns:
            List of permission instances.
        """
        if self.request.method == 'POST':
            return [IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """
        Saves a new order instance.

        Args:
            serializer (OrderCreateSerializer): Validated serializer.
        """
        serializer.save()


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single order instance.

    PATCH is restricted to business users responsible for order fulfillment.
    DELETE is restricted to admin users (staff) to ensure order history integrity.

    Order deletion is intentionally limited to admins to preserve transactional
    history for auditing, dispute resolution, and platform-level record keeping.
    """

    queryset = Order.objects.all().select_related(
        'customer_user', 'business_user', 'detail'
    )
    serializer_class = OrderDetailSerializer

    def get_permissions(self):
        """
        Returns permissions depending on request method.
        """
        if self.request.method == 'PATCH':
            return [IsBusinessUser()]
        elif self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]


class CompletedOrderCountView(APIView):
    """
    Returns the number of completed orders for a given business user.

    This endpoint aggregates orders where:
    - business_user matches the provided user ID
    - status is 'completed'

    Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        User = get_user_model()
        business_user = get_object_or_404(User, id=pk)

        completed_count = Order.objects.filter(
            business_user=business_user,
            status='completed'
        ).count()

        serializer = OrderCountSerializer(
            {'completed_order_count': completed_count}
        )

        return Response(serializer.data)


class OrderInProgressView(APIView):
    """
    Returns the number of in-progress orders for a given business user.

    This endpoint aggregates orders where:
    - business_user matches the provided user ID
    - status is 'in_progress'

    Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        User = get_user_model()
        business_user = get_object_or_404(User, id=pk)

        total_count = Order.objects.filter(
            business_user=business_user,
            status='in_progress'
        ).count()

        serializer = OrderTotalCountSerializer(
            {'order_count': total_count}
        )

        return Response(serializer.data)