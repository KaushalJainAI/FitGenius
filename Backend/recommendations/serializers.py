from rest_framework import serializers
from .models import (
    Recommendation, DatasetEntry,
    RecommendationFeedback, ExerciseFeedback,
    MealFeedback, UserPreferenceMemory
)


class RecommendationSerializer(serializers.ModelSerializer):
    """Full serializer for recommendation responses."""

    class Meta:
        model = Recommendation
        fields = [
            'id', 'user', 'status', 'confidence', 'algorithm_used',
            # Exercise
            'workout_split', 'exercise_plan', 'workout_days_per_week',
            # Diet
            'diet_plan', 'daily_calorie_target', 'macro_split',
            # Health
            'health_notes',
            # LLM & RAG
            'llm_recommendation', 'rag_context_chunks',
            # Snapshots & Explanation
            'profile_snapshot', 'checkin_snapshot', 'explanation',
            # Metadata
            'similar_profiles_count', 'avg_similarity_score',
            'created_at', 'updated_at',
        ]
        read_only_fields = (
            'id', 'user', 'status', 'confidence', 'algorithm_used',
            'workout_split', 'exercise_plan', 'workout_days_per_week',
            'diet_plan', 'daily_calorie_target', 'macro_split',
            'health_notes', 'llm_recommendation', 'rag_context_chunks',
            'profile_snapshot', 'checkin_snapshot', 'explanation',
            'similar_profiles_count', 'avg_similarity_score',
            'created_at', 'updated_at',
        )


class RecommendationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views (no exercise/diet JSON)."""

    class Meta:
        model = Recommendation
        fields = [
            'id', 'status', 'confidence', 'algorithm_used',
            'workout_split', 'workout_days_per_week',
            'daily_calorie_target',
            'similar_profiles_count', 'avg_similarity_score',
            'created_at',
        ]
        read_only_fields = (
            'id', 'user', 'status', 'confidence', 'algorithm_used',
            'workout_split', 'exercise_plan', 'workout_days_per_week',
            'diet_plan', 'daily_calorie_target', 'macro_split',
            'health_notes', 'llm_recommendation', 'rag_context_chunks',
            'profile_snapshot', 'checkin_snapshot', 'explanation',
            'similar_profiles_count', 'avg_similarity_score',
            'created_at', 'updated_at',
        )


class DatasetEntrySerializer(serializers.ModelSerializer):
    """Serializer for dataset entries (admin/debug use)."""

    class Meta:
        model = DatasetEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    difficulty_rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)
    satisfaction_rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)

    class Meta:
        model = RecommendationFeedback
        fields = '__all__'
        read_only_fields = ['id', 'user', 'recommendation', 'created_at']


class ExerciseFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)

    class Meta:
        model = ExerciseFeedback
        fields = '__all__'
        read_only_fields = ['id', 'user', 'recommendation', 'created_at']


class MealFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)

    class Meta:
        model = MealFeedback
        fields = '__all__'
        read_only_fields = ['id', 'user', 'recommendation', 'created_at']


class UserPreferenceMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferenceMemory
        fields = '__all__'
        read_only_fields = ['id', 'user', 'updated_at']
