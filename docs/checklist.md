# FitGenius Dynamic Recommendation Checklist

## Documentation

- [x] Update root README to describe the real datasets and merged schema.
- [x] Update architecture documentation to explain the real data flow.
- [x] Update notebook README to avoid overclaiming 30-feature training or true collaborative filtering.
- [x] Update frontend README to describe the real app, auth flow, and routes.
- [x] Update backend README to describe the real API and data models.
- [ ] Update proposal/progress report after implementation changes are complete.

## Backend: Data Models

- [x] Review current `Recommendation` model fields.
- [x] Add `DailyCheckIn` model.
- [x] Add validation choices/ranges for dynamic fields.
- [x] Add profile snapshot field to recommendations if missing.
- [x] Add check-in snapshot field to recommendations if missing.
- [x] Create migrations.
- [x] Run migrations locally.

## Backend: Serializers

- [x] Add `DailyCheckInSerializer`.
- [x] Add latest/history response serializers if needed.
- [x] Update `RecommendationSerializer` to expose snapshots, confidence, and explanation.
- [x] Confirm profile serializer supports partial updates.

## Backend: API Views And URLs

- [x] Add `POST /api/checkins/`.
- [x] Add `GET /api/checkins/latest/`.
- [x] Add `GET /api/checkins/history/`.
- [x] Add `GET /api/checkins/<id>/`.
- [x] Confirm `GET /api/profiles/`.
- [x] Confirm `POST /api/profiles/`.
- [x] Confirm or add `POST /api/recommendations/generate/`.
- [x] Add `GET /api/recommendations/latest/`.
- [x] Add `GET /api/recommendations/history/`.
- [x] Add `GET /api/recommendations/<id>/`.
- [x] Ensure all endpoints require authentication.

## Backend: Recommendation Engine

- [x] Add `BMI` to `train_model.py` numeric features.
- [x] Retrain and export `preprocessor.pkl`, `knn_model.pkl`, `svd_model.pkl`, and `reference_plans.pkl`.
- [x] Update inference payload to include `BMI`.
- [x] Replace closest-neighbor-only plan selection with top-K aggregation.
- [x] Convert KNN distances into similarity scores.
- [x] Rank diet candidates by weighted similarity.
- [x] Rank exercise candidates by weighted similarity.
- [x] Add medical safety filter function.
- [x] Add context-aware adjustment function using latest check-in.
- [x] Add injury-aware adjustment rules.
- [x] Add short-workout variant when available minutes are low.
- [x] Add explanation generation using similarity, safety, and context reasons.
- [x] Save recommendation result with profile and check-in snapshots.

## Backend: Tests / Verification

- [ ] Test profile create/update flow.
- [ ] Test check-in create/latest/history flow.
- [ ] Test recommendation generation without check-in.
- [ ] Test recommendation generation with latest check-in.
- [ ] Test poor sleep lowers workout intensity.
- [ ] Test high soreness switches to recovery/lower intensity.
- [ ] Test diabetes adds safety notes and avoids sugar-heavy plan text where possible.
- [ ] Test recommendation history returns newest first.
- [ ] Test unauthenticated requests are rejected.

## Frontend: API Layer

- [x] Add API client methods for profile get/create/update.
- [x] Add API client methods for check-in create/latest/history.
- [x] Add API client methods for recommendation generate/latest/history/detail.
- [x] Add shared TypeScript types for profile, check-in, recommendation, exercise plan, diet plan.
- [x] Add loading and error handling for each API flow.
- [x] Add auth context and token refresh support.

## Frontend: Pages

- [x] Build or update Health Profile page.
- [x] Build Daily Check-In page.
- [x] Build Recommendations page.
- [ ] Build Recommendation History page.
- [ ] Build Progress/Trends page.
- [x] Update Dashboard with latest profile, check-in, and recommendation summary.

## Frontend: UX Details

- [x] Separate stable profile questions from daily check-in questions.
- [x] Use sliders/segmented controls for energy, soreness, stress, and intensity.
- [x] Show BMI as backend-calculated, not manually entered.
- [x] Show clear call-to-action to check in before generating today's plan.
- [x] Show explanation for why the recommendation changed.
- [x] Show confidence and similar profile count.
- [ ] Show empty states for no profile, no check-in, and no recommendation.

## Coursework Demo

- [ ] Prepare a demo user account.
- [ ] Fill stable health profile.
- [ ] Submit normal daily check-in.
- [ ] Generate baseline recommendation.
- [ ] Submit poor sleep/high soreness check-in.
- [ ] Generate updated recommendation.
- [ ] Show stored recommendation history.
- [ ] Explain stable vs dynamic data split.
- [ ] Explain KNN similarity retrieval.
- [ ] Explain safety and context-aware adjustment layer.

## Final Polish

- [ ] Run backend tests.
- [ ] Run frontend lint/build.
- [ ] Manually test end-to-end flow.
- [ ] Update proposal/progress report screenshots.
- [ ] Update architecture diagram if needed.
- [ ] Confirm generated recommendations are saved and retrievable.
