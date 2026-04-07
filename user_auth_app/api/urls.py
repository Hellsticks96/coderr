from django.urls import path
from .views import UserProfileList, UserProfileDetail, RegistrationView, CustomLoginView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('profiles/', UserProfileList.as_view(), name='User-list'),
    path('profiles/<int:pk>/', UserProfileDetail.as_view(), name='User-detail'),
    path('registration/', RegistrationView.as_view(), name='registration-detail'),
    path('login/', CustomLoginView.as_view(), name="login-detail")
]