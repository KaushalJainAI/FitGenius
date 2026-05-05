# FitGenius AI Frontend

This is the React + Vite frontend for FitGenius AI. It talks to the Django backend through a token-aware API client and uses an auth context so authenticated requests always carry the current access token.

## Stack

- React 19
- TypeScript
- Vite
- React Router
- Tailwind CSS
- lucide-react icons

## Runtime Flow

- Login stores the JWT tokens returned by the backend.
- `AuthContext` loads the current user and exposes `login`, `logout`, `register`, and `refreshUser`.
- `src/lib/api.ts` attaches the access token to every request and retries once after a refresh if a request gets `401`.
- Vite proxies `/api/*` to `http://127.0.0.1:8000` in development.

## Pages

- `/login` - sign in
- `/register` - account creation
- `/` - dashboard summary
- `/profile` - stable health profile editor
- `/check-in` - daily readiness form
- `/plan` - latest recommendation view
- `/progress` - progress analytics
- `/settings` - UI settings
- `/account` - user account panel

## Data Contract

The frontend mirrors the backend data shapes for:

- `HealthProfile`
- `DailyCheckIn`
- `Recommendation`

Local fallback storage is used only when the backend is unavailable; the app still prefers backend reads and writes.

## Development

```bash
cd Frontend/workout-recommender
npm install
npm run dev
```

Optional environment variable:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

If `VITE_API_BASE_URL` is not set, the app uses the Vite proxy and calls `/api/*` directly.

## Build

```bash
npm run build
```

## Notable Files

- `src/contexts/AuthContext.tsx` - auth state and token-backed API helpers.
- `src/lib/api.ts` - backend client and refresh handling.
- `src/pages/ProfileSetup.tsx` - stable profile editor.
- `src/pages/DailyCheckIn.tsx` - daily readiness form.
- `src/pages/MyPlan.tsx` - recommendation view.
- `src/pages/Dashboard.tsx` - summary dashboard.

