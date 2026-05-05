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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(
            HealthProfileSerializer(profile).data,
            status=status.HTTP_201_CREATED,
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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
