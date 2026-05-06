from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import QuerySet
from .models import HealthProfile, DailyCheckIn
from .serializers import HealthProfileSerializer, HealthProfileCreateSerializer, DailyCheckInSerializer, DailyCheckInListSerializer


class IsOwner(IsAuthenticated):
    """Only allow users to access their own profile."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class HealthProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for health profiles.
    Users can only access their own profile.
    Supports create-or-update via POST.
    """
    queryset = HealthProfile.objects.none()
    permission_classes = [IsOwner]

    def get_queryset(self) -> QuerySet[HealthProfile]:
        return HealthProfile.objects.filter(user=self.request.user).select_related('user')

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return HealthProfileCreateSerializer
        return HealthProfileSerializer

    def create(self, request, *args, **kwargs):
        """Create or update the user's health profile (upsert)."""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'detail': 'Invalid health profile data.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            profile = serializer.save()
            return Response(
                HealthProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response(
                {'success': False, 'detail': 'Unable to save health profile.', 'errors': getattr(exc, 'detail', str(exc))},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list(self, request, *args, **kwargs):
        """Return the user's single profile (not a list)."""
        try:
            profile = HealthProfile.objects.select_related('user').get(user=request.user)
            return Response(HealthProfileSerializer(profile).data)
        except HealthProfile.DoesNotExist:
            return Response(
                {'detail': 'No health profile found. Create one first.'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=['get'])
    def options(self, request):
        """Return user-facing choices constrained to the merged dataset feature schema."""
        return Response({
            'source': 'Backend/notebooks/data/merged_fitness_data.csv',
            'recommendation_features': [
                'Age', 'Height', 'Weight', 'BMI',
                'Gender', 'Chronic_Disease', 'Activity_Level',
                'Dietary_Preference', 'Fitness_Goal',
            ],
            'gender': _choices([
                ('male', 'Male'),
                ('female', 'Female'),
                ('other', 'Other'),
            ]),
            'chronic_disease': _choices([
                ('', 'None'),
                ('diabetes', 'Diabetes'),
                ('heart_disease', 'Heart Disease'),
                ('hypertension', 'Hypertension'),
                ('obesity', 'Obesity'),
            ]),
            'activity_level': _choices([
                ('sedentary', 'Sedentary'),
                ('moderate', 'Moderate'),
                ('active', 'Active'),
            ]),
            'fitness_goal': _choices([
                ('weight_loss', 'Weight Loss'),
                ('weight_gain', 'Weight Gain'),
                ('maintenance', 'Maintenance'),
            ]),
            'bmi_level': _choices(HealthProfile.BMI_LEVEL_CHOICES),
            'dietary_preference': _choices([
                ('no_preference', 'No Preference'),
                ('regular', 'Regular'),
                ('vegetarian', 'Vegetarian'),
                ('vegan', 'Vegan'),
                ('keto', 'Keto'),
                ('low_sodium', 'Low Sodium'),
                ('low_sugar', 'Low Sugar'),
            ]),
            'sleep_quality': _choices(HealthProfile.SLEEP_QUALITY_CHOICES),
            'alcohol_consumption': _choices(HealthProfile.ALCOHOL_CHOICES),
            'genetic_risk': _choices(HealthProfile.GENETIC_RISK_CHOICES),
            'experience_level': _choices(HealthProfile.EXPERIENCE_LEVEL_CHOICES),
            'preferred_workout_type': _choices(HealthProfile.WORKOUT_TYPE_CHOICES),
            'available_equipment': _choices(HealthProfile.EQUIPMENT_CHOICES),
        })

    @action(detail=False, methods=['get'])
    def defaults(self, request):
        """Return backend-owned onboarding defaults."""
        return Response({
            'age': 25,
            'gender': 'other',
            'height': 170,
            'weight': 68,
            'chronic_disease': '',
            'hypertension': False,
            'diabetes': False,
            'blood_pressure_systolic': None,
            'blood_pressure_diastolic': None,
            'cholesterol': None,
            'genetic_risk': 'low',
            'activity_level': 'moderate',
            'exercise_frequency': 3,
            'daily_steps': 8000,
            'sleep_quality': 'good',
            'smoking_habit': False,
            'alcohol_consumption': 'none',
            'avg_heart_rate': None,
            'dietary_preference': 'no_preference',
            'caloric_intake': None,
            'protein_intake': None,
            'carbohydrate_intake': None,
            'fat_intake': None,
            'cuisine_preference': '',
            'food_aversion': '',
            'fitness_goal': 'weight_gain',
            'experience_level': 'intermediate',
            'preferred_workout_type': 'mixed',
            'available_equipment': 'full_gym',
        })


class DailyCheckInViewSet(viewsets.ModelViewSet):
    """
    ViewSet for daily check-ins.

    - POST   /api/checkins/           → Create new check-in
    - GET    /api/checkins/latest/    → Most recent check-in
    - GET    /api/checkins/history/   → All check-ins (newest first)
    - GET    /api/checkins/<id>/      → Specific check-in
    """
    queryset = DailyCheckIn.objects.none()
    permission_classes = [IsOwner]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self) -> QuerySet[DailyCheckIn]:
        return DailyCheckIn.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyCheckInListSerializer
        return DailyCheckInSerializer

    def create(self, request, *args, **kwargs):
        """Create or update (upsert by date) a check-in."""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'success': False, 'detail': 'Invalid daily check-in data.', 'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Upsert: update if user+date combo exists
            date = serializer.validated_data.get('date')
            existing = DailyCheckIn.objects.filter(user=request.user, date=date).first()
            if existing:
                for attr, value in serializer.validated_data.items():
                    setattr(existing, attr, value)
                existing.save()
                instance = existing
            else:
                instance = serializer.save()
            return Response(
                DailyCheckInSerializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as exc:
            return Response(
                {'success': False, 'detail': 'Unable to save daily check-in.', 'errors': getattr(exc, 'detail', str(exc))},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Return the most recent check-in."""
        instance = self.get_queryset().first()
        if not instance:
            return Response(
                {'detail': 'No check-ins found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(DailyCheckInSerializer(instance).data)

    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """Return all check-ins in descending date order."""
        queryset = self.get_queryset().order_by('-date', '-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DailyCheckInSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DailyCheckInSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def options(self, request):
        """Return frontend check-in choices and score ranges."""
        return Response({
            'sleep_quality': _choices(HealthProfile.SLEEP_QUALITY_CHOICES),
            'preferred_intensity': _choices(DailyCheckIn.INTENSITY_CHOICES),
            'score_ranges': {
                'energy_level': {'min': 1, 'max': 5, 'low_label': 'Drained', 'high_label': 'Ready'},
                'soreness_level': {'min': 1, 'max': 5, 'low_label': 'Fresh', 'high_label': 'Very sore'},
                'stress_level': {'min': 1, 'max': 5, 'low_label': 'Calm', 'high_label': 'High'},
            },
        })


def _choices(choices):
    return [{'value': value, 'label': label} for value, label in choices]
