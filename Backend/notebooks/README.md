# FitGenius AI Recommendation Engine (Syllabus Alignment)

This directory contains the machine learning pipelines and interactive Jupyter notebooks for the FitGenius AI recommendation engine. The implementation follows the Information Retrieval & Recommender Systems (RS) syllabus by building a normalized health-profile corpus, training a content-based KNN recommender, exporting model artifacts, and demonstrating experimental matrix factorization/evaluation workflows.

## Dataset Information

The engine ingests four primary CSV sources:

| Source file | Rows | Main contribution |
| :--- | ---: | :--- |
| `gym_recommendation.csv` | 14,589 | Fitness goal, diet, exercise recommendation, BMI, hypertension/diabetes flags |
| `diet_recommendations.csv` | 1,000 | Disease type, dietary restrictions, activity level, diet recommendation |
| `personalized_medical_diet.csv` | 5,000 | Chronic disease, lifestyle/medical attributes, recommended meal plan |
| `diet_workout_dataset.csv` | 2,600 | Heart-rate/body-temperature workout and diet-plan signals |

`merge_datasets.py` maps these sources into `data/merged_fitness_data.csv`, a 23,189-row production corpus with 12 normalized columns:

`source`, `Age`, `Gender`, `Height`, `Weight`, `BMI`, `Chronic_Disease`, `Activity_Level`, `Dietary_Preference`, `Fitness_Goal`, `diet_recommendation`, `exercise_plan`.

Some raw files in `data/` are exploratory or currently unused by the production pipeline, including `GYM.csv`, `megaGymDataset.csv`, and the `gym_members_exercise_tracking*.csv` files.

> [!NOTE]
> The `diet_workout_dataset.csv` source does not contain demographics, so the current merge script fills age, gender, height, weight, and BMI synthetically for those rows. This is useful for coursework experimentation but should be documented as a limitation.

## Syllabus Implementation Mapping

### 1. Introduction, Pre-processing, and Matrix Operations (Unit 1)

**File**: `01_data_integration_and_profiling.ipynb`

- Loads the source CSV datasets and profiles missing values, distributions, and correlations.
- Demonstrates how heterogeneous tabular records are normalized into a common user/profile representation.
- Produces exploratory plots for demographic, medical, diet, and workout variables.

### 2. Content-Based Filtering (Unit 2)

**File**: `02_content_based_filtering.ipynb`

- Uses profile features to build user vectors.
- Applies scaling and one-hot encoding to combine numeric and categorical variables.
- Implements cosine-similarity KNN retrieval to find historical profiles similar to a new user.
- Recommends diet/workout outputs from the nearest reference profiles.

### 3. Collaborative Filtering / Latent Factors (Unit 3)

**File**: `03_collaborative_filtering.ipynb`

- Builds an implicit assignment matrix from profile rows and diet recommendations.
- Applies Truncated SVD as an experimental latent-factor component.
- Because the available data does not contain real ratings, clicks, or adoption logs, this should be presented as implicit-label experimentation rather than full collaborative filtering.

### 3b. Synthetic Collaborative Interaction Priors

**File**: `06_synthetic_cf_interactions_analysis.ipynb`

- Profiles `fitgenius_cf_synthetic_interactions.csv.gz`, a simulated interaction telemetry dataset used for collaborative-filtering cold start.
- The file contains synthetic user context, item metadata, ranking scores, simulated behavior (`viewed`, `started_or_eaten`, `completed`, `skipped`, ratings), pain/safety flags, and outcome labels.
- The production backend reads this file through `CF_SYNTHETIC_INTERACTIONS_PATH` and aggregates item-level priors in `recommendations/collaborative.py`.
- The data is intentionally ignored by git under `Backend/data/` because it is a large generated artifact.
- This dataset should not be described as real user behavior, clinical evidence, or medical validation. It is a synthetic prior that is blended at lower weight than real app feedback.

### 4. Hybrid and Context-Aware Approaches (Unit 4 and Unit 6)

**File**: `04_hybrid_and_context_aware.ipynb`

- Combines content-based profile similarity, medical safety rules, template-based plan generation, and nearest-neighbor reference plans.
- Demonstrates context-aware adjustments such as lowering workout intensity when sleep quality is poor or activity level is low.
- Provides a defensible coursework hybrid: retrieve similar cases, filter unsafe options, then personalize the final plan.

### 5. Evaluation Metrics (Unit 5)

**File**: `05_evaluation_metrics.ipynb`

- Evaluates profile/goal prediction and recommendation behavior using offline splits.
- Reports metrics such as classification accuracy/F1, Precision@K, Recall@K, catalog coverage, and list diversity.
- SVD reconstruction error may be reported as an experimental matrix-factorization diagnostic, but it should not be described as validation against real user ratings.

## Production Training Script

**File**: `train_model.py`

Run from `Backend/notebooks`:

```bash
python merge_datasets.py
python train_model.py
```

`train_model.py` reads from `data/merged_fitness_data.csv`, trains the preprocessing pipeline, KNN similarity model, experimental SVD component, and reference plan pool, then exports `.pkl` objects to `../recommendations/models/` for low-latency inference in the Django web application.

## Current Production Model Inputs

The exported preprocessor and KNN model currently use:

- Numeric: `Age`, `Height`, `Weight`
- Categorical: `Gender`, `Chronic_Disease`, `Activity_Level`, `Dietary_Preference`, `Fitness_Goal`

The production reference outputs are:

- `diet_recommendation`
- `exercise_plan`

`BMI` is present in the merged corpus and can be added to the model inputs as a straightforward improvement.
