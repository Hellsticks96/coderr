from rest_framework import generics, permissions, status
from offers.models import Package, Detail
from .serializers import PackageSerializer, PackageCreateSerializer, DetailSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .permissions import IsOwner

#set pagination
class OfferPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

#Get and post new offer-set
class OfferListCreateView(generics.GenericAPIView):
    queryset = Package.objects.all().order_by('id')
    pagination_class = OfferPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PackageCreateSerializer
        return PackageSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return []

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        try:
            profile = request.user.profile
        except Exception:
            return Response({"detail": "User profile not found."}, status=status.HTTP_403_FORBIDDEN)

        if profile.type != 'business':
            return Response({"detail": "Only business users can create offers."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        full_serializer = PackageSerializer(serializer.instance, context={'request': request})
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
