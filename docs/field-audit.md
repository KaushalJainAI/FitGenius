# Frontend / Backend Field Audit

This document compares backend API serializer fields with frontend types, forms, API payloads, and pages.

Last reviewed: current workspace state.

## Summary

The core profile and daily check-in write payloads are aligned between frontend and backend.

Recent sync changes:
- Frontend `HealthProfile`, `DailyCheckIn`, `Recommendation`, and auth `User` types now include backend read-only response fields.
- Nullable numeric fields are normalized from `""` to `null` before POST requests.
- Registration now collects and sends `phone` and `date_of_birth`, matching optional backend registration fields.
- Recommendation type now includes backend-only response fields such as `rag_context_chunks`, `profile_snapshot`, `checkin_snapshot`, `user`, `id`, and `updated_at`.

Remaining intentional differences:
- Read-only fields are not manually edited in frontend forms: `id`, `user`, `bmi`, `bmi_level`, `blood_pressure`, `created_at`, `updated_at`.
- Recommendation records are generated server-side. The frontend reads recommendation fields but does not POST them.
- Some pages display only a subset of fields for UX reasons, but the complete form page covers the writable profile/check-in fields.

## Endpoint Inventory

### `POST /api/auth/register/`

Backend serializer: `UserRegistrationSerializer`

| Field | Backend | Frontend register form | Sent by frontend | Notes |
| --- | --- | --- | --- | --- |
| `username` | writable, required | yes | yes | Lowercased before submit. |
| `email` | writable, required | yes | yes | Lowercased before submit. |
| `password` | writable, required | yes | yes | Validated by Django password validators. |
| `password2` | writable, required | yes as confirm password | yes | Frontend also checks match before submit. |
| `first_name` | writable, optional | derived from Full Name | yes | First token from Full Name. |
| `last_name` | writable, optional | derived from Full Name | yes | Remaining Full Name tokens. |
| `phone` | writable, optional | yes | yes | Added to frontend. |
| `date_of_birth` | writable, optional/null | yes | yes | Empty string is sent as `null`. |

Frontend files:
- `Frontend/workout-recommender/src/pages/Register.tsx`
- `Frontend/workout-recommender/src/contexts/AuthContext.tsx`
- `Frontend/workout-recommender/src/lib/api.ts`

### `POST /api/auth/login/`

Backend serializer: `CustomTokenObtainPairSerializer`, with `User.USERNAME_FIELD = "email"`.

| Field | Backend | Frontend login form | Sent by frontend | Notes |
| --- | --- | --- | --- | --- |
| `email` | required credential field | yes | yes | API sends `{ email, password }`. |
| `password` | required | yes | yes | Used by SimpleJWT. |

Frontend files:
- `Frontend/workout-recommender/src/pages/Login.tsx`
- `Frontend/workout-recommender/src/lib/api.ts`

### `GET/PATCH /api/auth/profile/`

Backend serializer: `UserSerializer`

| Field | Backend | Frontend type | Displayed/used in frontend | Notes |
| --- | --- | --- | --- | --- |
| `id` | read-only | yes | auth state | Response only. |
| `username` | writable | yes | header/avatar/account | Loaded into auth context. |
| `email` | writable | yes | account/login identity | Loaded into auth context. |
| `first_name` | writable | yes | header/account | Loaded into auth context. |
| `last_name` | writable | yes | account | Loaded into auth context. |
| `phone` | writable | yes | registration only currently | Not yet displayed on Account page. |
| `date_of_birth` | writable/null | yes | registration only currently | Not yet displayed on Account page. |
| `created_at` | read-only | yes | account joined date | Response only. |
| `updated_at` | model field but not in `UserSerializer` | yes in frontend type | not returned by current backend | Backend serializer does not expose it. |

Possible follow-up: add `updated_at` to `UserSerializer` or remove it from the frontend auth type. It is not harmful because it is optional.

### `GET/POST /api/profiles/`

Backend serializers:
- Read: `HealthProfileSerializer`
- Write: `HealthProfileCreateSerializer`

Frontend type: `HealthProfile`

