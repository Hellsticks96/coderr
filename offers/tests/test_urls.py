from django.test import SimpleTestCase
from django.urls import resolve, reverse

from offers.api.views import (
    OfferDetailRetrieveView,
    OfferListCreateView,
    OfferRetrieveUpdateDeleteView,
)


class OfferUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_offers_list_url_resolves(self):
        url = reverse("offers-list")
        self.assertEqual(resolve(url).func.view_class, OfferListCreateView)

    def test_offers_detail_url_resolves(self):
        url = "/api/offers/1/"
        self.assertEqual(resolve(url).func.view_class, OfferRetrieveUpdateDeleteView)

    def test_offerdetails_url_resolves(self):
        url = "/api/offerdetails/1/"
        self.assertEqual(resolve(url).func.view_class, OfferDetailRetrieveView)
