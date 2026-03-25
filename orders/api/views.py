from rest_framework import generics, permissions
from orders.models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderDetailSerializer, OrderCountSerializer, OrderTotalCountSerializer
from .permissions import IsCustomerUser, IsBusinessUser, IsAdminUser
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView

#View for get (list) and post of orders.
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

#View for single order details.
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all().select_related('customer_user', 'business_user', 'detail')
    serializer_class = OrderDetailSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsBusinessUser()]
        elif self.request.method == 'DELETE':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

#View for completed order count.

class CompletedOrderCountView(APIView):
    permission_classes= [permissions.IsAuthenticated]

    def get(self, request, pk):
        User = get_user_model()
        business_user = get_object_or_404(User, id=pk)
        completed_count = Order.objects.filter(
            business_user = business_user,
            status='completed'
        ).count()

        serializer = OrderCountSerializer({'completed_order_count': completed_count})
        return Response(serializer.data)
    
#View for total order count.

class OrderInProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        User = get_user_model()
        business_user = get_object_or_404(User, id=pk)
        total_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        serializer = OrderTotalCountSerializer({'order_count': total_count})
        return Response(serializer.data)