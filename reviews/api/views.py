from rest_framework import generics, permissions, serializers
from reviews.models import Review
from .serializers import ReviewSerializer
from orders.api.permissions import IsCustomerUser
from .permissions import IsReviewer
from rest_framework.filters import OrderingFilter

#Get all reviews or post a single new review.
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCustomerUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Review.objects.select_related("reviewer", "business_user")
        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)

        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset
    
    def perform_create(self, serializer):
        business_user_id = self.request.data.get("business_user")
        if not business_user_id:
            raise serializers.ValidationError({
                "business_user": "This field is required."
            })

#Get details of a single review.    
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewer]
