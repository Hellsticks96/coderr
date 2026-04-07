from rest_framework import generics, permissions
from .serializers import UserProfileSerializer
from user_auth_app.models import User
from .permissions import IsOwner

#Get all Profiles
class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

#Get all customer type users
class CustomerListView(generics.ListAPIView):
    queryset = User.objects.filter(type='customer')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

#Get all business type users
class BusinessListView(generics.ListAPIView):
    queryset = User.objects.filter(type='business')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]