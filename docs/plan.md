# FitGenius Dynamic Recommendation Implementation Plan

## Objective

Upgrade FitGenius from a mostly static profile-to-plan recommender into a coursework-ready dynamic recommender system. The system should separate stable user health information from frequently changing body-state data, then use both to generate, store, explain, and display personalized diet/workout recommendations on demand.

## Core Concept

FitGenius should model two kinds of user data:

- **Stable profile data**: information that changes rarely, such as demographics, chronic conditions, diet preferences, equipment, and long-term fitness goals.
- **Dynamic state data**: information that can change daily or weekly, such as sleep, steps, soreness, energy, stress, injury status, and current workout availability.

Recommendations should be generated from the combination of:

1. The user's latest stable health profile.
2. The user's latest body-state check-in.
3. KNN similarity retrieval from the merged historical reference corpus.
4. Medical safety filters.
5. Context-aware intensity and plan adjustments.

Each generated result should be stored in the database with snapshots of the profile and body state used at that time.

## Data Model Plan

### Existing Stable Model: `HealthProfile`

Keep stable or slowly changing fields here:

- `age`
- `gender`
- `height`
- `weight`
- `bmi`
- `bmi_level`
- `chronic_disease`
- `hypertension`
- `diabetes`
- `blood_pressure_systolic`
- `blood_pressure_diastolic`
- `cholesterol`
- `genetic_risk`
- `activity_level`
- `exercise_frequency`
- `dietary_preference`
- `caloric_intake`
- `protein_intake`
- `carbohydrate_intake`
- `fat_intake`
- `cuisine_preference`
- `food_aversion`
- `fitness_goal`
- `experience_level`
- `preferred_workout_type`
- `available_equipment`

Some current lifestyle fields can remain on `HealthProfile` for defaults, but daily values should be captured separately.

### New Dynamic Model: `DailyCheckIn`

Create a new model for current body state:

- `user`
- `date`
- `current_weight`
- `sleep_quality`
- `sleep_hours`
- `daily_steps`
- `energy_level`
- `soreness_level`
- `stress_level`
- `resting_heart_rate`
- `workout_completed`
- `pain_or_injury`
- `injury_area`
- `available_minutes`
- `preferred_intensity`
- `notes`
- `created_at`
- `updated_at`

Suggested scale fields:

- `energy_level`: 1-5
- `soreness_level`: 1-5
- `stress_level`: 1-5
- `preferred_intensity`: `low`, `moderate`, `high`

### Recommendation Storage

Ensure the `Recommendation` model stores:

- `user`
- `status`
- `confidence`
- `algorithm_used`
- `workout_split`
- `exercise_plan`
- `workout_days_per_week`
- `diet_plan`
- `daily_calorie_target`
- `macro_split`
- `health_notes`
- `explanation`
- `profile_snapshot`
- `checkin_snapshot`
- `similar_profiles_count`
- `avg_similarity_score`
- `created_at`
- `updated_at`

The snapshots are important because a user's profile and check-in can change later. Historical recommendations should still show what data was used when the plan was generated.

## Backend API Plan

### Authentication

Keep the existing user/auth flow. All profile, check-in, and recommendation endpoints must require authentication.

### Profile Endpoints

Use these endpoints for stable data:

- `GET /api/profiles/me/`
- `POST /api/profiles/`
- `PATCH /api/profiles/me/`

Expected behavior:

- Return the current user's stable health profile.
- Create a profile if one does not exist.
- Update only submitted fields for profile edits.
- Recalculate BMI whenever height or weight changes.

### Daily Check-In Endpoints

Add endpoints for dynamic state:

- `POST /api/checkins/`
- `GET /api/checkins/latest/`
- `GET /api/checkins/history/`
- `GET /api/checkins/<id>/`

Expected behavior:

- `POST` creates a new check-in for the current user.
- `latest` returns the newest check-in.
- `history` returns recent check-ins in descending date order.
- Validate scale fields and reasonable numeric ranges.

### Recommendation Endpoints

Use these endpoints for recommendation generation and retrieval:

- `POST /api/recommendations/generate/`
- `GET /api/recommendations/latest/`
- `GET /api/recommendations/history/`
- `GET /api/recommendations/<id>/`

Expected behavior for `POST /generate/`:

1. Load the current user's `HealthProfile`.
2. Load the latest `DailyCheckIn`; allow generation without one, but mark context confidence lower.
3. Build model input from profile fields.
4. Run the saved preprocessor and KNN model.
5. Retrieve top-K similar historical rows from `reference_plans.pkl`.
6. Aggregate candidate diet/workout plans using similarity-weighted ranking.
7. Apply medical safety filters.
8. Apply daily context adjustments.
9. Generate explanation text.
10. Save the result as a `Recommendation`.
11. Return the saved recommendation JSON.

