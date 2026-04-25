from django.test import SimpleTestCase
from django.urls import resolve, reverse

from reviews.api.views import ReviewDetailView, ReviewListCreateView


class ReviewUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_reviews_list_url_resolves(self):
        url = reverse("reviews-list")
        self.assertEqual(resolve(url).func.view_class, ReviewListCreateView)

    def test_review_detail_url_resolves(self):
        url = reverse("review-detail", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, ReviewDetailView)
