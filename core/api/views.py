from django.db.models import Avg, Count
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from offers.models import Package
from reviews.models import Review
from user_auth_app.models import User


class StatsView(APIView):
    """
    Returns general platform statistics such as reviews, ratings,
    business users, and offers.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """
        Retrieve aggregated statistics for the platform.

        Returns:
            Response: A JSON object containing review count, average rating,
            business profile count, and offer count.
        """
        review_data = Review.objects.aggregate(
            average_rating=Avg("rating"),
            review_count=Count("id"),
        )

        business_profile_count = User.objects.filter(type="business").count()
        offer_count = Package.objects.count()

        data = {
            "review_count": review_data["review_count"] or 0,
            "average_rating": (
                round(review_data["average_rating"], 1)
                if review_data["average_rating"]
                else 0
            ),
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data)
