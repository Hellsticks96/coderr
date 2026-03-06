from django.urls import path
from .views import OfferListCreateView, OfferRetrieveUpdateDeleteView, OfferDetailRetrieveView

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offers-list'),
    path('offers/<int:pk>/', OfferRetrieveUpdateDeleteView.as_view(), name='offers-detail'),
    path('offerdetails/<int:pk>/', OfferDetailRetrieveView.as_view(), name='offers-detail'),
]
