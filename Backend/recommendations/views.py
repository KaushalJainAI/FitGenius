import logging
from django.db.models import QuerySet
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.throttling import UserRateThrottle

from .models import Recommendation
from .serializers import RecommendationSerializer, RecommendationListSerializer
from .engine import engine
from profiles.models import HealthProfile, DailyCheckIn

logger = logging.getLogger('recommendations')


# ==================== CUSTOM THROTTLE ====================

class RecommendationRateThrottle(UserRateThrottle):
    """Rate limit recommendation generation to prevent abuse."""
    scope = 'recommendations'


# ==================== PERMISSIONS ====================

class IsOwner(IsAuthenticated):
    """Only allow users to access their own recommendations."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


# ==================== VIEWSET ====================

class RecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for workout & diet recommendations.

    - GET /api/recommendations/              → List user's recommendations (newest first)
    - GET /api/recommendations/latest/       → Most recent recommendation
    - GET /api/recommendations/history/       → All recommendations paginated
    - GET /api/recommendations/<id>/          → Specific recommendation detail
    - POST /api/recommendations/generate/     → Generate new recommendation
    - DELETE /api/recommendations/<id>/       → Delete a recommendation
    """
    queryset = Recommendation.objects.none()
    permission_classes = [IsOwner]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self) -> QuerySet[Recommendation]:
        return Recommendation.objects.filter(
            user=self.request.user
        ).select_related('user')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecommendationListSerializer
        return RecommendationSerializer

    def list(self, request, *args, **kwargs):
        """List all recommendations for the authenticated user (newest first)."""
        queryset = self.get_queryset().order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['post'], throttle_classes=[RecommendationRateThrottle])
    def generate(self, request):
        """
        Generate a new recommendation based on the user's health profile
        and latest daily check-in.

        Optionally accept checkin_id in the POST body to use a specific
        check-in instead of automatically fetching the latest.
        """
        user = request.user

        # Fetch health profile
        try:
            profile = HealthProfile.objects.select_related('user').get(user=user)
        except HealthProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': 'No health profile found. Create your profile first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch latest check-in (optional)
        checkin = DailyCheckIn.objects.filter(user=user).order_by('-date', '-created_at').first()

        # Allow override with specific checkin_id from request body
        checkin_id = request.data.get('checkin_id')
        if checkin_id:
            try:
                checkin = DailyCheckIn.objects.get(id=checkin_id, user=user)
            except (DailyCheckIn.DoesNotExist, TypeError, ValueError):
                return Response(
                    {'success': False, 'error': 'Invalid checkin_id for this user.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Generate recommendation
        try:
            result = engine.generate(profile, checkin)

            # Build check-in snapshot
            checkin_snapshot = {}
            if checkin:
                checkin_snapshot = {
                    'date': str(checkin.date),
                    'current_weight': checkin.current_weight,
                    'sleep_quality': checkin.sleep_quality,
                    'sleep_hours': checkin.sleep_hours,
                    'daily_steps': checkin.daily_steps,
                    'energy_level': checkin.energy_level,
                    'soreness_level': checkin.soreness_level,
                    'stress_level': checkin.stress_level,
                    'resting_heart_rate': checkin.resting_heart_rate,
                    'workout_completed': checkin.workout_completed,
                    'pain_or_injury': checkin.pain_or_injury,
                    'injury_area': checkin.injury_area,
                    'available_minutes': checkin.available_minutes,
                    'preferred_intensity': checkin.preferred_intensity,
                }

            # Save recommendation
            recommendation = Recommendation.objects.create(
                user=user,
                status=result['status'],
                confidence=result['confidence'],
                algorithm_used=result['algorithm_used'],
                workout_split=result['workout_split'],
                exercise_plan=result['exercise_plan'],
                workout_days_per_week=result['workout_days_per_week'],
                diet_plan=result['diet_plan'],
                daily_calorie_target=result['daily_calorie_target'],
                macro_split=result['macro_split'],
                health_notes=result['health_notes'],
                llm_recommendation=result.get('llm_recommendation', ''),
                rag_context_chunks=result.get('rag_context_chunks', []),
                profile_snapshot=result['profile_snapshot'],
                checkin_snapshot=checkin_snapshot,
                explanation=result.get('explanation', ''),
                similar_profiles_count=result.get('similar_profiles_count', 0),
                avg_similarity_score=result.get('avg_similarity_score'),
            )

            serialized = RecommendationSerializer(recommendation).data

            return Response({
                'success': True,
                'message': 'Recommendation generated successfully.',
                'data': serialized,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error("Recommendation generation failed: %s", str(e), exc_info=True)
            return Response(
                {'success': False, 'error': 'Failed to generate recommendation. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the most recent recommendation for the authenticated user."""
        recommendation = self.get_queryset().order_by('-created_at').first()
        if not recommendation:
            return Response(
                {'detail': 'No recommendations found. Generate one first.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(RecommendationSerializer(recommendation).data)

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """Return all recommendations in descending created_at order."""
        queryset = self.get_queryset().order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecommendationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = RecommendationSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['post'])
    def refresh_engine(self, request):
        """Admin-only: invalidate engine cache so it reloads models on next request."""
        if not request.user.is_staff:
            return Response({'detail': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)

        engine.invalidate_cache()
        return Response({'success': True, 'message': 'Engine cache invalidated.'})
