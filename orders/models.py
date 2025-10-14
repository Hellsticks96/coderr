from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_customer'
    )
    business_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_business'
    )
    detail = models.ForeignKey(
        'offers.Detail',
        on_delete=models.CASCADE,
        related_name='orders'
    )

    title = models.CharField(max_length=255)
    revisions = models.IntegerField()
    delivery_time_in_days = models.IntegerField()
    price = models.FloatField()
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=50)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.title} ({self.status})"
