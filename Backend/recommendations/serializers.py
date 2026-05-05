from rest_framework import serializers
from .models import Recommendation, DatasetEntry


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
        read_only_fields = '__all__'


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
        read_only_fields = '__all__'


class DatasetEntrySerializer(serializers.ModelSerializer):
    """Serializer for dataset entries (admin/debug use)."""

    class Meta:
        model = DatasetEntry
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
