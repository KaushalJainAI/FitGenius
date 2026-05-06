# Frontend Architecture Subsystem

## Overview
The frontend architecture is designed to deliver a premium, highly responsive, and dynamic user experience. It consumes the Django REST Framework APIs and handles complex local state, routing, and styling.

## Core Technology Stack
- **Framework**: React 18
- **Build Tool**: Vite (configured with a proxy to `localhost:8000` to avoid CORS issues during development).
- **Language**: TypeScript, ensuring type safety across API payloads and component props.
- **Styling**: Vanilla CSS (`index.css`) with extensive use of CSS variables for theming. Tailwind CSS is configured but currently kept minimal in favor of custom premium component designs.

## Key Architectural Concepts

### 1. Context-Driven State Management
- **`AuthContext`**: Wraps the application to provide global access to the current authenticated user, JWT tokens, login/logout handlers, and token refresh logic.
- **`ThemeContext`**: Synchronizes the user's light/dark mode preference with the backend `UserPreference` API and manages the `[data-theme="dark"]` attribute on the HTML root element.

### 2. Dynamic Component Library
To avoid reliance on standard browser elements (which look basic), the application utilizes custom-built, highly polished UI components:
- **`CustomDropdown`**: Replaces native `<select>` elements. Fully theme-aware, supports keyboard navigation, and integrates flawlessly with backend `/options/` metadata.
- **`NumericInput`**: A specialized increment/decrement control with integrated unit labels (e.g., "kg", "cm") to replace standard `<input type="number">`.
- **Form Wrappers**: Extensive use of flexbox, CSS Grid, and subtle micro-animations (like hover states and transitions) to create a "glassmorphism" or modern SaaS aesthetic.

### 3. API Integration Layer
- **`api.ts`**: A centralized Axios/Fetch wrapper that automatically injects the JWT Authorization header, normalizes empty strings to `null` before sending payloads to Django, and catches network errors.

### 4. Routing
- **React Router DOM**: Handles client-side navigation.
- **Protected Routes**: Wraps sensitive pages (like Dashboard, Settings, Check-In) to automatically redirect unauthenticated users to the Login page.

## Data Flow
1. **Load**: On mount, protected pages fetch necessary data (e.g., Profile, Check-in, Recommendations) via `api.ts`.
2. **Display**: Data is passed down to presentation components.
3. **Mutate**: Form submissions trigger `POST`/`PATCH` API calls.
4. **Error Handling**: 400 Bad Request responses containing `errors` objects are mapped back to form inputs, providing the user with immediate, inline field validation feedback.
