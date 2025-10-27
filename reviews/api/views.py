from rest_framework import generics, permissions
from reviews.models import Review
from .serializers import ReviewSerializer
from orders.api.permissions import IsCustomerUser
from .permissions import IsReviewer

#Get all reviews or post a single new review.
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.select_related("reviewer", "business_user")
        business_user_id = self.request.query_params.get("business_user")
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        return queryset

#Get details of a single review.    
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewer]
