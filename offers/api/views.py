from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters, generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from offers.models import Detail, Package

from .permissions import IsOwner
from .serializers import (
    DetailSerializer,
    PackageCreateResponseSerializer,
    PackageCreateSerializer,
    PackageSerializer,
)


class OfferPagination(PageNumberPagination):
    """Handles pagination for offers list endpoint."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class OfferFilter(FilterSet):
    """Provides filtering options for offers based on creator, price, and delivery time."""
    creator_id = NumberFilter(field_name='user_id', lookup_expr='exact')
    min_price = NumberFilter(field_name='details__price', lookup_expr='gte')
    max_delivery_time = NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte')

    class Meta:
        model = Package
        fields = ['creator_id', 'min_price', 'max_delivery_time']


class OfferListCreateView(generics.GenericAPIView):
    """
    Handles listing all offers and creating new offer packages.

    - GET: Returns a paginated and filterable list of offers.
    - POST: Allows authenticated business users to create a new offer package.
    """
    queryset = Package.objects.all().order_by('id')
    pagination_class = OfferPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        """Returns the appropriate serializer depending on request method."""
        if self.request.method == 'POST':
            return PackageCreateSerializer
        return PackageSerializer

    def get_permissions(self):
        """Restricts POST requests to authenticated users only."""
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return []

    def get_queryset(self):
        """Annotates queryset with minimum price and delivery time for sorting/filtering."""
        return (
            Package.objects.all()
            .annotate(
                min_price=Min('details__price'),
                min_delivery_time=Min('details__delivery_time_in_days'),
            )
            .order_by('id')
        )

    def get(self, request):
        """Returns a paginated list of filtered offers."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """Creates a new offer package for business users."""
        try:
            profile = request.user
        except Exception:
            return Response({"detail": "User profile not found."}, status=status.HTTP_403_FORBIDDEN)

        if profile.type != 'business':
            return Response({"detail": "Only business users can create offers."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        full_serializer = PackageCreateResponseSerializer(serializer.instance)
        return Response(full_serializer.data, status=status.HTTP_201_CREATED)


class OfferRetrieveUpdateDeleteView(generics.GenericAPIView):
    """
    Handles retrieving, updating, and deleting a single offer package.

    - GET: Retrieve offer details
    - PATCH: Update offer (only owner)
    - DELETE: Delete offer (only owner)
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self):
        """Fetches the offer package by primary key."""
        return generics.get_object_or_404(Package, pk=self.kwargs['pk'])

    def get(self, request, pk):
        """Returns details of a specific offer."""
        obj = self.get_object()
        serializer = self.get_serializer(obj, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        """Partially updates an offer package including nested details."""
        obj = self.get_object()
        self.check_object_permissions(request, obj)

        serializer = PackageCreateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        full_serializer = PackageSerializer(obj, context={'request': request})
        return Response(full_serializer.data)

    def delete(self, request, pk):
        """Deletes an offer package."""
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    Retrieves a single offer detail entry.
    """
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer
    permission_classes = [permissions.IsAuthenticated]