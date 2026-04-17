from django.urls import path

from .views import BusinessListView, CustomerListView, ProfileView

urlpatterns = [
    path('profile/<int:pk>/', ProfileView.as_view(), name="profiles-detail"),
    path('profiles/customer/', CustomerListView.as_view(), name='customers-list'),
    path('profiles/business/', BusinessListView.as_view(), name='business-list')
]