## Recommendation Engine Plan

### Model Input Improvements

Update `train_model.py` to include `BMI` as a numeric feature:

- Current numeric features: `Age`, `Height`, `Weight`
- New numeric features: `Age`, `Height`, `Weight`, `BMI`

Retrain and export the model artifacts after this change.

### Top-K Aggregation

Replace single-neighbor recommendation selection with top-K aggregation:

1. Retrieve 10-20 nearest neighbors.
2. Convert cosine distances to similarity scores.
3. Group candidate diet recommendations and exercise plans.
4. Rank by weighted vote or weighted average similarity.
5. Select the best safe plan.

### Medical Safety Rules

Apply hard constraints after candidate retrieval:

- Diabetes: prefer low-glycemic/complex-carb plans; avoid high-sugar text matches.
- Hypertension: avoid extreme intensity, heavy isometric holds, and high-sodium notes.
- High BMI: prefer low-impact workouts.
- Heart disease keyword: warn user and avoid HIIT initially.
- Smoking habit: reduce cardiovascular intensity progression.
- Injury present: avoid exercises that stress the injury area.

### Context-Aware Adjustments

Use `DailyCheckIn` fields to adjust the plan:

- Poor sleep or sleep hours below 6: reduce intensity.
- High soreness: switch to recovery, mobility, or low-impact workout.
- Low energy: reduce volume or recommend a lighter session.
- High stress: favor moderate steady-state or mobility work.
- Low available minutes: return a short workout variant.
- High daily steps: avoid unnecessary extra conditioning.
- Low daily steps: include walking or light cardio.

### Explanation Layer

Each recommendation should include a short explanation:

- Similarity reason: matched users with similar profile/goal/condition.
- Safety reason: any medical constraints applied.
- Context reason: today's check-in adjustments.
- Practical summary: what the user should do today.

## Frontend Plan

### Page 1: Onboarding / Health Profile

Purpose: collect stable profile data.

Sections:

- Basic details
- Medical background
- Diet preferences
- Fitness goals
- Equipment and workout preferences

Expected behavior:

- Create profile for new users.
- Edit profile for returning users.
- Show BMI auto-calculated by backend.

### Page 2: Daily Check-In

Purpose: collect current body state.

Questions:

- Current weight
- Sleep quality
- Sleep hours
- Steps today
- Energy level
- Soreness level
- Stress level
- Resting heart rate
- Pain or injury
- Available workout minutes
- Preferred intensity
- Notes

Expected behavior:

- Submit a new check-in.
- Show latest submitted check-in.
- Encourage the user to check in before generating a plan.

### Page 3: Recommendations

Purpose: show the latest generated recommendation.

Content:

- Generate recommendation button
- Workout split and today's exercise plan
- Diet plan
- Calories and macros
- Health notes
- Explanation
- Confidence and similar profile count
- Link to recommendation history

### Page 4: Progress / History

Purpose: show trends and previous plans.

Content:

- Recent check-ins
- Previous recommendations
- Weight trend
- Steps trend
- Sleep trend
- Workout completion trend

### Page 5: Dashboard

Purpose: central landing screen after login.

Content:

- Latest profile summary
- Latest check-in summary
- Latest recommendation summary
- Quick action: Check in today
- Quick action: Generate recommendation
- Quick action: View history

## Demo Flow For Coursework

1. Register/login as a user.
2. Complete the stable health profile.
3. Submit a daily check-in with normal sleep/energy.
4. Generate a recommendation and show the result.
5. Submit another check-in with poor sleep, high soreness, or injury.
6. Generate another recommendation.
7. Show how the system adjusts workout intensity and explanation.
8. Open history to show stored recommendations and snapshots.

## Implementation Order

1. Add `DailyCheckIn` model, serializer, views, URLs, and migrations.
2. Update `Recommendation` storage if snapshots or fields are missing.
3. Update recommendation engine to accept profile plus latest check-in.
4. Add BMI to model training inputs and retrain artifacts.
5. Implement top-K weighted aggregation.
6. Implement medical safety and context adjustment functions.
7. Add or update backend tests for profile/check-in/recommendation flows.
8. Build frontend check-in page.
9. Update frontend profile flow.
10. Build recommendations page with generate/latest/history support.
11. Build progress/history page.
12. Polish dashboard and coursework demo flow.

## Success Criteria

- Users can maintain stable profile data separately from daily check-ins.
- Users can generate recommendations on demand.
- Recommendations use the latest check-in when available.
- Generated recommendations are stored with profile and check-in snapshots.
- The frontend shows current recommendation, explanation, and history.
- The demo clearly shows dynamic recommendation changes after body-state updates.
