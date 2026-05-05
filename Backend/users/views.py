from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)


# ==================== CUSTOM THROTTLES ====================

class LoginRateThrottle(AnonRateThrottle):
    """Throttle for login attempts — prevents brute force attacks."""
    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """Throttle for registration — prevents mass account creation."""
    scope = 'register'


# ==================== AUTH VIEWS ====================

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user.
    Rate limited: 3 attempts per minute.
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully. Please login to continue.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change password for authenticated users."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError

        if not old_password or not new_password:
            return Response(
                {'detail': 'Both old and new passwords are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(old_password):
            return Response(
                {'detail': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except DjangoValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password updated successfully.'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view that sets HttpOnly cookies.
    Rate limited: 5 attempts per minute.
    """
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            refresh_token = response.data['refresh']

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=3600,
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=3600 * 24 * 7,
            )
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """Custom Token Refresh View — reads refresh token from cookie if not in body."""

    def post(self, request, *args, **kwargs):
        refresh_from_cookie = request.COOKIES.get('refresh_token')
        if not request.data.get('refresh') and refresh_from_cookie:
            request.data['refresh'] = refresh_from_cookie

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access_token = response.data['access']
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Lax',
                max_age=3600,
            )
            if 'refresh' in response.data:
                refresh_token = response.data['refresh']
                response.set_cookie(
                    key='refresh_token',
                    value=refresh_token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite='Lax',
                    max_age=3600 * 24 * 7,
                )
        return response


class LogoutView(APIView):
    """
    Logout: blacklist refresh token and clear cookies.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        response = Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
