from rest_framework import generics, permissions
from orders.models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderDetailSerializer
from .permissions import IsCustomerUser, IsBusinessUser, IsAdminUser


class OrderListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all().select_related('customer_user', 'business_user', 'detail')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "profile"):
            if user.profile.type == "customer":
                return self.queryset.filter(customer_user=user)
            elif user.profile.type == "business":
                return self.queryset.filter(business_user=user)
        return Order.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().select_related('customer_user', 'business_user', 'detail')
    serializer_class = OrderDetailSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsBusinessUser()]
        elif self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]