from django.test import SimpleTestCase
from django.urls import resolve, reverse

from user_auth_app.api.views import (
    CustomLoginView,
    RegistrationView,
    UserProfileDetail,
    UserProfileList,
)


class UserAuthUrlTests(SimpleTestCase):
    """Tests that URLs resolve to the correct views"""

    def test_user_list_url_resolves(self):
        url = reverse("User-list")
        self.assertEqual(resolve(url).func.view_class, UserProfileList)

    def test_user_detail_url_resolves(self):
        url = reverse("User-detail", args=[1])
        self.assertEqual(resolve(url).func.view_class, UserProfileDetail)

    def test_registration_url_resolves(self):
        url = reverse("registration-detail")
        self.assertEqual(resolve(url).func.view_class, RegistrationView)

    def test_login_url_resolves(self):
        url = reverse("login-detail")
        self.assertEqual(resolve(url).func.view_class, CustomLoginView)