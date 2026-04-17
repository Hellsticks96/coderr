from rest_framework import serializers
from reviews.models import Review

#Serializer for reviews. Sorting parameters and declare read_only fields.
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["reviewer", "created_at", "updated_at"]

    def validate(self, data):
        """
        Prevents duplicate reviews from the same reviewer for the same business user.
        """
        request = self.context['request']
        reviewer = request.user
        business_user = data.get('business_user')

        if Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this business."
            )

        return data
