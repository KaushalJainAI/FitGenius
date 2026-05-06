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
    UserPreferenceSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    OTPVerifySerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
)
from .models import PasswordResetOTP, UserPreference
import random
import threading
import uuid
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError, ProgrammingError


DEFAULT_PREFERENCES = {
    'theme': 'dark',
    'measurement_system': 'metric',
    'push_enabled': False,
    'reminder_time': '07:00',
    'weekly_email_enabled': True,
    'two_factor_enabled': False,
}


def preference_payload(preferences=None, overrides=None):
    if preferences is not None:
        data = UserPreferenceSerializer(preferences).data
    else:
        data = {
            **DEFAULT_PREFERENCES,
            'notification_settings': {
                'pushEnabled': DEFAULT_PREFERENCES['push_enabled'],
                'reminderTime': DEFAULT_PREFERENCES['reminder_time'],
                'weeklyEmailEnabled': DEFAULT_PREFERENCES['weekly_email_enabled'],
            },
            'created_at': None,
            'updated_at': None,
        }
    if overrides:
        data.update(overrides)
        data['notification_settings'] = {
            'pushEnabled': data.get('push_enabled', False),
            'reminderTime': data.get('reminder_time', '07:00'),
            'weeklyEmailEnabled': data.get('weekly_email_enabled', True),
        }
    return data


