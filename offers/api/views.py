from rest_framework import generics, permissions, status
from offers.models import Package, Detail
from .serializers import PackageSerializer, PackageCreateSerializer, DetailSerializer, PackageCreateResponseSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .permissions import IsOwner
from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters


#set pagination
class OfferPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

#Query filter class.
class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name='user_id', lookup_expr='exact')
    min_price = NumberFilter(field_name='details__price', lookup_expr='gte')
    max_delivery_time = NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte')

    class Meta:
        model = Package
        fields = ['creator_id', 'min_price', 'max_delivery_time']

#Get and post new offer-set
class OfferListCreateView(generics.GenericAPIView):
    queryset = Package.objects.all().order_by('id')
    pagination_class = OfferPagination

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PackageCreateSerializer
        return PackageSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return []
    
    def get_queryset(self):
        return (
            Package.objects.all()
            .annotate(
                min_price=Min('details__price'),
                min_delivery_time=Min('details__delivery_time_in_days'),
            )
            .order_by('id')
        )


    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
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

#For detail endpoint. Update or delete an offer-package.
class OfferRetrieveUpdateDeleteView(generics.GenericAPIView):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_object(self):
        return generics.get_object_or_404(Package, pk=self.kwargs['pk'])

    def get(self, request, pk):
        obj = self.get_object()
        serializer = self.get_serializer(obj, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        serializer = PackageCreateSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        full_serializer = PackageSerializer(obj, context={'request': request})
        return Response(full_serializer.data)

    def delete(self, request, pk):
        obj = self.get_object()
        self.check_object_permissions(request, obj)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#Get detail list of a specific offer.   
class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = Detail.objects.all()
    serializer_class = DetailSerializer
    permission_classes = [permissions.IsAuthenticated]