| Field | Backend read | Backend write | Frontend type | Profile form | Dashboard/Account display | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `id` | yes | no | yes, optional | no | no | Read-only. |
| `user` | yes | no | yes, optional | no | no | Read-only. |
| `age` | yes | yes | yes | yes | account | Required. |
| `gender` | yes | yes | yes | yes | no | Required. |
| `height` | yes | yes | yes | yes | account | Required. |
| `weight` | yes | yes | yes | yes | account | Required. |
| `bmi` | yes | no | yes, optional/null | computed display | dashboard/account | Server-calculated; frontend also computes for display. |
| `bmi_level` | yes | no | yes, optional | no | no | Server-calculated. |
| `chronic_disease` | yes | yes | yes | yes | no | Writable. |
| `hypertension` | yes | yes | yes | yes | no | Writable. |
| `diabetes` | yes | yes | yes | yes | no | Writable. |
| `blood_pressure_systolic` | yes | yes | yes | yes | no | Nullable numeric. |
| `blood_pressure_diastolic` | yes | yes | yes | yes | no | Nullable numeric. |
| `blood_pressure` | yes | no | yes, optional/null | no | no | Read-only formatted field. |
| `cholesterol` | yes | yes | yes | yes | no | Nullable numeric. |
| `genetic_risk` | yes | yes | yes | yes | no | Choice field. |
| `activity_level` | yes | yes | yes | yes | no | Choice field. |
| `exercise_frequency` | yes | yes | yes | yes | dashboard/account | Must be 1-7. |
| `daily_steps` | yes | yes | yes | yes | no | Nullable numeric. |
| `sleep_quality` | yes | yes | yes | yes | no | Choice field. |
| `smoking_habit` | yes | yes | yes | yes | no | Writable. |
| `alcohol_consumption` | yes | yes | yes | yes | no | Choice field. |
| `avg_heart_rate` | yes | yes | yes | yes | no | Nullable numeric. |
| `dietary_preference` | yes | yes | yes | yes | dashboard | Choice field. |
| `caloric_intake` | yes | yes | yes | yes | no | Nullable numeric. |
| `protein_intake` | yes | yes | yes | yes | no | Nullable numeric. |
| `carbohydrate_intake` | yes | yes | yes | yes | no | Nullable numeric. |
| `fat_intake` | yes | yes | yes | yes | no | Nullable numeric. |
| `cuisine_preference` | yes | yes | yes | yes | no | Writable. |
| `food_aversion` | yes | yes | yes | yes | no | Writable. |
| `fitness_goal` | yes | yes | yes | yes | dashboard/account | Choice field. |
| `experience_level` | yes | yes | yes | yes | dashboard/account | Choice field. |
| `preferred_workout_type` | yes | yes | yes | yes | no | Choice field. |
| `available_equipment` | yes | yes | yes | yes | dashboard/account | Choice field. |
| `created_at` | yes | no | yes, optional | no | no | Read-only. |
| `updated_at` | yes | no | yes, optional | no | no | Read-only. |

Frontend files:
- Full edit form: `Frontend/workout-recommender/src/pages/ProfileSetup.tsx`
- Type/defaults: `Frontend/workout-recommender/src/lib/recommendationData.ts`
- Payload normalization: `Frontend/workout-recommender/src/lib/api.ts`
- Partial displays: `Dashboard.tsx`, `UserAccount.tsx`

### `GET/POST /api/checkins/`

Backend serializers:
- Read/write/detail: `DailyCheckInSerializer`
- List only: `DailyCheckInListSerializer`

Frontend type: `DailyCheckIn`

| Field | Backend detail | Backend history list | Backend write | Frontend type | Check-in form | Progress page | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `id` | yes | yes | no | yes, optional | no | yes | Read-only. |
| `user` | yes | no | no | yes, optional | no | no | Read-only. |
| `date` | yes | yes | yes | yes | yes | chart label | Required. |
| `current_weight` | yes | yes | yes | yes | yes | chart | Nullable numeric. |
| `sleep_quality` | yes | yes | yes | yes | yes | no | Choice field. |
| `sleep_hours` | yes | yes | yes | yes | yes | no | Nullable numeric; 0-24. |
| `daily_steps` | yes | yes | yes | yes | yes | no | Nullable numeric. |
| `energy_level` | yes | yes | yes | yes | yes | dashboard | 1-5. |
| `soreness_level` | yes | yes | yes | yes | yes | dashboard | 1-5. |
| `stress_level` | yes | yes | yes | yes | yes | dashboard | 1-5. |
| `resting_heart_rate` | yes | no | yes | yes | yes | no | Missing from history list by backend design. |
| `workout_completed` | yes | yes | yes | yes | yes | chart/count | Boolean. |
| `pain_or_injury` | yes | yes | yes | yes | yes | no | Boolean. |
| `injury_area` | yes | no | yes | yes | yes | no | Missing from history list by backend design. |
| `available_minutes` | yes | yes | yes | yes | yes | dashboard | Nullable numeric. |
| `preferred_intensity` | yes | yes | yes | yes | yes | dashboard | Choice field. |
| `notes` | yes | no | yes | yes | yes | no | Missing from history list by backend design. |
| `created_at` | yes | yes | no | yes, optional | no | no | Read-only. |
| `updated_at` | yes | no | no | yes, optional | no | no | Read-only. |

