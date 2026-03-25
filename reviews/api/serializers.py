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
        read_only_fields = ["business_user", "reviewer", "created_at", "updated_at"]

        def validate(self, data):
            details = data.get('details')
    
            if details is not None:
                for detail in details:
                    required_fields = [
                        "business_user",
                        "rating",
                        "description"
                    ]
                    for field in required_fields:
                        if field not in detail:
                            raise serializers.ValidationError({
                                'details': f"Field '{field}' is required for each detail."
                            })
            return data
