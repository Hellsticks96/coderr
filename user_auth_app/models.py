from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )
    file = models.ImageField(upload_to="profile_pictures/", null=True, blank=True)
    location = models.CharField(max_length=255, default="")
    tel = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    working_hours = models.CharField(max_length=100, blank=True, default="")
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True)
    created_at = models.DateTimeField(default=timezone.now)