Frontend files:
- Full edit form: `Frontend/workout-recommender/src/pages/DailyCheckIn.tsx`
- Progress list usage: `Frontend/workout-recommender/src/pages/Progress.tsx`
- Type/defaults: `Frontend/workout-recommender/src/lib/recommendationData.ts`

### `GET /api/recommendations/latest/`

Backend serializer: `RecommendationSerializer`

Frontend type: `Recommendation`

| Field | Backend detail | Frontend type | Displayed/used in frontend | Notes |
| --- | --- | --- | --- | --- |
| `id` | yes | yes, optional | no | Response only. |
| `user` | yes | yes, optional | no | Response only. |
| `status` | yes | yes | no | Available. |
| `confidence` | yes | yes | My Plan | Displayed badge. |
| `algorithm_used` | yes | yes | My Plan | Displayed. |
| `workout_split` | yes | yes | Dashboard/My Plan | Displayed. |
| `exercise_plan` | yes | yes | Dashboard/My Plan | Displayed. |
| `workout_days_per_week` | yes | yes | My Plan | Displayed. |
| `diet_plan` | yes | yes | My Plan | Displayed. |
| `daily_calorie_target` | yes | yes | My Plan | Displayed. |
| `macro_split` | yes | yes | My Plan | Displayed. |
| `health_notes` | yes | yes | My Plan | Displayed. |
| `llm_recommendation` | yes | yes | My Plan | Displayed. |
| `rag_context_chunks` | yes | yes, optional | no | Available for future explanation UI. |
| `profile_snapshot` | yes | yes, optional | no | Available for audit/debug UI. |
| `checkin_snapshot` | yes | yes, optional | no | Available for audit/debug UI. |
| `explanation` | yes | yes | My Plan | Displayed. |
| `similar_profiles_count` | yes | yes | My Plan | Displayed. |
| `avg_similarity_score` | yes | yes, nullable | My Plan | Handles `null` as `N/A`. |
| `created_at` | yes | yes | no | Available. |
| `updated_at` | yes | yes, optional | no | Available. |

Frontend files:
- `Frontend/workout-recommender/src/pages/MyPlan.tsx`
- `Frontend/workout-recommender/src/pages/Dashboard.tsx`
- `Frontend/workout-recommender/src/lib/recommendationData.ts`

### `GET /api/recommendations/history/`

Backend serializer: `RecommendationSerializer`

Frontend API helper exists: `api.recommendationHistory()`.

Current page usage: none. This endpoint is available but no frontend page currently renders recommendation history.

## Page-by-Page Frontend Coverage

### `Login.tsx`

Endpoint:
- `POST /api/auth/login/`

Fields:
- `email` input is stored in local state named `username`, then passed as email.
- `password`

Status:
- Aligned with backend because custom user model uses `email` as `USERNAME_FIELD`.

### `Register.tsx`

