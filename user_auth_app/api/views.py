from rest_framework import generics, permissions
from user_auth_app.models import User
from .serializers import RegistrationSerializer, UserProfileSerializer, CustomAuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from profiles.api.permissions import IsOwner

class UserProfileList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registers a new user account.

        Creates a User instance via serializer validation,
        generates an auth token, and returns authentication
        details required for immediate login.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            token, _ = Token.objects.get_or_create(user=saved_account)

            data = {
                "token": token.key,
                "username": saved_account.username,
                "email": saved_account.email,
                "user_id": saved_account.pk
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        """
        Authenticates a user using DRF token authentication.
        
        Validates credentials and returns an auth token along
        with basic user information.
        """
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'user_id': user.id
        })