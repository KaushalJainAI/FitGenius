# Billing & Subscription Subsystem

## Overview
The Billing subsystem manages the business logic for premium tier access, subscription statuses, and free trial activations.

## Core Architecture
- **Framework**: Django REST Framework.
- **Mocked Payment Gateway**: Currently, the system operates without a live payment gateway (like Stripe or PayPal). It simulates subscription states via database flags and manual validation endpoints.

## Key Features

### 1. Subscription Management
- **Endpoints**: 
  - `GET /api/billing/subscription/`: Returns the current active plan, trial status, and renewal dates.
  - `POST /api/billing/cancel/`: Safely downgrades a user to the "Free" tier at the end of their billing cycle.

### 2. Pro Trial Activation
- **Endpoint**: `POST /api/billing/start-pro-trial/`
- **Logic**: Grants the user a simulated 14-day premium trial, updating their subscription tier to `Pro` instantly without requiring credit card information.

### 3. Billing Plan Catalog
- **Endpoint**: `GET /api/billing/plans/`
- **Dynamic Pricing**: Serves the pricing tiers, plan names, and feature bullets directly from the backend. This allows administrators to adjust pricing, feature lists, and promotional badges without requiring frontend deployments.

## Frontend Integration
- **Component**: `Settings.tsx` (Billing Tab)
- **UX**: Displays beautiful comparison cards for the Free and Pro tiers, dynamically populated by the `/plans/` endpoint. Users can seamlessly start a trial or cancel their plan, with state instantly reflecting across the application.
