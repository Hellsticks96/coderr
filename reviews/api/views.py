from rest_framework import filters, generics, permissions, serializers

from orders.api.permissions import IsCustomerUser
from reviews.models import Review

from .permissions import IsReviewer
from .serializers import ReviewSerializer


# Get all reviews or post a single new review.
class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List reviews or create a new review.

    Supports filtering by:
    - business_user_id
    - reviewer_id

    Supports ordering by:
    - rating
    - updated_at

    On creation:
    - reviewer is automatically set from authenticated user
    - business_user is taken from request body
    """

    serializer_class = ReviewSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["rating", "updated_at"]
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
        """
        Creates a review and assigns:
        - reviewer from request.user
        - business_user from request data
        """
        business_user_id = self.request.data.get("business_user")
        if not business_user_id:
            raise serializers.ValidationError(
                {"business_user": "This field is required."}
            )
        serializer.save(reviewer=self.request.user, business_user_id=business_user_id)


# Get details of a single review.
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a review.

    Update/delete is restricted by custom IsReviewer permission.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsReviewer]
