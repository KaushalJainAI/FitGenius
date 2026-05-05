# FitGenius AI Backend

This directory contains the Django REST backend for FitGenius AI. It serves authentication, health profiles, daily check-ins, and recommendation generation.

## Apps

- `users/` - custom user model, JWT login/register/logout, password changes, profile endpoint.
- `profiles/` - `HealthProfile` and `DailyCheckIn` models plus serializers and viewsets.
- `recommendations/` - recommendation model, serializers, API views, and the in-memory recommendation engine.
- `fitness_backend/` - project settings, URL routing, validation helpers, and shared exceptions.

## Data Model Summary

### HealthProfile

Stable profile fields captured by the frontend:

- demographics: `age`, `gender`, `height`, `weight`, `bmi`, `bmi_level`
- medical: `chronic_disease`, `hypertension`, `diabetes`, `blood_pressure_systolic`, `blood_pressure_diastolic`, `cholesterol`, `genetic_risk`
- lifestyle: `activity_level`, `exercise_frequency`, `daily_steps`, `sleep_quality`, `smoking_habit`, `alcohol_consumption`, `avg_heart_rate`
- nutrition: `dietary_preference`, `caloric_intake`, `protein_intake`, `carbohydrate_intake`, `fat_intake`, `cuisine_preference`, `food_aversion`
- training: `fitness_goal`, `experience_level`, `preferred_workout_type`, `available_equipment`

### DailyCheckIn

Dynamic readiness fields captured daily:

- `date`, `current_weight`, `sleep_quality`, `sleep_hours`, `daily_steps`
- `energy_level`, `soreness_level`, `stress_level`, `resting_heart_rate`
- `workout_completed`, `pain_or_injury`, `injury_area`
- `available_minutes`, `preferred_intensity`, `notes`

### Recommendation

Stored recommendation snapshot:

- `status`, `confidence`, `algorithm_used`
- `workout_split`, `exercise_plan`, `workout_days_per_week`
- `diet_plan`, `daily_calorie_target`, `macro_split`
- `health_notes`, `llm_recommendation`, `rag_context_chunks`
- `profile_snapshot`, `checkin_snapshot`
- `explanation`, `similar_profiles_count`, `avg_similarity_score`

## API Surface

### Authentication

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/logout/`
- `GET/PATCH /api/auth/profile/`

Login and refresh responses set HttpOnly cookies. The frontend also stores access and refresh tokens and sends `Authorization: Bearer ...` headers on API requests.

### Profiles

- `GET /api/profiles/` returns the current user's profile or `404` if none exists.
- `POST /api/profiles/` creates or updates the current user's profile.

The profile serializer recalculates BMI on save.

### Check-Ins

- `POST /api/checkins/` upserts a check-in by user/date.
- `GET /api/checkins/latest/`
- `GET /api/checkins/history/`

### Recommendations

- `POST /api/recommendations/generate/`
- `GET /api/recommendations/latest/`
- `GET /api/recommendations/history/`
- `GET /api/recommendations/<id>/`

The generate endpoint loads the latest profile and check-in, passes them into the engine, applies medical safety and context rules, stores a snapshot, and returns the saved recommendation.

## Recommendation Engine

The engine in `recommendations/engine.py` follows this flow:

1. Build the profile feature vector.
2. Run KNN retrieval over the exported model artifacts.
3. Aggregate the top matching historical plans.
4. Apply medical safety constraints.
5. Apply daily context adjustments from the latest check-in.
6. Build an explanation and store the final recommendation.

## Local Setup

```bash
cd Backend
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

If you need to regenerate model artifacts, run the notebook pipeline under `Backend/notebooks/` first, then refresh the engine cache or restart the server.

