from rest_framework import generics, permissions
from user_auth_app.models import UserProfile
from .serializers import RegistrationSerializer, UserProfileSerializer, CustomAuthTokenSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from profiles.api.permissions import IsOwner

class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            saved_account = serializer.save()
            profile = UserProfile.objects.get(user=saved_account)
            token, _ = Token.objects.get_or_create(user=saved_account)

            data = {
                "user": saved_account.pk,
                "username": saved_account.username,
                "first_name": saved_account.first_name,
                "last_name": saved_account.last_name,
                "email": saved_account.email,
                "file": profile.file.url if profile.file else None,
                "location": profile.location,
                "tel": profile.tel,
                "description": profile.description,
                "working_hours": profile.working_hours,
                "type": profile.type,
                "created_at": profile.created_at,
                "token": token.key
            }
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomAuthTokenSerializer(data=request.data)
        data = {}
        statuscode = status.HTTP_200_OK
        if serializer.is_valid():
            user = serializer.validated_data['user']
            profile = UserProfile.objects.get(user=user)
            token, _ = Token.objects.get_or_create(user=user)

            fullname = f"{user.first_name} {user.last_name}".strip()

            data = {
                'token': token.key,
                'fullname': fullname,
                'email': user.email,
                'user_id': user.pk
            }
        else:
            data = serializer.errors
            statuscode = status.HTTP_400_BAD_REQUEST
        return Response(data, status=statuscode)