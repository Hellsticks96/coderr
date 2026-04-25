from django.test import SimpleTestCase
from django.urls import resolve, reverse

from core.api.views import StatsView


class CoreUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_base_info_url_resolves(self):
        url = reverse("base-info-list")
        self.assertEqual(resolve(url).func.view_class, StatsView)
