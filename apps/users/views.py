"""
USERS/VIEWS.PY — Authentication API Endpoints
===============================================
Login flow: POST /api/auth/login/ -> validate -> generate JWT -> return tokens+user

Google OAuth flow:
  React Native gets a Google ID token via expo-auth-session
  POST /api/auth/google/ {id_token} -> verify with Google's servers
  -> create/fetch user -> return OUR OWN JWT tokens (not Google's)
"""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({**tokens, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'], password=serializer.validated_data['password'])
        if not user:
            return Response({'detail': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        tokens = get_tokens_for_user(user)
        return Response({**tokens, 'user': UserSerializer(user).data})


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token_str = request.data.get('id_token')
        if not id_token_str:
            return Response({'detail': 'id_token required'}, status=400)
        try:
            idinfo = id_token.verify_oauth2_token(id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            google_id = idinfo['sub']
            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            user, created = User.objects.get_or_create(
                email=email,
                defaults={'google_id': google_id, 'first_name': first_name, 'last_name': last_name, 'is_verified': True}
            )
            if not created and not user.google_id:
                user.google_id = google_id
                user.is_verified = True
                user.save()

            tokens = get_tokens_for_user(user)
            return Response({**tokens, 'user': UserSerializer(user).data})
        except ValueError as e:
            return Response({'detail': f'Invalid token: {str(e)}'}, status=400)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        return Response({'detail': 'Logged out successfully'})
