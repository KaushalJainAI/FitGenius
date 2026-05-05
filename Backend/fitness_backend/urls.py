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
    LogoutView, ChangePasswordView,
)
from profiles.views import HealthProfileViewSet, DailyCheckInViewSet
from recommendations.views import RecommendationViewSet

router = DefaultRouter()
router.register(r'profiles', HealthProfileViewSet, basename='profiles')
router.register(r'checkins', DailyCheckInViewSet, basename='checkins')
router.register(r'recommendations', RecommendationViewSet, basename='recommendations')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Health check
    path('api/health/', health_check, name='health-check'),

    # Main API endpoints
    path('api/', include(router.urls)),

    # Authentication endpoints
    path('api/auth/register/', UserRegistrationView.as_view(), name='register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('api/auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
