from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import DailyCheckIn, HealthProfile
from profiles.serializers import DailyCheckInSerializer, HealthProfileSerializer
from recommendations.models import Recommendation
from recommendations.serializers import RecommendationListSerializer, RecommendationSerializer


class DashboardSummaryView(APIView):
    """Single backend-owned summary for the app shell and dashboard page."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = HealthProfile.objects.filter(user=user).first()
        latest_checkin = DailyCheckIn.objects.filter(user=user).order_by('-date', '-created_at').first()
        latest_recommendation = Recommendation.objects.filter(user=user).order_by('-created_at').first()

        checkins = DailyCheckIn.objects.filter(user=user).order_by('-date')
        total_checkins = checkins.count()
        completed_workouts = checkins.filter(workout_completed=True).count()
        consistency = round((completed_workouts / total_checkins) * 100) if total_checkins else 0

        streak = _current_workout_streak(user)
        next_workout = None
        if latest_recommendation and latest_recommendation.exercise_plan:
            first_day = latest_recommendation.exercise_plan[0]
            next_workout = {
                'day': first_day.get('day'),
                'focus': first_day.get('focus'),
                'exercise_count': len(first_day.get('exercises', [])),
            }

        return Response({
            'display_name': user.first_name or user.username or 'Athlete',
            'streak_days': streak,
            'consistency_percent': consistency,
            'completed_workouts': completed_workouts,
            'total_checkins': total_checkins,
            'profile_complete': profile is not None,
            'has_checkin': latest_checkin is not None,
            'has_recommendation': latest_recommendation is not None,
            'current_split': latest_recommendation.workout_split if latest_recommendation else None,
            'training_days_per_week': profile.exercise_frequency if profile else None,
            'readiness': {
                'energy_level': latest_checkin.energy_level if latest_checkin else None,
                'soreness_level': latest_checkin.soreness_level if latest_checkin else None,
                'stress_level': latest_checkin.stress_level if latest_checkin else None,
                'sleep_hours': latest_checkin.sleep_hours if latest_checkin else None,
            },
            'next_workout': next_workout,
            'profile': HealthProfileSerializer(profile).data if profile else None,
            'latest_checkin': DailyCheckInSerializer(latest_checkin).data if latest_checkin else None,
            'latest_recommendation': RecommendationSerializer(latest_recommendation).data if latest_recommendation else None,
        })


class AnalyticsSummaryView(APIView):
    """Small analytics endpoint for shell widgets such as streak badges."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        checkins = DailyCheckIn.objects.filter(user=request.user)
        total_checkins = checkins.count()
        completed_workouts = checkins.filter(workout_completed=True).count()
        latest_recommendations = Recommendation.objects.filter(user=request.user).order_by('-created_at')[:5]
        return Response({
            'streak_days': _current_workout_streak(request.user),
            'completed_workouts': completed_workouts,
            'total_checkins': total_checkins,
            'consistency_percent': round((completed_workouts / total_checkins) * 100) if total_checkins else 0,
            'recent_recommendations': RecommendationListSerializer(latest_recommendations, many=True).data,
        })


def _current_workout_streak(user):
    today = timezone.localdate()
    streak = 0
    current_day = today

    while True:
        completed = DailyCheckIn.objects.filter(
            user=user,
            date=current_day,
            workout_completed=True,
        ).exists()
        if not completed:
            return streak
        streak += 1
        current_day -= timedelta(days=1)
