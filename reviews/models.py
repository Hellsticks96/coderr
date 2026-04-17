from django.db import models
from django.utils import timezone

from user_auth_app.models import User


class Review(models.Model):
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_received"
    )
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews_written"
    )
    rating = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "business_user"],
                name="unique_review_per_user_business",
            )
        ]

    def __str__(self):
        return f"Review {self.id} by {self.reviewer_id} for {self.business_user_id} ({self.rating}★)"
