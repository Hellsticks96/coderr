from django.db import models
from django.utils import timezone
from user_auth_app.models import User

class Package(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='packages', null=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='package_images/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class Detail(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.FloatField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)
