# FitGenius AI Current Plan

This document tracks what is already implemented in the codebase and what still needs follow-up work.

## Implemented

### Backend

- JWT auth with login, refresh, logout, and profile endpoints.
- Advanced authentication flows: OTP-based password reset, authenticated password change, 2FA enabling/disabling, and secure account deletion.
- User preferences model persisting theme, measurement system, and notification settings.
- Global custom exception handling for standardized frontend error responses.
- `HealthProfile` with stable health, dataset-grounded diet, and fitness fields.
- `DailyCheckIn` for dynamic readiness data.
- `Recommendation` storage with profile and check-in snapshots.
- Recommendation generation from the latest profile and check-in.
- Medical safety rules and context-aware workout adjustments.
- Recommendation history and latest endpoints.
- Dashboard and analytics summary endpoints for streaks, consistency, next workout, and page summary data.
- Backend-owned profile defaults and profile/check-in option metadata endpoints.
- RAG Help Chat integration using NVIDIA-compatible LLM APIs for fitness-related Q&A. This is the only LLM-backed feature.
- Billing plan catalog and subscription endpoints.

### Frontend

- Token-aware `AuthContext` and API client.
- Login and registration forms wired to backend auth, with field-level validation.
- Profile editor and Daily Check-In forms utilizing dynamic backend option endpoints.
- Dashboard summary and analytics streak driven by backend data.
- Latest recommendation view with detailed workout and diet plans.
- Settings page fully wired for user preferences, security management (2FA, password resets), and billing.
- Help Chat interface connecting to the RAG chat backend.
- Custom premium UI components replacing native inputs, with stable global light/dark theme switching.

## Remaining Work

### Current Endpoint Task: Frontend Data Audit

Goal: verify every frontend page, list what the user sees, and decide whether each data area is already backend-backed or still hardcoded/local.

Current backend-backed areas:

- Login page: sign-in uses `POST /api/auth/login/`; register link is route-only.
- Register page: account creation uses `POST /api/auth/register/`, then creates a starter profile with `POST /api/profiles/`.
- Dashboard: loads profile, latest check-in, and latest recommendation from `/api/profiles/`, `/api/checkins/latest/`, and `/api/recommendations/latest/`.
- Profile Setup: reads and saves the full health profile with `/api/profiles/`; generates plans with `/api/recommendations/generate/`.
- Daily Check-In: reads latest check-in, saves today's readiness, and regenerates the plan through `/api/checkins/latest/`, `/api/checkins/`, and `/api/recommendations/generate/`.
- My Plan: renders the latest recommendation from `/api/recommendations/latest/`.
- Progress: renders analytics from `/api/checkins/history/`.
- User Account: reads auth identity from `/api/auth/profile/` and health profile from `/api/profiles/`.
- Settings billing tab: reads and updates subscription state with `/api/billing/subscription/`, `/api/billing/start-pro-trial/`, and `/api/billing/cancel/`.

Hardcoded or local-only items that need backend APIs if they should be real user data:

1. App header streak: `3 Day Streak` is hardcoded in `src/App.tsx`; add `GET /api/analytics/summary/` or include streak in a dashboard summary endpoint.
2. Dashboard aggregate summary: dashboard currently makes three separate calls and derives metrics client-side; add `GET /api/dashboard/summary/` returning profile status, latest check-in, latest plan summary, streak, consistency, and next workout.
3. Account avatar: uses Dicebear generated URL from username/email; add avatar upload/storage fields if real profile photos are required.
4. Account location/status text: `Backend account` and `Authenticated` are static labels; add real account metadata only if location, verification, or membership status must be shown.
5. Settings preferences: theme, measurement system, and notification settings are stored in localStorage; add `GET/PATCH /api/user/preferences/`.
6. Notification settings: daily reminder and weekly email are local/browser-only; add `GET/PATCH /api/notifications/preferences/` and a backend scheduler/email flow if reminders must work when the app is closed.
7. Security password metadata: `Last changed 3 months ago` is hardcoded; add `password_changed_at` to `GET /api/auth/profile/` or create `GET /api/auth/security/`.
8. Security update password button: UI button is not wired to the existing change-password OTP endpoints; connect it to `/api/auth/change-password/request-otp/` and `/api/auth/change-password/`.
9. Two-factor authentication: toggle is local-only and not persisted; add `/api/auth/2fa/status/`, `/api/auth/2fa/enable/`, and `/api/auth/2fa/disable/` if 2FA is in scope.
10. Delete account: button has no backend action; add `DELETE /api/auth/account/` with confirmation safeguards if account deletion is required.
11. Profile select choices: goal, gender, activity, diet, sleep, alcohol, risk, experience, workout type, and equipment choices are hardcoded in the frontend; optional improvement is `GET /api/profiles/options/` so frontend choices always match Django model choices.
12. Check-in select choices and slider ranges: sleep quality, intensity, and 1-5 readiness scales are hardcoded; optional improvement is `GET /api/checkins/options/`.
13. Register starter profile defaults: gender, activity, exercise frequency, steps, diet, equipment, and other defaults are hardcoded during registration; add `GET /api/profiles/defaults/` or return defaults from registration onboarding.
14. Billing plan comparison cards: plan names, prices, and feature bullets are hardcoded except the active subscription response; add `GET /api/billing/plans/` if plan catalog should be backend-controlled.
15. Legacy local recommendation builder/cache: `src/lib/recommendationData.ts` still contains `buildRecommendation()` and localStorage save/load fallback for profile, check-in, and recommendation; remove or quarantine it once the app is fully backend-only.

