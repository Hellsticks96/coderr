from django.urls import path

from .views import (
    OfferDetailRetrieveView,
    OfferListCreateView,
    OfferRetrieveUpdateDeleteView,
)

urlpatterns = [
    path("offers/", OfferListCreateView.as_view(), name="offers-list"),
    path(
        "offers/<int:pk>/",
        OfferRetrieveUpdateDeleteView.as_view(),
        name="offer-detail",
    ),
    path(
        "offerdetails/<int:pk>/",
        OfferDetailRetrieveView.as_view(),
        name="offers-detail",
    ),
]
