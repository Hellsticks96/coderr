from django.urls import path
from .views import ProfileDetailView, CustomerListView, BusinessListView


urlpatterns = [
    path('profiles/<int:pk>', ProfileDetailView.as_view(), name="profiles-detail"),
    path('profiles/customer/', CustomerListView.as_view(), name='customers-list'),
    path('profiles/business/', BusinessListView.as_view(), name='business-list')
]