from django.db import models
from django.conf import settings
from fitness_backend.validators import validate_age, validate_weight, validate_height


class HealthProfile(models.Model):
    """
    Comprehensive health profile merging features from all 4 datasets:
    - Dataset 1: Diet & Exercise Plan (nimsara55)
    - Dataset 2: Gym Recommendation (Mendeley)
    - Dataset 3: Diet Recommendations (ziya07)
    - Dataset 4: Personalized Medical Diet Recommendations (ziya07)

    One-to-one with User. Auto-calculates BMI.
    """

    # ==================== CHOICE FIELDS ====================

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
        ('very_active', 'Very Active'),
    ]

    FITNESS_GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('endurance', 'Endurance'),
    ]

    BMI_LEVEL_CHOICES = [
        ('underweight', 'Underweight'),
        ('normal', 'Normal'),
        ('overweight', 'Overweight'),
        ('obese', 'Obese'),
    ]

    DIETARY_PREFERENCE_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('regular', 'Regular'),
        ('low_sodium', 'Low Sodium'),
        ('low_sugar', 'Low Sugar'),
        ('pescatarian', 'Pescatarian'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('mediterranean', 'Mediterranean'),
        ('no_preference', 'No Preference'),
    ]

    SLEEP_QUALITY_CHOICES = [
        ('poor', 'Poor'),
        ('fair', 'Fair'),
        ('good', 'Good'),
    ]

    ALCOHOL_CHOICES = [
        ('none', 'None'),
        ('occasional', 'Occasional'),
        ('regular', 'Regular'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    EQUIPMENT_CHOICES = [
        ('full_gym', 'Full Gym'),
        ('dumbbells', 'Dumbbells Only'),
        ('bodyweight', 'Bodyweight Only'),
        ('home_gym', 'Home Gym'),
        ('resistance_bands', 'Resistance Bands'),
    ]

    WORKOUT_TYPE_CHOICES = [
        ('cardio', 'Cardio'),
        ('strength', 'Strength'),
        ('flexibility', 'Flexibility'),
        ('hiit', 'HIIT'),
        ('mixed', 'Mixed'),
    ]

    GENETIC_RISK_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    # ==================== RELATIONSHIPS ====================

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='health_profile',
    )

    # ==================== DEMOGRAPHICS ====================

    age = models.PositiveIntegerField(validators=[validate_age])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.FloatField(help_text='Height in cm', validators=[validate_height])
    weight = models.FloatField(help_text='Weight in kg', validators=[validate_weight])
    bmi = models.FloatField(blank=True, null=True, help_text='Auto-calculated BMI')
    bmi_level = models.CharField(
        max_length=15, choices=BMI_LEVEL_CHOICES,
        blank=True, help_text='Auto-determined from BMI',
    )

    # ==================== MEDICAL (Dataset 2 & 4) ====================

    chronic_disease = models.CharField(
        max_length=100, blank=True, default='',
        help_text='Diabetes, Heart Disease, Hypertension, Obesity, None',
    )
    hypertension = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    cholesterol = models.PositiveIntegerField(null=True, blank=True, help_text='mg/dL')
    genetic_risk = models.CharField(
        max_length=10, choices=GENETIC_RISK_CHOICES,
        blank=True, default='low',
    )

    # ==================== LIFESTYLE (Dataset 4) ====================

    activity_level = models.CharField(
        max_length=15, choices=ACTIVITY_LEVEL_CHOICES,
        default='moderate',
    )
    exercise_frequency = models.PositiveIntegerField(
        default=3, help_text='Days per week (1-7)',
    )
    daily_steps = models.PositiveIntegerField(
        null=True, blank=True, help_text='From wearable data',
    )
    sleep_quality = models.CharField(
        max_length=10, choices=SLEEP_QUALITY_CHOICES,
        blank=True, default='good',
    )
    smoking_habit = models.BooleanField(default=False)
    alcohol_consumption = models.CharField(
        max_length=15, choices=ALCOHOL_CHOICES,
        blank=True, default='none',
    )
    avg_heart_rate = models.PositiveIntegerField(
        null=True, blank=True, help_text='Wearable device data',
    )

    # ==================== DIET INPUTS (Datasets 1, 3, 4) ====================

    dietary_preference = models.CharField(
        max_length=20, choices=DIETARY_PREFERENCE_CHOICES,
        default='no_preference',
    )
    caloric_intake = models.FloatField(
        null=True, blank=True, help_text='Daily calories target',
    )
    protein_intake = models.FloatField(null=True, blank=True, help_text='Grams/day')
    carbohydrate_intake = models.FloatField(null=True, blank=True, help_text='Grams/day')
    fat_intake = models.FloatField(null=True, blank=True, help_text='Grams/day')
    cuisine_preference = models.CharField(max_length=100, blank=True, default='')
    food_aversion = models.TextField(blank=True, default='', help_text='Foods to avoid')

    # ==================== FITNESS PREFERENCES (Datasets 1, 2) ====================

    fitness_goal = models.CharField(
        max_length=20, choices=FITNESS_GOAL_CHOICES,
        default='maintenance',
    )
    experience_level = models.CharField(
        max_length=15, choices=EXPERIENCE_LEVEL_CHOICES,
        default='intermediate',
    )
    preferred_workout_type = models.CharField(
        max_length=15, choices=WORKOUT_TYPE_CHOICES,
        default='mixed',
    )
    available_equipment = models.CharField(
        max_length=20, choices=EQUIPMENT_CHOICES,
        default='full_gym',
    )

    # ==================== METADATA ====================

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Health Profile'
        verbose_name_plural = 'Health Profiles'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} — BMI {self.bmi or 'N/A'}"

    def save(self, *args, **kwargs):
        """Auto-calculate BMI and BMI level on save."""
        if self.height and self.weight:
            height_m = self.height / 100
            self.bmi = round(self.weight / (height_m ** 2), 1)
            if self.bmi < 18.5:
                self.bmi_level = 'underweight'
            elif self.bmi < 25:
                self.bmi_level = 'normal'
            elif self.bmi < 30:
                self.bmi_level = 'overweight'
            else:
                self.bmi_level = 'obese'
        super().save(*args, **kwargs)

    @property
    def blood_pressure(self):
        """Formatted blood pressure string."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None


class DailyCheckIn(models.Model):
    """
    Dynamic daily body-state check-in.
    Captures frequently-changing fields separate from stable HealthProfile.
    """

    ENERGY_CHOICES = [(i, str(i)) for i in range(1, 6)]
    SORENESS_CHOICES = [(i, str(i)) for i in range(1, 6)]
    STRESS_CHOICES = [(i, str(i)) for i in range(1, 6)]
    INTENSITY_CHOICES = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_checkins',
    )
    date = models.DateField(help_text='Date of the check-in')

    # Body metrics
    current_weight = models.FloatField(
        null=True, blank=True,
        help_text='Weight in kg (optional — use if different from profile)',
    )
    sleep_quality = models.CharField(
        max_length=10, choices=HealthProfile.SLEEP_QUALITY_CHOICES,
        blank=True, default='good',
    )
    sleep_hours = models.FloatField(
        null=True, blank=True,
        help_text='Hours slept last night',
    )
    daily_steps = models.PositiveIntegerField(null=True, blank=True)
    energy_level = models.PositiveIntegerField(
        choices=ENERGY_CHOICES, default=3,
        help_text='Energy level 1-5',
    )
    soreness_level = models.PositiveIntegerField(
        choices=SORENESS_CHOICES, default=1,
        help_text='Soreness level 1-5',
    )
    stress_level = models.PositiveIntegerField(
        choices=STRESS_CHOICES, default=1,
        help_text='Stress level 1-5',
    )
    resting_heart_rate = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='BPM from wearable',
    )
    workout_completed = models.BooleanField(default=False)

    # Workout context
    pain_or_injury = models.BooleanField(default=False)
    injury_area = models.CharField(max_length=100, blank=True, default='')
    available_minutes = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Minutes available for workout today',
    )
    preferred_intensity = models.CharField(
        max_length=10, choices=INTENSITY_CHOICES,
        default='moderate',
    )
    notes = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Daily Check-In'
        verbose_name_plural = 'Daily Check-Ins'
        ordering = ['-date', '-created_at']
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_daily_checkin_per_user_date'),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.date}"
