from rest_framework import generics, permissions
from .serializers import UserProfileSerializer
from user_auth_app.models import UserProfile
from .permissions import IsOwner

#Get all Profiles
class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

#Get all customer type users
class CustomerListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type='customer')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

#Get all business type users
class BusinessListView(generics.ListAPIView):
    queryset = UserProfile.objects.filter(type='business')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]