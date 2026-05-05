# FitGenius AI - Workout & Diet Recommender

Welcome to the **FitGenius AI Recommender System**. This repository contains both the React frontend and the Django backend required to run the personalized fitness platform. The system uses four primary health and fitness CSV datasets, normalizes them into a shared recommendation schema, and combines similarity matching with rule-based diet/workout generation.

## System Features
- JWT Secure Authentication (HttpOnly Cookies)
- Comprehensive User Health Profiles (Demographics, Medical History, Lifestyle input)
- Machine Learning recommendation engine using KNN profile similarity, exported preprocessing artifacts, and a reference pool of historical diet/workout plans.
- Fully responsive Dashboard UI for tracking daily plans.

## Directory Structure
- `/Backend` - Django REST Framework project
- `/Frontend/workout-recommender` - React application built with Vite
- `/docs` - Project architecture, implementation plan, and execution checklist

## Project Documentation

Use this README as the entry point for the project. Supporting documents are kept under `docs/`:

- [Architecture](docs/architecture.md) - system components, dataset layer, and backend/frontend data flow.
- [Implementation Plan](docs/plan.md) - planned backend, frontend, model, and demo upgrades for the dynamic recommender.
- [Implementation Checklist](docs/checklist.md) - task checklist for building and verifying the coursework-ready system.
- [Notebook Pipeline Notes](Backend/notebooks/README.md) - dataset details, notebook mapping, and model-training notes.

## Getting Started

### Local Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd Backend
   ```
2. Activate the virtual environment:
   ```bash
   # Windows
   .\venv\Scripts\activate
   ```
3. Install requirements (if not already):
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations and start the server:
   ```bash
   python manage.py runserver
   ```

### Local Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd Frontend/workout-recommender
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Dataset Merging
The notebook pipeline under `Backend/notebooks` merges four source files into `Backend/notebooks/data/merged_fitness_data.csv`:

| Source file | Rows | Main contribution |
| :--- | ---: | :--- |
| `gym_recommendation.csv` | 14,589 | Fitness goal, diet, exercise recommendation, BMI, hypertension/diabetes flags |
| `diet_recommendations.csv` | 1,000 | Disease type, dietary restrictions, activity level, diet recommendation |
| `personalized_medical_diet.csv` | 5,000 | Chronic disease, medical/lifestyle attributes, personalized meal plan |
| `diet_workout_dataset.csv` | 2,600 | Heart-rate/body-temperature workout and diet-plan signals |

The merged production corpus currently has 23,189 rows and 12 normalized columns:

`source`, `Age`, `Gender`, `Height`, `Weight`, `BMI`, `Chronic_Disease`, `Activity_Level`, `Dietary_Preference`, `Fitness_Goal`, `diet_recommendation`, `exercise_plan`.

Run the pipeline from `Backend/notebooks`:

```bash
python merge_datasets.py
python train_model.py
```

`train_model.py` fits the preprocessing pipeline, KNN similarity model, experimental SVD model, and reference plan pool, then exports `.pkl` artifacts to `Backend/recommendations/models/`.
