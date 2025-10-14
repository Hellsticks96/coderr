from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    file = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    tel = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True)
    created_at = models.DateTimeField(default=timezone.now)