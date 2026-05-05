from django.contrib import admin
from .models import Recommendation, DatasetEntry


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'workout_split', 'confidence', 'algorithm_used',
        'workout_days_per_week', 'daily_calorie_target',
        'similar_profiles_count', 'created_at',
    ]
    list_filter = ['status', 'confidence', 'algorithm_used', 'workout_split', 'created_at']
    search_fields = ['user__email', 'user__username', 'workout_split']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('User', {
            'fields': ('user', 'status', 'confidence', 'algorithm_used'),
        }),
        ('Exercise Plan', {
            'fields': ('workout_split', 'exercise_plan', 'workout_days_per_week'),
        }),
        ('Diet Plan', {
            'fields': ('diet_plan', 'daily_calorie_target', 'macro_split'),
        }),
        ('Health', {
            'fields': ('health_notes',),
        }),
        ('Similarity Matching', {
            'fields': ('profile_snapshot', 'similar_profiles_count', 'avg_similarity_score'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )


@admin.register(DatasetEntry)
class DatasetEntryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'source', 'age', 'gender', 'bmi',
        'fitness_goal', 'dietary_preference', 'created_at',
    ]
    list_filter = ['source', 'gender', 'fitness_goal', 'dietary_preference']
    search_fields = ['source_id', 'fitness_goal', 'exercise_plan']
    ordering = ['source', 'id']
    readonly_fields = ['created_at']