def safe_preferences_for_user(user):
    try:
        return UserPreference.get_or_create_for_user(user)
    except (OperationalError, ProgrammingError):
        return None


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
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'detail': 'Invalid registration data.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = serializer.save()
            return Response({
                'success': True,
                'user': UserSerializer(user).data,
                'message': 'User registered successfully. Please login to continue.'
            }, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response(
                {'success': False, 'detail': 'Unable to register user.', 'errors': getattr(exc, 'detail', str(exc))},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPreferenceView(APIView):
    """Read and update app, measurement, notification, and lightweight 2FA settings."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences = safe_preferences_for_user(request.user)
        return Response(preference_payload(preferences))

    def patch(self, request):
        preferences = safe_preferences_for_user(request.user)
        if preferences is None:
            allowed = set(DEFAULT_PREFERENCES)
            return Response(preference_payload(None, {
                key: value for key, value in request.data.items() if key in allowed
            }))
        serializer = UserPreferenceSerializer(preferences, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'detail': 'Invalid preference data.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(serializer.data)


class NotificationPreferenceView(UserPreferenceView):
    """Alias endpoint for notification-focused UI."""


class SecurityStatusView(APIView):
    """Account security metadata for settings screens."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences = safe_preferences_for_user(request.user)
        return Response({
            'email': request.user.email,
            'last_login': request.user.last_login,
            'password_changed_at': request.user.updated_at,
            'two_factor_enabled': preferences.two_factor_enabled if preferences else False,
            'can_change_password': True,
            'can_delete_account': True,
        })


class TwoFactorStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences = safe_preferences_for_user(request.user)
        return Response({'two_factor_enabled': preferences.two_factor_enabled if preferences else False})


class TwoFactorEnableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = safe_preferences_for_user(request.user)
        if preferences is None:
            return Response({'success': True, 'two_factor_enabled': True, 'persisted': False})
        preferences.two_factor_enabled = True
        preferences.save(update_fields=['two_factor_enabled', 'updated_at'])
        return Response({'success': True, 'two_factor_enabled': True})


class TwoFactorDisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        preferences = safe_preferences_for_user(request.user)
        if preferences is None:
            return Response({'success': True, 'two_factor_enabled': False, 'persisted': False})
        preferences.two_factor_enabled = False
        preferences.save(update_fields=['two_factor_enabled', 'updated_at'])
        return Response({'success': True, 'two_factor_enabled': False})


class AccountDeleteView(APIView):
    """Delete the authenticated account after explicit email confirmation."""
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        confirm_email = request.data.get('confirm_email')
        if confirm_email != request.user.email:
            return Response(
                {'detail': 'confirm_email must match the authenticated user email.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.delete()
        response = Response({'success': True, 'detail': 'Account deleted.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class ChangePasswordOTPRequestView(APIView):
    """Request an OTP to change password (requires authentication)."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        user = request.user

        # Generate 6-digit OTP
        otp_code = f"{random.randint(100000, 999999)}"

        # Invalidate previous unexpired OTPs
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        expires_at = timezone.now() + timedelta(minutes=10)
        otp_record = PasswordResetOTP(user=user, expires_at=expires_at)
        otp_record.set_otp(otp_code)
        otp_record.save()

        def send_otp_email(email_kwargs):
            import logging
            logger = logging.getLogger(__name__)
            try:
                send_mail(**email_kwargs)
            except Exception as e:
                logger.error(f"Failed to send OTP email: {str(e)}")
                print(f"\n❌ EMAIL ERROR: {str(e)}\n")

        email_kwargs = {
            'subject': 'Change Password OTP - FitGenius',
            'message': f'Your OTP to change your password is: {otp_code}\n\nThis code will expire in 10 minutes.',
            'from_email': settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER,
            'recipient_list': [user.email],
            'fail_silently': False,
        }
        threading.Thread(target=send_otp_email, args=(email_kwargs,)).start()

        return Response({'detail': 'An OTP has been sent to your email.'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """Change password for authenticated users with OTP."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        otp_code = serializer.validated_data['otp_code']

        if not user.check_password(old_password):
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        try:
            otp_record = PasswordResetOTP.objects.filter(user=user, is_used=False).latest('created_at')
            if otp_record.is_expired:
                return Response({'detail': 'OTP has expired.'}, status=status.HTTP_400_BAD_REQUEST)
            if otp_record.is_locked:
                return Response({'detail': 'Too many failed attempts.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            if not otp_record.check_otp(otp_code):
                otp_record.failed_attempts += 1
                otp_record.save(update_fields=['failed_attempts'])
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            otp_record.is_used = True
            otp_record.save(update_fields=['is_used'])

        except PasswordResetOTP.DoesNotExist:
            return Response({'detail': 'No OTP requested.'}, status=status.HTTP_400_BAD_REQUEST)

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


# ==================== PASSWORD RESET VIEWS ====================

class PasswordResetRateThrottle(AnonRateThrottle):
    """Throttle for password reset - 10 attempts per day per IP."""
    scope = 'password_reset'


class PasswordResetRequestView(APIView):
    """
    Send an OTP to the user's email for password reset verification.
    Rate limited: 10 attempts per day.
    """
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = get_user_model().objects.get(email=email)

            otp_code = f"{random.randint(100000, 999999)}"
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

            PasswordResetOTP.objects.filter(
                user=user,
                expires_at__lt=timezone.now() - timedelta(hours=24)
            ).delete()

            expires_at = timezone.now() + timedelta(minutes=10)
            otp_record = PasswordResetOTP(user=user, expires_at=expires_at)
            otp_record.set_otp(otp_code)
            otp_record.save()

            def send_otp_email(email_kwargs):
                import logging
                logger = logging.getLogger(__name__)
                try:
                    send_mail(**email_kwargs)
                except Exception as e:
                    logger.error(f"Failed to send OTP email: {str(e)}")
                    print(f"\n❌ EMAIL ERROR: {str(e)}\n")

            email_kwargs = {
                'subject': 'Password Reset OTP - FitGenius',
                'message': f'Your OTP for password reset is: {otp_code}\n\nThis code will expire in 10 minutes.',
                'from_email': settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER,
                'recipient_list': [user.email],
                'fail_silently': False,
            }
            threading.Thread(target=send_otp_email, args=(email_kwargs,)).start()

        except get_user_model().DoesNotExist:
            get_user_model()().set_password('dummy_password')

        return Response(
            {'detail': 'If an account exists with this email, an OTP has been sent.'},
            status=status.HTTP_200_OK
        )

class PasswordResetVerifyView(APIView):
    """
    Verify the OTP code sent to the email (without resetting password yet).
    Rate limited: 10 attempts per day.
    """
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = get_user_model().objects.get(email=email)
            otp_record = PasswordResetOTP.objects.filter(
                user=user,
                is_used=False
            ).latest('created_at')

            if otp_record.is_expired:
                return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.is_locked:
                return Response({'detail': 'Too many failed attempts. Please request a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            if not otp_record.check_otp(otp_code):
                otp_record.failed_attempts += 1
                otp_record.save(update_fields=['failed_attempts'])
                remaining = PasswordResetOTP.MAX_FAILED_ATTEMPTS - otp_record.failed_attempts
                if remaining > 0:
                    return Response({'detail': f'Invalid OTP. {remaining} attempt(s) remaining.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'detail': 'Too many failed attempts. Please request a new OTP.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            otp_record.is_used = True
            otp_record.reset_token = str(uuid.uuid4())
            otp_record.save(update_fields=['is_used', 'reset_token'])

            return Response({
                'detail': 'OTP verified successfully. You may proceed to reset password.',
                'reset_token': otp_record.reset_token
            }, status=status.HTTP_200_OK)

        except (get_user_model().DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response({'detail': 'Invalid OTP or email.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    """
    Confirm OTP and reset the password.
    Rate limited: 10 attempts per day.
    """
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']

        try:
            user = get_user_model().objects.get(email=email)
            otp_record = PasswordResetOTP.objects.get(
                user=user,
                reset_token=reset_token,
                is_used=True
            )

            if otp_record.is_expired:
                return Response({'detail': 'Password reset session has expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            otp_record.reset_token = None
            otp_record.save()

            return Response({'detail': 'Password has been reset successfully. You can now login.'}, status=status.HTTP_200_OK)

        except (get_user_model().DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response({'detail': 'Invalid OTP or email.'}, status=status.HTTP_400_BAD_REQUEST)
