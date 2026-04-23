from django.test import SimpleTestCase
from django.urls import resolve, reverse

from profiles.api.views import BusinessListView, CustomerListView, ProfileView


class ProfileUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_profile_detail_url_resolves(self):
        url = reverse("profiles-detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, ProfileView)

    def test_customer_list_url_resolves(self):
        url = reverse("customers-list")
        self.assertEqual(resolve(url).func.view_class, CustomerListView)

    def test_business_list_url_resolves(self):
        url = reverse("business-list")
        self.assertEqual(resolve(url).func.view_class, BusinessListView)
