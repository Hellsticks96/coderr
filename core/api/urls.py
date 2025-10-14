from django.urls import path
from .views import StatsView

urlpatterns = [
    path('base-info/', StatsView.as_view(), name='base-info-list'),
]