Implemented endpoint coverage:

- `GET /api/dashboard/summary/` replaces client-only dashboard aggregation and gives the frontend one backend-owned source for profile state, latest readiness, latest plan, consistency, streak, and next workout.
- `GET /api/analytics/summary/` replaces the hardcoded app-shell streak badge.
- `GET /api/profiles/options/` and `GET /api/profiles/defaults/` expose Django-owned profile choices and onboarding defaults.
- `GET /api/checkins/options/` exposes check-in choices and readiness score ranges.
- `GET/PATCH /api/user/preferences/` persists theme, measurement system, notification settings, and lightweight 2FA state.
- `GET/PATCH /api/notifications/preferences/` aliases notification preference access for notification-specific UI.
- `GET /api/auth/security/` exposes dynamic security metadata.
- `GET /api/auth/2fa/status/`, `POST /api/auth/2fa/enable/`, and `POST /api/auth/2fa/disable/` replace the local-only 2FA toggle.
- `DELETE /api/auth/account/` supports account deletion after explicit email confirmation.
- `GET /api/billing/plans/` replaces hardcoded plan comparison cards.

Current status: all 15 audited hardcoded/local-only areas now have corresponding backend endpoints or backend-backed fallback data. The frontend has been updated for the most important dynamic surfaces: app streak, dashboard summary, settings preferences, security status, billing plans, and onboarding defaults.

Dataset-grounded profile fields:

- The recommender training script uses these merged dataset features: `Age`, `Height`, `Weight`, `BMI`, `Gender`, `Chronic_Disease`, `Activity_Level`, `Dietary_Preference`, and `Fitness_Goal`.
- `/api/profiles/options/` now exposes this `recommendation_features` list and returns choices constrained to the merged dataset values.
- Dataset-backed fitness goals shown to users are now `Weight Loss`, `Weight Gain`, and `Maintenance`. `Muscle Gain` and `Endurance` are no longer presented as profile goals because they are not present in `merged_fitness_data.csv`.
- Dataset-backed diet choices shown to users are `No Preference`, `Regular`, `Vegetarian`, `Vegan`, `Keto`, `Low Sodium`, and `Low Sugar`.
- Dataset-backed activity choices shown to users are `Sedentary`, `Moderate`, and `Active`; BMI-category artifacts that appear in the raw merged `Activity_Level` column are intentionally filtered out.
- For a user who wants to build muscle, the dataset-grounded goal should be `Weight Gain`, since that is the closest supported training label in the merged dataset and maps to the muscle-building workout template in the engine.

Follow-up frontend wiring:

- (Completed) Replace remaining non-critical hardcoded select arrays in `DailyCheckIn` and the registration experience-level dropdown with `/api/checkins/options/` and `/api/profiles/options/`.
- (Completed) Build real UI flows for password update, 2FA setup confirmation, and account deletion confirmation.
- (Completed) Remove the legacy local recommendation builder from `src/lib/recommendationData.ts` once no screen depends on offline fallback behavior.

Migration note:

- `users/migrations/0003_userpreference.py` adds persistent preference storage. Until it is applied, preference and 2FA endpoints return backend defaults with `persisted: false` for 2FA actions instead of failing.

### Backend Verification

- Add automated tests for profile, check-in, and recommendation flows.
- Verify unauthorized requests are rejected in test coverage.
- Validate recommendation behavior under poor sleep, soreness, injury, and medical conditions.
- Add tests for dashboard summary, analytics summary, options/defaults, preferences, security, and billing plan catalog endpoints.

### Frontend Expansion

- Build a recommendation history page backed by `/api/recommendations/history/`.
- Expand the progress page to read from backend history instead of placeholder chart data.
- Add stronger empty states for first-time users with no profile, check-in, or recommendation yet.

### Polishing

- Review proposal/progress reports so they match the implemented system.
- Capture screenshots or screen recordings for the coursework demo.

## Development Notes

- The frontend currently prefers backend reads and writes, but keeps a local cache as a fallback.
- The backend proxy for frontend development is `http://127.0.0.1:8000`.
- If the recommendation model artifacts are retrained, restart the Django backend to reload them.
