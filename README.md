# FitGenius AI - Workout & Diet Recommender

FitGenius AI is a full-stack fitness recommender with a Django REST backend and a React + Vite frontend. The system keeps stable user health data separate from daily check-ins, then combines both with the recommendation pipeline to generate workout, diet, and safety-aware guidance.

## What The App Does

- JWT authentication with access and refresh tokens.
- Stable health profile capture for demographics, medical history, diet, goals, and equipment.
- Daily check-ins for sleep, soreness, stress, energy, injury, steps, and workout availability.
- Recommendation generation with profile + check-in snapshots.
- Dashboard, plan, and progress views for the current recommendation workflow.

## Repository Layout

- `Backend/` - Django REST Framework API, authentication, profile/check-in models, recommendation engine, notebook pipeline.
- `Frontend/workout-recommender/` - React app with token-aware API client and auth context.
- `docs/` - Architecture, implementation plan, and checklist.

## Backend Quick Start

```bash
cd Backend
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The backend runs on `http://127.0.0.1:8000`.

## Frontend Quick Start

```bash
cd Frontend/workout-recommender
npm install
npm run dev
```

The frontend uses a Vite proxy so `/api/*` requests go to the Django server during development.

## Key API Areas

- `POST /api/auth/register/`, `POST /api/auth/login/`, `POST /api/auth/logout/`
- `GET /api/auth/profile/`
- `GET /api/profiles/`, `POST /api/profiles/`
- `GET /api/checkins/latest/`, `POST /api/checkins/`
- `GET /api/recommendations/latest/`, `POST /api/recommendations/generate/`

## Documentation

- [Backend README](Backend/README.md)
- [Frontend README](Frontend/workout-recommender/README.md)
- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/plan.md)
- [Checklist](docs/checklist.md)
- [Notebook Pipeline Notes](Backend/notebooks/README.md)

## Data And Pipeline

The backend recommendation engine uses the merged dataset and exported model artifacts in `Backend/recommendations/models/`. The pipeline is driven by the notebooks under `Backend/notebooks/` and currently uses profile features such as age, gender, height, weight, BMI, activity level, goal, preference, and medical conditions to select and adjust workout and diet templates.

