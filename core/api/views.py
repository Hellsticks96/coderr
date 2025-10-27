from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Avg, Count
from reviews.models import Review
from user_auth_app.models import UserProfile
from offers.models import Package


#This view is for the stats endpoint of the API:
#Gets the data e.g. ALL ratings, calulates the average and displays it.
#GET-Only!
class StatsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        review_data = Review.objects.aggregate(
            average_rating=Avg('rating'),
            review_count=Count('id')
        )
        business_profile_count = UserProfile.objects.filter(type='business').count()
        offer_count = Package.objects.count()

        data = {
            "review_count": review_data["review_count"] or 0,
            "average_rating": round(review_data["average_rating"], 1) if review_data["average_rating"] else 0,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data)
