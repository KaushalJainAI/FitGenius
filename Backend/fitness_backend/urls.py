from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({'status': 'healthy', 'service': 'fitgenius-backend'})


from users.views import (
    UserRegistrationView, UserProfileView,
    CustomTokenObtainPairView, CustomTokenRefreshView,
    LogoutView, ChangePasswordView, ChangePasswordOTPRequestView,
    PasswordResetRequestView, PasswordResetVerifyView, PasswordResetConfirmView,
    UserPreferenceView, NotificationPreferenceView, SecurityStatusView,
    TwoFactorStatusView, TwoFactorEnableView, TwoFactorDisableView, AccountDeleteView,
)
from profiles.views import HealthProfileViewSet, DailyCheckInViewSet
from recommendations.views import RecommendationViewSet, PreferenceMemoryViewSet
from billing.views import SubscriptionView, StartProTrialView, CancelSubscriptionView, BillingPlansView
from fitness_backend.dashboard import DashboardSummaryView, AnalyticsSummaryView

router = DefaultRouter()
router.register(r'profiles', HealthProfileViewSet, basename='profiles')
router.register(r'checkins', DailyCheckInViewSet, basename='checkins')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')
router.register(r'preferences/memory', PreferenceMemoryViewSet, basename='preference-memory')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check
    path('api/health/', health_check, name='health-check'),
    path('api/dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('api/analytics/summary/', AnalyticsSummaryView.as_view(), name='analytics-summary'),

    # Main API endpoints
    path('api/', include(router.urls)),
    path('api/chat/', include('chat.urls')),

    # Authentication endpoints
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/auth/security/', SecurityStatusView.as_view(), name='auth-security'),
    path('api/auth/2fa/status/', TwoFactorStatusView.as_view(), name='auth-2fa-status'),
    path('api/auth/2fa/enable/', TwoFactorEnableView.as_view(), name='auth-2fa-enable'),
    path('api/auth/2fa/disable/', TwoFactorDisableView.as_view(), name='auth-2fa-disable'),
    path('api/auth/account/', AccountDeleteView.as_view(), name='auth-account-delete'),
    path('api/auth/change-password/request-otp/', ChangePasswordOTPRequestView.as_view(), name='change-password-request-otp'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('api/auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('api/auth/password-reset/verify/', PasswordResetVerifyView.as_view(), name='password-reset-verify'),
    path('api/auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('api/user/preferences/', UserPreferenceView.as_view(), name='user-preferences'),
    path('api/notifications/preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),

    # Billing endpoints (manual validation / free trial, no payment gateway)
    path('api/billing/subscription/', SubscriptionView.as_view(), name='billing-subscription'),
    path('api/billing/plans/', BillingPlansView.as_view(), name='billing-plans'),
    path('api/billing/start-pro-trial/', StartProTrialView.as_view(), name='billing-start-pro-trial'),
    path('api/billing/cancel/', CancelSubscriptionView.as_view(), name='billing-cancel'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
