from rest_framework import serializers
from .models import HealthProfile, DailyCheckIn


class HealthProfileSerializer(serializers.ModelSerializer):
    """Full health profile serializer with computed fields."""
    blood_pressure = serializers.ReadOnlyField()
    bmi = serializers.ReadOnlyField()
    bmi_level = serializers.ReadOnlyField()

    class Meta:
        model = HealthProfile
        fields = [
            'id', 'user',
            # Demographics
            'age', 'gender', 'height', 'weight', 'bmi', 'bmi_level',
            # Medical
            'chronic_disease', 'hypertension', 'diabetes',
            'blood_pressure_systolic', 'blood_pressure_diastolic', 'blood_pressure',
            'cholesterol', 'genetic_risk',
            # Lifestyle
            'activity_level', 'exercise_frequency', 'daily_steps',
            'sleep_quality', 'smoking_habit', 'alcohol_consumption', 'avg_heart_rate',
            # Diet
            'dietary_preference', 'caloric_intake', 'protein_intake',
            'carbohydrate_intake', 'fat_intake', 'cuisine_preference', 'food_aversion',
            # Fitness
            'fitness_goal', 'experience_level', 'preferred_workout_type',
            'available_equipment',
            # Meta
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'bmi', 'bmi_level', 'created_at', 'updated_at']


class HealthProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating health profiles.
    Automatically assigns the current user.
    """

    class Meta:
        model = HealthProfile
        exclude = ['user', 'bmi', 'bmi_level', 'created_at', 'updated_at']

    def validate_exercise_frequency(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError('Exercise frequency must be between 1 and 7 days per week.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        # Update existing or create new
        profile, _ = HealthProfile.objects.update_or_create(
            user=user,
            defaults=validated_data,
        )
        return profile

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DailyCheckInSerializer(serializers.ModelSerializer):
    """Serializer for daily check-in create/read."""

    class Meta:
        model = DailyCheckIn
        fields = [
            'id', 'user',
            'date',
            'current_weight', 'sleep_quality', 'sleep_hours', 'daily_steps',
            'energy_level', 'soreness_level', 'stress_level',
            'resting_heart_rate', 'workout_completed',
            'pain_or_injury', 'injury_area', 'available_minutes',
            'preferred_intensity', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        for field in ('energy_level', 'soreness_level', 'stress_level'):
            value = attrs.get(field)
            if value is not None and (value < 1 or value > 5):
                raise serializers.ValidationError({field: 'Value must be between 1 and 5.'})

        sleep_hours = attrs.get('sleep_hours')
        if sleep_hours is not None and (sleep_hours < 0 or sleep_hours > 24):
            raise serializers.ValidationError({'sleep_hours': 'Sleep hours must be between 0 and 24.'})

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class DailyCheckInListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for history list views."""

    class Meta:
        model = DailyCheckIn
        fields = [
            'id', 'date', 'current_weight', 'sleep_quality', 'sleep_hours',
            'daily_steps', 'energy_level', 'soreness_level', 'stress_level',
            'workout_completed', 'pain_or_injury', 'available_minutes',
            'preferred_intensity', 'created_at',
        ]
        read_only_fields = (
            'id', 'date', 'current_weight', 'sleep_quality', 'sleep_hours',
            'daily_steps', 'energy_level', 'soreness_level', 'stress_level',
            'workout_completed', 'pain_or_injury', 'available_minutes',
            'preferred_intensity', 'created_at',
        )
