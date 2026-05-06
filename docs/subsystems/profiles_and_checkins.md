# Profiles & Check-Ins Subsystem

## Overview
The Profiles & Check-Ins subsystem acts as the primary data collection layer for the recommendation engine. It stores static/historical user health data (`HealthProfile`) and dynamic, daily readiness data (`DailyCheckIn`).

## Core Architecture
- **Framework**: Django REST Framework.
- **Models**: `HealthProfile` and `DailyCheckIn`.
- **Validation**: Strict model and serializer-level validations protect data integrity before it reaches the recommendation pipeline.

## Key Features

### 1. Health Profile Management
- **Model (`HealthProfile`)**: Captures detailed biometrics (age, weight, height, BMI), medical flags (chronic diseases, hypertension, diabetes), and lifestyle choices (diet, alcohol, sleep quality).
- **Options Endpoint (`GET /api/profiles/options/`)**: Instead of hardcoding dropdown choices in the frontend, this endpoint serves backend-defined choices. For example, diet options like `Regular`, `Low Sodium`, and `Low Sugar` match the exact string expectations of the recommendation code.
- **Defaults Endpoint (`GET /api/profiles/defaults/`)**: Provides standard fallback values to streamline the frontend onboarding/registration process.

### 2. Daily Readiness Check-Ins
- **Model (`DailyCheckIn`)**: Records daily variance in weight, sleep hours, stress levels, soreness, and available workout time.
- **Upsert Logic**: The `POST /api/checkins/` endpoint handles upserts gracefully. If a user submits multiple check-ins on the same calendar day, the backend automatically updates the existing record rather than creating duplicates.
- **Validation Rules**: Ensures energy, soreness, and stress levels stay precisely between 1 and 5, and sleep hours remain between 0 and 24.

### 3. Data Integration with Recommender
- **Triggers**: Creating or updating a profile/check-in generally triggers a prompt to the user to regenerate their plan (`POST /api/recommendations/generate/`).
- **BMI Calculation**: The backend dynamically calculates BMI on read operations and passes it directly to the recommendation engine's context payload.

## Frontend Integration
The frontend utilizes the metadata from `/options/` to dynamically populate premium React components (like custom dropdowns and segmented controls), ensuring the UI always stays in sync with backend schema changes.
