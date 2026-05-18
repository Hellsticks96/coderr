"""
URL configuration for coderr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from pathlib import Path

from django.contrib import admin
from django.http import FileResponse, JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "coderr-frontend"


def serve_html(filename):
    def view(request):
        return FileResponse(
            open(FRONTEND_DIR / filename, "rb"), content_type="text/html; charset=utf-8"
        )

    return view


def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/", include("user_auth_app.api.urls")),
    path("api/", include("profiles.api.urls")),
    path("api/", include("offers.api.urls")),
    path("api/", include("orders.api.urls")),
    path("api/", include("reviews.api.urls")),
    path("api/", include("core.api.urls")),
    path("health/", health_check, name="health"),
    path("login/", serve_html("login.html")),
    path("register/", serve_html("registration.html")),
    path("offers/", serve_html("offer_list.html")),
    path("offer/", serve_html("offer.html")),
    path("profile/", serve_html("own_profile.html")),
    path("business-profile/", serve_html("business_profile.html")),
    path("customer-profile/", serve_html("customer_profile.html")),
    path("imprint/", serve_html("imprint.html")),
    path("privacy-policy/", serve_html("privacy_policy.html")),
]
