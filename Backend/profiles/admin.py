from django.contrib import admin
from .models import HealthProfile


@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'age', 'gender', 'bmi', 'bmi_level',
        'fitness_goal', 'activity_level', 'updated_at',
    ]
    list_filter = [
        'gender', 'bmi_level', 'fitness_goal', 'activity_level',
        'dietary_preference', 'experience_level',
    ]
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['bmi', 'bmi_level', 'created_at', 'updated_at']
    ordering = ['-updated_at']

    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Demographics', {
            'fields': ('age', 'gender', 'height', 'weight', 'bmi', 'bmi_level'),
        }),
        ('Medical', {
            'fields': (
                'chronic_disease', 'hypertension', 'diabetes',
                'blood_pressure_systolic', 'blood_pressure_diastolic',
                'cholesterol', 'genetic_risk',
            ),
            'classes': ('collapse',),
        }),
        ('Lifestyle', {
            'fields': (
                'activity_level', 'exercise_frequency', 'daily_steps',
                'sleep_quality', 'smoking_habit', 'alcohol_consumption', 'avg_heart_rate',
            ),
            'classes': ('collapse',),
        }),
        ('Diet', {
            'fields': (
                'dietary_preference', 'caloric_intake', 'protein_intake',
                'carbohydrate_intake', 'fat_intake', 'cuisine_preference', 'food_aversion',
            ),
            'classes': ('collapse',),
        }),
        ('Fitness', {
            'fields': (
                'fitness_goal', 'experience_level', 'preferred_workout_type',
                'available_equipment',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
