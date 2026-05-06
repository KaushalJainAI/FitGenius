# Authentication & Security Subsystem

## Overview
The Authentication & Security subsystem is responsible for identity management, session handling, password recovery, and enhanced security layers such as Two-Factor Authentication (2FA). It serves as the foundation for protecting user health and fitness data.

## Core Architecture
- **Framework**: Django REST Framework (DRF) with SimpleJWT.
- **Custom User Model**: Uses `email` as the primary `USERNAME_FIELD` for a modern login experience.
- **Session Strategy**: Stateless JSON Web Tokens (JWT) stored securely on the frontend and attached to the `Authorization: Bearer <token>` header of every authenticated request.

## Key Features

### 1. Registration & Authentication
- **Endpoints**: `POST /api/auth/register/`, `POST /api/auth/login/`, `POST /api/auth/token/refresh/`.
- **Validation**: Strict password validation and email uniqueness checks. The `custom_exception_handler` formats validation errors beautifully for the frontend.

### 2. Password Recovery (OTP-Based)
- **Model**: `PasswordResetOTP` tracks the generation, expiration, and lock-out states of One-Time Passwords.
- **Flow**:
  1. User requests reset (`POST /api/auth/password-reset/`).
  2. System emails a 6-digit OTP and rate-limits the endpoint (`10/day`).
  3. User verifies OTP (`POST /api/auth/password-reset/verify/`) to receive a temporary reset token.
  4. User submits new password with the token (`POST /api/auth/password-reset/confirm/`).

### 3. Two-Factor Authentication (2FA)
- **Model**: Stored alongside user preferences in the `UserPreference` model (`two_factor_enabled`).
- **Endpoints**: `/api/auth/2fa/enable/`, `/api/auth/2fa/disable/`, and `/api/auth/2fa/status/`.
- **UX**: Managed seamlessly via the Settings > Security tab in the frontend.

### 4. User Preferences
- **Model**: `UserPreference` tracks `theme`, `measurement_system`, and notification preferences.
- **Endpoint**: `GET/PATCH /api/user/preferences/`.
- **Sync**: The frontend `ThemeContext` uses this to persist light/dark mode across devices.

### 5. Account Deletion
- **Endpoint**: `DELETE /api/auth/account/`.
- **Safety**: Requires explicit password verification or email confirmation to prevent accidental data loss.

## Frontend Integration
The React frontend manages authentication state globally via `AuthContext`. It intercepts expired tokens and utilizes the `/refresh/` endpoint to seamlessly extend sessions without interrupting the user's flow.