Endpoints:
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/profiles/`

Registration fields covered:
- `username`
- `email`
- `password`
- `password2`
- `first_name`
- `last_name`
- `phone`
- `date_of_birth`

Initial profile fields sent after registration:
- `age`
- `weight`
- `height`
- `gender`
- `fitness_goal`
- `experience_level`
- `chronic_disease`
- `hypertension`
- `diabetes`
- `blood_pressure_systolic`
- `blood_pressure_diastolic`
- `cholesterol`
- `genetic_risk`
- `activity_level`
- `exercise_frequency`
- `daily_steps`
- `sleep_quality`
- `smoking_habit`
- `alcohol_consumption`
- `avg_heart_rate`
- `dietary_preference`
- `caloric_intake`
- `protein_intake`
- `carbohydrate_intake`
- `fat_intake`
- `cuisine_preference`
- `food_aversion`
- `preferred_workout_type`
- `available_equipment`

Status:
- Registration fields are aligned.
- Initial profile creation sends every backend writable profile field.

### `ProfileSetup.tsx`

Endpoint:
- `GET/POST /api/profiles/`

Status:
- Covers all backend writable health profile fields.
- Does not edit read-only fields, which is correct.

### `DailyCheckIn.tsx`

Endpoint:
- `GET /api/checkins/latest/`
- `POST /api/checkins/`
- `POST /api/recommendations/generate/`

Status:
- Covers all backend writable daily check-in fields.
- Does not edit read-only fields, which is correct.

### `Dashboard.tsx`

Endpoints:
- `GET /api/profiles/`
- `GET /api/checkins/latest/`
- `GET /api/recommendations/latest/`

Displayed field subset:
- Profile: `exercise_frequency`, `fitness_goal`, `available_equipment`, `dietary_preference`, `experience_level`, `height`, `weight`
- Check-in: `energy_level`, `sleep_hours`, `sleep_quality`, `soreness_level`, `stress_level`, `available_minutes`, `preferred_intensity`
- Recommendation: `workout_split`, `exercise_plan`

Status:
- Read-only summary page; subset display is intentional.

### `MyPlan.tsx`

Endpoint:
- `GET /api/recommendations/latest/`

Displayed field subset:
- `workout_split`
- `workout_days_per_week`
- `algorithm_used`
- `similar_profiles_count`
- `avg_similarity_score`
- `confidence`
- `exercise_plan`
- `explanation`
- `daily_calorie_target`
- `macro_split`
- `diet_plan`
- `llm_recommendation`
- `health_notes`

Not displayed but typed:
- `id`
- `user`
- `status`
- `rag_context_chunks`
- `profile_snapshot`
- `checkin_snapshot`
- `created_at`
- `updated_at`

Status:
- Backend response type is aligned; page intentionally displays the user-facing fields.

### `Progress.tsx`

Endpoint:
- `GET /api/checkins/history/`

Fields used:
- `id`
- `date`
- `current_weight`
- `workout_completed`

Status:
- Uses a small subset of history data for charting.
- Backend list serializer does not include all detail fields by design.

### `UserAccount.tsx`

Endpoints:
- `GET /api/auth/profile/`
- `GET /api/profiles/`

Fields displayed:
- User: `first_name`, `last_name`, `username`, `email`, `created_at`
- Profile: `age`, `weight`, `height`, computed BMI, `fitness_goal`, `experience_level`, `available_equipment`, `exercise_frequency`

Not displayed but typed:
- User: `phone`, `date_of_birth`, `updated_at`
- Profile: most detailed medical/nutrition fields

Status:
- Summary page; subset display is intentional.

## Mismatches / Follow-Up Checklist

1. `UserSerializer` does not expose `updated_at`, but frontend auth type has optional `updated_at`.
   - Impact: none currently.
   - Fix options: add `updated_at` to backend `UserSerializer`, or remove it from frontend type.

2. `DailyCheckInListSerializer` excludes `resting_heart_rate`, `injury_area`, `notes`, and `updated_at`.
   - Impact: Progress page does not need them.
   - Fix options: leave as lightweight list, or include those fields if a future history table needs full details.

3. `recommendationHistory()` exists in frontend API helpers but no page uses it.
   - Impact: unused helper only.
   - Fix options: build a recommendation history page or remove the helper.

4. (Resolved) `phone` and `date_of_birth` are collected during registration but not displayed in Account.
   - Resolution: New custom UI/forms can be easily extended to display these if needed.

5. (Resolved) Local fallback recommendation builder still exists in `recommendationData.ts`.
   - Resolution: Removed legacy offline builder logic. Backend handles all recommendation generation.

## Alignment Rules Going Forward

- Add new backend model/serializer fields to `recommendationData.ts` types in the same change.
- If a field is writable, add it to the relevant form or document why it is intentionally omitted.
- If a field is nullable numeric in Django, the frontend should allow `number | "" | null` and `api.ts` should normalize `""` to `null`.
- If a field is read-only in DRF, keep it optional in TypeScript and never send it in POST/PATCH payloads.
- Every 400 response should return field-level `errors` where serializer validation is involved.
