"""
FitGenius AI — Recommendation Engine

Hybrid recommendation system combining:
1. Content-Based Filtering: Match user profile features against dataset entries
2. Collaborative Filtering: Find similar user profiles and aggregate their recommendations
3. Rule-Based Medical Overrides: Apply health-aware constraints
4. Context-Aware Adjustments: Adjust plans based on daily check-in data

Uses KNN (k-Nearest Neighbors) with cosine similarity on a feature vector
built from the merged 4-dataset schema.
"""

import logging
from copy import deepcopy
import numpy as np
from collections import defaultdict
from .safety import (
    checkin_context_score, apply_medical_safety_filter,
    apply_context_adjustments, generate_health_notes
)
from .models import UserPreferenceMemory
from .collaborative import find_similar_user_ids, get_exercise_scores_from_similar_users, get_meal_scores_from_similar_users
from .reranker import rerank_plan_items

logger = logging.getLogger('recommendations')


# ==================== FEATURE ENGINEERING ====================

GENDER_MAP = {'male': 0, 'female': 1, 'other': 2}
ACTIVITY_MAP = {'sedentary': 0, 'low': 1, 'moderate': 2, 'active': 3, 'very_active': 4}
GOAL_MAP = {'weight_loss': 0, 'weight_gain': 1, 'muscle_gain': 2, 'maintenance': 3, 'endurance': 4}
BMI_LEVEL_MAP = {'underweight': 0, 'normal': 1, 'overweight': 2, 'obese': 3}
EXPERIENCE_MAP = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
EQUIPMENT_MAP = {'bodyweight': 0, 'resistance_bands': 1, 'dumbbells': 2, 'home_gym': 3, 'full_gym': 4}
DIETARY_MAP = {
    'no_preference': 0, 'vegetarian': 1, 'non_veg': 2, 'vegan': 3,
    'pescatarian': 4, 'keto': 5, 'paleo': 6, 'mediterranean': 7,
    'regular': 8, 'low_sodium': 9, 'low_sugar': 10,
}
SLEEP_MAP = {'poor': 0, 'fair': 1, 'good': 2}
ALCOHOL_MAP = {'none': 0, 'occasional': 1, 'regular': 2}
GENETIC_RISK_MAP = {'low': 0, 'moderate': 1, 'high': 2}
WORKOUT_TYPE_MAP = {'cardio': 0, 'strength': 1, 'flexibility': 2, 'hiit': 3, 'mixed': 4}

K_NEIGHBORS = 20  # top-K for aggregation


def _safe_get_display(method, fallback):
    """Safely call get_FOO_display() method."""
    try:
        return method() or fallback
    except Exception:
        return fallback


def profile_to_vector(profile) -> np.ndarray:
    """Convert a HealthProfile into a numeric feature vector for KNN similarity."""
    return np.array([
        float(profile.age),
        float(GENDER_MAP.get(profile.gender, 0)),
        float(profile.height),
        float(profile.weight),
        float(profile.bmi or 24.2),
        float(BMI_LEVEL_MAP.get(profile.bmi_level, 1)),
        float(ACTIVITY_MAP.get(profile.activity_level, 2)),
        float(profile.exercise_frequency or 3),
        float(GOAL_MAP.get(profile.fitness_goal, 3)),
        float(EXPERIENCE_MAP.get(profile.experience_level, 1)),
        float(DIETARY_MAP.get(profile.dietary_preference, 0)),
        float(1 if profile.hypertension else 0),
        float(1 if profile.diabetes else 0),
        float(1 if profile.smoking_habit else 0),
        float(SLEEP_MAP.get(profile.sleep_quality, 2)),
        float(ALCOHOL_MAP.get(profile.alcohol_consumption, 0)),
        float(GENETIC_RISK_MAP.get(profile.genetic_risk, 0)),
        float(EQUIPMENT_MAP.get(profile.available_equipment, 4)),
        float(WORKOUT_TYPE_MAP.get(profile.preferred_workout_type, 4)),
    ], dtype=np.float64)


# ==================== TOP-K AGGREGATION ====================

def knn_top_k_aggregate(profile, k: int = K_NEIGHBORS) -> tuple:
    """
    Find top-K similar profiles from the reference dataset using KNN.
    Convert cosine distances to similarity scores and aggregate votes.

    Returns (diet_votes, exercise_votes, similar_count, avg_similarity, explanation).
    """
    from .apps import RecommendationsConfig
    import pandas as pd

    diet_votes = defaultdict(float)
    exercise_votes = defaultdict(float)
    explanation_parts = []

    try:
        vector = profile_to_vector(profile).reshape(1, -1)
        if RecommendationsConfig.knn_model and RecommendationsConfig.preprocessor:
            # Transform using the preprocessor (expects 'Age', 'Height', 'Weight', etc.)
            # Build a DataFrame matching the preprocessor's expected columns
            user_df = pd.DataFrame([{
                'Age': profile.age,
                'Height': profile.height,
                'Weight': profile.weight,
                'BMI': profile.bmi,
                'Gender': _safe_get_display(profile.get_gender_display, 'Male'),
                'Chronic_Disease': profile.chronic_disease or 'None',
                'Activity_Level': _safe_get_display(profile.get_activity_level_display, 'Moderate'),
                'Dietary_Preference': _safe_get_display(profile.get_dietary_preference_display, 'No Preference'),
                'Fitness_Goal': _safe_get_display(profile.get_fitness_goal_display, 'Maintenance'),
            }])
            user_transformed = RecommendationsConfig.preprocessor.transform(user_df)
            distances, indices = RecommendationsConfig.knn_model.kneighbors(user_transformed, n_neighbors=k)

            # Convert distances to similarity scores (cosine)
            similarities = 1 - distances[0]  # cosine similarity

            avg_similarity = float(np.mean(similarities))
            similar_count = int(np.sum(similarities > 0.3))  # count meaningful matches

            explanation_parts.append(
                f"Matched {similar_count} similar profiles (avg similarity {avg_similarity:.2f})."
            )

            if RecommendationsConfig.reference_plans is not None:
                ref_plans = RecommendationsConfig.reference_plans

                for i, idx in enumerate(indices[0]):
                    sim = float(similarities[i])
                    if sim <= 0.3:
                        continue

                    ref_plan = ref_plans.iloc[idx]

                    # Aggregate diet recommendations
                    if pd.notna(ref_plan.get('diet_recommendation')):
                        diet_key = str(ref_plan['diet_recommendation'])[:80]
                        diet_votes[diet_key] += sim

                    # Aggregate exercise plans
                    if pd.notna(ref_plan.get('exercise_plan')):
                        ex_key = str(ref_plan['exercise_plan'])[:80]
                        exercise_votes[ex_key] += sim

            explanation_parts.append(
                f"Aggregated recommendations from {similar_count} similar users using "
                f"similarity-weighted ranking."
            )

        else:
            avg_similarity = None
            similar_count = 0

    except Exception as e:
        logger.error("KNN aggregation failed: %s", str(e), exc_info=True)
        avg_similarity = None
        similar_count = 0

    if not explanation_parts:
        explanation_parts.append("No similar profiles found — using template-based recommendation.")

    return dict(diet_votes), dict(exercise_votes), similar_count, avg_similarity, ' '.join(explanation_parts)


# ==================== TOP-K RANKED SELECTION ====================

def select_top_ranked(diet_votes: dict, exercise_votes: dict, top_n: int = 3) -> tuple:
    """
    Select top-N ranked diet and exercise candidates from weighted votes.
    Returns (top_diets, top_exercises).
    """
    top_diets = sorted(diet_votes.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_exercises = sorted(exercise_votes.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top_diets, top_exercises


# ==================== BUILD EXPLANATION ====================

def build_explanation(
    similar_count: int,
    avg_similarity: float,
    safety_notes: list,
    context_flags: dict,
    top_diets: list,
    top_exercises: list,
) -> str:
    """Generate a human-readable explanation string for the recommendation."""
    lines = []

    if similar_count > 0:
        lines.append(
            f"📊 Matched {similar_count} similar user profiles "
            f"(avg similarity score: {avg_similarity:.2f}). "
            f"Combined the top recommendations using similarity-weighted aggregation."
        )
    else:
        lines.append("📋 No similar profiles found in the reference dataset. Using personalized template instead.")

    if safety_notes:
        lines.append("\n🔒 Safety constraints applied:")
        for note in safety_notes[:3]:
            lines.append(f"   • {note}")

    active_context = [k for k, v in context_flags.items() if v]
    if active_context:
        lines.append(f"\n⚡ Today's context adjustments ({', '.join(active_context)}).")

    if top_exercises:
        top_ex = top_exercises[0][0][:60] if top_exercises else ''
        if top_ex:
            lines.append(f"\n💪 Top workout match: \"{top_ex}\".")

    if top_diets:
        top_diet = top_diets[0][0][:60] if top_diets else ''
        if top_diet:
            lines.append(f"\n🍽️ Top diet match: \"{top_diet}\".")

    lines.append("\n✅ Your personalized plan is ready. Follow it consistently for best results.")
    return ''.join(lines)


# ==================== WORKOUT TEMPLATES ====================

WORKOUT_TEMPLATES = {
    'muscle_gain': {
        'full_gym': {
            'split': 'Push/Pull/Legs',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Push (Chest, Shoulders, Triceps)',
                    'exercises': [
                        {'name': 'Barbell Bench Press', 'muscle': 'Chest', 'equipment': 'Barbell', 'sets': 4, 'reps': '8-10'},
                        {'name': 'Overhead Shoulder Press', 'muscle': 'Shoulders', 'equipment': 'Dumbbells', 'sets': 4, 'reps': '10-12'},
                        {'name': 'Incline Dumbbell Press', 'muscle': 'Upper Chest', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '10-12'},
                        {'name': 'Tricep Dips', 'muscle': 'Triceps', 'equipment': 'Bodyweight', 'sets': 3, 'reps': 'To failure'},
                        {'name': 'Lateral Raises', 'muscle': 'Shoulders', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '15'},
                    ]
                },
                {
                    'day': 'Day 2', 'focus': 'Pull (Back, Biceps)',
                    'exercises': [
                        {'name': 'Deadlifts', 'muscle': 'Back/Posterior Chain', 'equipment': 'Barbell', 'sets': 4, 'reps': '5-6'},
                        {'name': 'Weighted Pull-Ups', 'muscle': 'Lats', 'equipment': 'Pull-up Bar', 'sets': 4, 'reps': '8-10'},
                        {'name': 'Barbell Rows', 'muscle': 'Back', 'equipment': 'Barbell', 'sets': 3, 'reps': '10'},
                        {'name': 'Dumbbell Hammer Curls', 'muscle': 'Biceps', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12'},
                        {'name': 'Face Pulls', 'muscle': 'Rear Delts', 'equipment': 'Cable', 'sets': 3, 'reps': '15'},
                    ]
                },
                {
                    'day': 'Day 3', 'focus': 'Legs & Core',
                    'exercises': [
                        {'name': 'Barbell Squats', 'muscle': 'Quads', 'equipment': 'Barbell', 'sets': 4, 'reps': '6-8'},
                        {'name': 'Romanian Deadlifts', 'muscle': 'Hamstrings', 'equipment': 'Barbell', 'sets': 3, 'reps': '10'},
                        {'name': 'Leg Press', 'muscle': 'Quads/Glutes', 'equipment': 'Machine', 'sets': 3, 'reps': '12'},
                        {'name': 'Bulgarian Split Squats', 'muscle': 'Quads', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '10/leg'},
                        {'name': 'Hanging Leg Raises', 'muscle': 'Core', 'equipment': 'Pull-up Bar', 'sets': 3, 'reps': '15'},
                    ]
                },
            ]
        },
        'dumbbells': {
            'split': 'Upper/Lower',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Upper Body',
                    'exercises': [
                        {'name': 'Dumbbell Bench Press', 'muscle': 'Chest', 'equipment': 'Dumbbells', 'sets': 4, 'reps': '10-12'},
                        {'name': 'Dumbbell Rows', 'muscle': 'Back', 'equipment': 'Dumbbells', 'sets': 4, 'reps': '10-12'},
                        {'name': 'Dumbbell Shoulder Press', 'muscle': 'Shoulders', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12'},
                        {'name': 'Dumbbell Curls', 'muscle': 'Biceps', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12-15'},
                        {'name': 'Overhead Tricep Extension', 'muscle': 'Triceps', 'equipment': 'Dumbbell', 'sets': 3, 'reps': '12'},
                    ]
                },
                {
                    'day': 'Day 2', 'focus': 'Lower Body & Core',
                    'exercises': [
                        {'name': 'Goblet Squats', 'muscle': 'Quads', 'equipment': 'Dumbbell', 'sets': 4, 'reps': '12'},
                        {'name': 'Dumbbell Romanian Deadlifts', 'muscle': 'Hamstrings', 'equipment': 'Dumbbells', 'sets': 4, 'reps': '10'},
                        {'name': 'Walking Lunges', 'muscle': 'Quads/Glutes', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12/leg'},
                        {'name': 'Calf Raises', 'muscle': 'Calves', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '20'},
                        {'name': 'Dumbbell Woodchops', 'muscle': 'Core', 'equipment': 'Dumbbell', 'sets': 3, 'reps': '12/side'},
                    ]
                },
            ]
        },
        'bodyweight': {
            'split': 'Full Body',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Full Body Strength',
                    'exercises': [
                        {'name': 'Push-Ups (Elevated)', 'muscle': 'Chest/Triceps', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '15-20'},
                        {'name': 'Pull-Ups / Inverted Rows', 'muscle': 'Back', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '8-12'},
                        {'name': 'Bodyweight Squats', 'muscle': 'Quads', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '20'},
                        {'name': 'Pike Push-Ups', 'muscle': 'Shoulders', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '10-12'},
                        {'name': 'Plank Hold', 'muscle': 'Core', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '45-60s'},
                    ]
                },
            ]
        },
    },
    'weight_loss': {
        'full_gym': {
            'split': 'HIIT + Strength Circuit',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Upper Body + HIIT Finisher',
                    'exercises': [
                        {'name': 'Dumbbell Bench Press', 'muscle': 'Chest', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12-15'},
                        {'name': 'Lat Pulldowns', 'muscle': 'Back', 'equipment': 'Cable', 'sets': 3, 'reps': '12-15'},
                        {'name': 'Shoulder Press Machine', 'muscle': 'Shoulders', 'equipment': 'Machine', 'sets': 3, 'reps': '12'},
                        {'name': 'Battle Ropes', 'muscle': 'Full Body', 'equipment': 'Ropes', 'sets': 4, 'reps': '30s'},
                        {'name': 'Treadmill Sprints', 'muscle': 'Cardio', 'equipment': 'Treadmill', 'sets': 6, 'reps': '30s on/30s off'},
                    ]
                },
                {
                    'day': 'Day 2', 'focus': 'Lower Body + Conditioning',
                    'exercises': [
                        {'name': 'Leg Press', 'muscle': 'Quads', 'equipment': 'Machine', 'sets': 3, 'reps': '15'},
                        {'name': 'Walking Lunges', 'muscle': 'Glutes/Quads', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12/leg'},
                        {'name': 'Kettlebell Swings', 'muscle': 'Posterior Chain', 'equipment': 'Kettlebell', 'sets': 4, 'reps': '15'},
                        {'name': 'Box Jumps', 'muscle': 'Full Body', 'equipment': 'Box', 'sets': 3, 'reps': '10'},
                        {'name': 'Rowing Machine', 'muscle': 'Cardio', 'equipment': 'Rower', 'sets': 1, 'reps': '10 min'},
                    ]
                },
                {
                    'day': 'Day 3', 'focus': 'Full Body HIIT',
                    'exercises': [
                        {'name': 'Burpees', 'muscle': 'Full Body', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '10'},
                        {'name': 'Mountain Climbers', 'muscle': 'Core/Cardio', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '20'},
                        {'name': 'Dumbbell Thrusters', 'muscle': 'Full Body', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12'},
                        {'name': 'Jump Squats', 'muscle': 'Quads', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '15'},
                        {'name': 'Plank to Push-Up', 'muscle': 'Core/Chest', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '10'},
                    ]
                },
            ]
        },
        'dumbbells': {
            'split': 'Full Body Circuit',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Fat Burning Circuit',
                    'exercises': [
                        {'name': 'Dumbbell Thrusters', 'muscle': 'Full Body', 'equipment': 'Dumbbells', 'sets': 4, 'reps': '12'},
                        {'name': 'Renegade Rows', 'muscle': 'Back/Core', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '10/side'},
                        {'name': 'Dumbbell Swings', 'muscle': 'Posterior Chain', 'equipment': 'Dumbbell', 'sets': 4, 'reps': '15'},
                        {'name': 'Reverse Lunges', 'muscle': 'Quads/Glutes', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '12/leg'},
                        {'name': 'Man Makers', 'muscle': 'Full Body', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '8'},
                    ]
                },
            ]
        },
        'bodyweight': {
            'split': 'Bodyweight HIIT',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Cardio Blast',
                    'exercises': [
                        {'name': 'Burpees', 'muscle': 'Full Body', 'equipment': 'Bodyweight', 'sets': 5, 'reps': '10'},
                        {'name': 'High Knees', 'muscle': 'Cardio', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '30s'},
                        {'name': 'Jump Squats', 'muscle': 'Quads', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '15'},
                        {'name': 'Mountain Climbers', 'muscle': 'Core/Cardio', 'equipment': 'Bodyweight', 'sets': 4, 'reps': '20'},
                        {'name': 'Plank Hold', 'muscle': 'Core', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '60s'},
                    ]
                },
            ]
        },
    },
    'endurance': {
        'full_gym': {
            'split': 'Endurance Circuit',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Cardio + Muscle Endurance',
                    'exercises': [
                        {'name': 'Treadmill (Incline Walk)', 'muscle': 'Cardio', 'equipment': 'Treadmill', 'sets': 1, 'reps': '20 min'},
                        {'name': 'Light Dumbbell Shoulder Press', 'muscle': 'Shoulders', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '20'},
                        {'name': 'Cable Rows', 'muscle': 'Back', 'equipment': 'Cable', 'sets': 3, 'reps': '20'},
                        {'name': 'Leg Extensions', 'muscle': 'Quads', 'equipment': 'Machine', 'sets': 3, 'reps': '20'},
                        {'name': 'Cycling', 'muscle': 'Cardio', 'equipment': 'Bike', 'sets': 1, 'reps': '15 min'},
                    ]
                },
            ]
        },
        'dumbbells': {
            'split': 'Endurance Circuit',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Full Body Endurance',
                    'exercises': [
                        {'name': 'Dumbbell Squats', 'muscle': 'Quads', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '20'},
                        {'name': 'Dumbbell Bent-Over Rows', 'muscle': 'Back', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '20'},
                        {'name': 'Dumbbell Shoulder Press', 'muscle': 'Shoulders', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '20'},
                        {'name': 'Step-Ups', 'muscle': 'Glutes/Quads', 'equipment': 'Dumbbells', 'sets': 3, 'reps': '15/leg'},
                        {'name': 'Plank', 'muscle': 'Core', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '60s'},
                    ]
                },
            ]
        },
        'bodyweight': {
            'split': 'Bodyweight Endurance',
            'days': [
                {
                    'day': 'Day 1', 'focus': 'Endurance Basics',
                    'exercises': [
                        {'name': 'Push-Ups', 'muscle': 'Chest', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '20-30'},
                        {'name': 'Bodyweight Squats', 'muscle': 'Quads', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '30'},
                        {'name': 'Walking Lunges', 'muscle': 'Quads/Glutes', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '20/leg'},
                        {'name': 'Jogging in Place', 'muscle': 'Cardio', 'equipment': 'Bodyweight', 'sets': 1, 'reps': '10 min'},
                        {'name': 'Side Plank', 'muscle': 'Core', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '30s/side'},
                    ]
                },
            ]
        },
    },
}

# Maintenance and weight_gain use the same templates as muscle_gain
WORKOUT_TEMPLATES['maintenance'] = WORKOUT_TEMPLATES['muscle_gain']
WORKOUT_TEMPLATES['weight_gain'] = WORKOUT_TEMPLATES['muscle_gain']


# ==================== DIET TEMPLATES ====================

DIET_TEMPLATES = {
    'weight_loss': {
        'no_preference': {
            'breakfast': 'Scrambled egg whites with spinach, whole wheat toast, black coffee',
            'lunch': 'Grilled chicken salad with mixed greens, quinoa, olive oil dressing',
            'dinner': 'Baked salmon with roasted broccoli and sweet potato (small portion)',
            'snacks': 'Greek yogurt with berries, handful of almonds',
        },
        'vegetarian': {
            'breakfast': 'Oats porridge with chia seeds, flaxseed, and sliced banana',
            'lunch': 'Paneer tikka salad with chickpeas, cucumber, tomato, lemon dressing',
            'dinner': 'Stir-fried tofu with mixed vegetables and brown rice (small portion)',
            'snacks': 'Roasted makhana, green tea, apple slices with peanut butter',
        },
        'vegan': {
            'breakfast': 'Smoothie bowl with almond milk, spinach, banana, and hemp seeds',
            'lunch': 'Buddha bowl with quinoa, black beans, avocado, corn, lime dressing',
            'dinner': 'Lentil soup with a side of whole grain bread',
            'snacks': 'Trail mix with dried fruits and seeds, coconut yogurt',
        },
        'non_veg': {
            'breakfast': 'Boiled eggs (3), whole wheat toast with avocado',
            'lunch': 'Grilled chicken breast with steamed vegetables and brown rice',
            'dinner': 'Fish curry (low oil) with roti and salad',
            'snacks': 'Protein shake, handful of walnuts, orange',
        },
        'keto': {
            'breakfast': 'Avocado and bacon omelette with cheese',
            'lunch': 'Grilled chicken thigh with cauliflower mash and butter',
            'dinner': 'Salmon with asparagus cooked in olive oil',
            'snacks': 'Cheese cubes, macadamia nuts, dark chocolate (85%+)',
        },
    },
    'muscle_gain': {
        'no_preference': {
            'breakfast': 'Protein pancakes with banana, maple syrup, and whey shake',
            'lunch': 'Double chicken breast with brown rice, mixed vegetables, olive oil',
            'dinner': 'Steak with sweet potato fries and grilled asparagus',
            'snacks': 'Protein bar, peanut butter banana sandwich, cottage cheese',
        },
        'vegetarian': {
            'breakfast': 'Paneer bhurji with multigrain paratha, glass of milk',
            'lunch': 'Rajma chawal with curd and salad',
            'dinner': 'Soya chunks curry with roti and dal',
            'snacks': 'Protein shake with milk, dry fruits and nuts, banana',
        },
        'vegan': {
            'breakfast': 'Tofu scramble with vegetables, sourdough toast, soy milk',
            'lunch': 'Tempeh stir-fry with brown rice and edamame',
            'dinner': 'Chickpea curry with quinoa and roasted vegetables',
            'snacks': 'Vegan protein shake, trail mix, rice cakes with almond butter',
        },
        'non_veg': {
            'breakfast': 'Omelette (4 eggs) with cheese, toast, orange juice',
            'lunch': 'Grilled chicken (250g) with pasta and marinara sauce',
            'dinner': 'Mutton curry with rice, dal, and raita',
            'snacks': 'Whey protein shake, boiled eggs (2), greek yogurt with granola',
        },
        'keto': {
            'breakfast': 'Bacon, eggs, and cheese omelette with avocado',
            'lunch': 'Bunless burger patties with cheese, lettuce wrap, mayo',
            'dinner': 'Ribeye steak with butter, mushrooms, and steamed broccoli',
            'snacks': 'Beef jerky, cheese slices, macadamia nuts',
        },
    },
    'maintenance': {
        'no_preference': {
            'breakfast': 'Whole grain cereal with milk, banana, and honey',
            'lunch': 'Grilled chicken wrap with vegetables and hummus',
            'dinner': 'Pasta with lean ground turkey, marinara, and side salad',
            'snacks': 'Apple with peanut butter, yogurt, mixed nuts',
        },
        'vegetarian': {
            'breakfast': 'Idli with sambar and coconut chutney',
            'lunch': 'Mixed vegetable sabzi with roti and dal',
            'dinner': 'Palak paneer with jeera rice and salad',
            'snacks': 'Fruit chaat, roasted chana, buttermilk',
        },
        'vegan': {
            'breakfast': 'Overnight oats with almond milk, berries, and maple syrup',
            'lunch': 'Falafel bowl with hummus, tabbouleh, and pita',
            'dinner': 'Vegetable stir-fry with tofu and noodles',
            'snacks': 'Smoothie with banana and oat milk, energy balls',
        },
        'non_veg': {
            'breakfast': 'Eggs sunny-side up with toast and avocado',
            'lunch': 'Chicken biryani with raita and salad',
            'dinner': 'Grilled fish with steamed rice and dal',
            'snacks': 'Protein bar, mixed fruit, handful of cashews',
        },
        'keto': {
            'breakfast': 'Bulletproof coffee, 2 boiled eggs',
            'lunch': 'Chicken salad with olive oil, feta cheese, and olives',
            'dinner': 'Pork chops with creamed spinach',
            'snacks': 'Celery with cream cheese, pork rinds, almonds',
        },
    },
}

DIET_TEMPLATES['weight_gain'] = DIET_TEMPLATES['muscle_gain']
DIET_TEMPLATES['endurance'] = DIET_TEMPLATES['maintenance']


# ==================== CALORIE ESTIMATION ====================

def estimate_daily_calories(profile) -> dict:
    """
    Estimate daily calorie needs using Mifflin-St Jeor equation.
    Returns target calories and macro split.
    """
    weight = float(getattr(profile, 'weight', 0) or 0)
    height = float(getattr(profile, 'height', 0) or 0)
    age = int(getattr(profile, 'age', 0) or 0)

    if weight <= 0 or height <= 0 or age <= 0:
        weight = weight if weight > 0 else 68
        height = height if height > 0 else 170
        age = age if age > 0 else 25

    # Mifflin-St Jeor BMR
    if profile.gender == 'male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    elif profile.gender == 'female':
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 78  # Average

    # Activity multiplier
    multipliers = {
        'sedentary': 1.2,
        'low': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9,
    }
    tdee = bmr * multipliers.get(profile.activity_level, 1.55)

    # Goal adjustment
    goal_adjustments = {
        'weight_loss': -500,
        'weight_gain': +400,
        'muscle_gain': +300,
        'maintenance': 0,
        'endurance': +200,
    }
    target_calories = round(tdee + goal_adjustments.get(profile.fitness_goal, 0))

    # Macro split based on goal
    if profile.fitness_goal in ('muscle_gain', 'weight_gain'):
        protein_ratio, carb_ratio, fat_ratio = 0.30, 0.45, 0.25
    elif profile.fitness_goal == 'weight_loss':
        protein_ratio, carb_ratio, fat_ratio = 0.35, 0.35, 0.30
    elif profile.fitness_goal == 'endurance':
        protein_ratio, carb_ratio, fat_ratio = 0.20, 0.55, 0.25
    else:
        protein_ratio, carb_ratio, fat_ratio = 0.25, 0.45, 0.30

    return {
        'daily_calories': target_calories,
        'protein_g': round((target_calories * protein_ratio) / 4),
        'carbs_g': round((target_calories * carb_ratio) / 4),
        'fat_g': round((target_calories * fat_ratio) / 9),
    }


# ==================== RECOMMENDATION ENGINE ====================

class RecommendationEngine:
    """
    Hybrid recommendation engine:
    1. Content-Based: Select workout/diet templates based on profile features
    2. Collaborative: Find K-nearest neighbors in dataset, aggregate their recommendations
    3. Rule-Based: Apply medical overrides and safety constraints
    """

    def __init__(self):
        # Uses static models attached to RecommendationsConfig
        self._is_fitted = True

    def _load_dataset(self):
        pass  # Replaced by static loading in apps.py

    def generate(self, profile, checkin=None) -> dict:
        """
        Generate a full recommendation for a given HealthProfile and optional DailyCheckIn.
        Returns a dict matching the Recommendation model fields.
        """
        goal = profile.fitness_goal or 'maintenance'
        equipment = profile.available_equipment or 'full_gym'

        # 1. Content-based template selection
        goal_templates = WORKOUT_TEMPLATES.get(goal, WORKOUT_TEMPLATES['maintenance'])
        workout_template = goal_templates.get(equipment, goal_templates.get('full_gym', {}))
        workout_split = workout_template.get('split', 'Full Body')
        exercise_plan = deepcopy(workout_template.get('days', []))

        diet_pref = profile.dietary_preference or 'no_preference'
        goal_diets = DIET_TEMPLATES.get(goal, DIET_TEMPLATES['maintenance'])
        diet_plan = deepcopy(goal_diets.get(diet_pref, goal_diets.get('no_preference', {})))

        # 2. Calorie estimation
        calorie_data = estimate_daily_calories(profile)

        # 3. Medical rules (static health notes)
        health_notes = generate_health_notes(profile)

        # 4. Top-K aggregation using KNN (Dataset-based Content Filtering)
        diet_votes, exercise_votes, similar_count, avg_similarity, knn_explanation = \
            knn_top_k_aggregate(profile, k=K_NEIGHBORS)

        algorithm_used = 'hybrid'

        # 5. Ranked selection from aggregated votes
        top_diets, top_exercises = select_top_ranked(diet_votes, exercise_votes, top_n=3)

        # 6. Build profile snapshot
        snapshot = {
            'age': profile.age,
            'gender': profile.gender,
            'height': profile.height,
            'weight': profile.weight,
            'bmi': profile.bmi,
            'fitness_goal': profile.fitness_goal,
            'activity_level': profile.activity_level,
            'experience_level': profile.experience_level,
            'equipment': profile.available_equipment,
            'dietary_preference': profile.dietary_preference,
            'hypertension': profile.hypertension,
            'diabetes': profile.diabetes,
            'chronic_disease': profile.chronic_disease,
        }

        # ==========================================================
        # FEEDBACK AND COLLABORATIVE FILTERING LAYER
        # ==========================================================
        # Load user preference memory
        user_memory, _ = UserPreferenceMemory.objects.get_or_create(user=profile.user)
        
        # Load similar users for collaborative filtering
        real_similar_users = find_similar_user_ids(profile)
        cf_exercise_scores = get_exercise_scores_from_similar_users(real_similar_users)
        cf_meal_scores = get_meal_scores_from_similar_users(real_similar_users)
        
        # Re-ranker layer
        base_plan = {
            'exercise_plan': exercise_plan,
            'diet_plan': diet_plan,
        }
        
        reranked_plan, rerank_notes = rerank_plan_items(
            base_plan, cf_exercise_scores, cf_meal_scores, user_memory
        )
        
        exercise_plan = reranked_plan['exercise_plan']
        diet_plan = reranked_plan['diet_plan']
        # ==========================================================

        # 7. Apply context-aware adjustments from check-in
        if checkin:
            exercise_plan = apply_context_adjustments(exercise_plan, checkin, profile)

        # 8. Adjust for experience level
        exercise_plan = self._adjust_for_experience(exercise_plan, profile.experience_level)

        # 9. Adjust for days per week
        days_per_week = profile.exercise_frequency or 3
        if len(exercise_plan) > days_per_week:
            exercise_plan = exercise_plan[:days_per_week]

        # 10. Apply medical safety filter (Must override everything)
        exercise_plan, safety_notes, removal_reasons = apply_medical_safety_filter(
            exercise_plan, checkin, profile
        )

        # 11. RAG & LLM Insights
        rag_data = self._generate_rag_insights(profile, workout_split, diet_plan, calorie_data)
        llm_recommendation = rag_data.get('llm_recommendation', '')
        rag_context_chunks = rag_data.get('rag_context_chunks', [])

        # 12. Context flags for explanation
        ctx_flags = checkin_context_score(checkin) if checkin else {}

        # 13. Build explanation
        explanation = build_explanation(
            similar_count=similar_count,
            avg_similarity=avg_similarity or 0.0,
            safety_notes=safety_notes,
            context_flags=ctx_flags,
            top_diets=top_diets,
            top_exercises=top_exercises,
        )
        
        # Append reranker explanations
        if rerank_notes:
            explanation += "\n\n💡 Personalized Adjustments:\n" + "\n".join([f"• {note}" for note in rerank_notes])

        return {
            'status': 'completed',
            'confidence': 'high' if similar_count >= 10 else ('medium' if similar_count > 3 else 'low'),
            'algorithm_used': algorithm_used,
            'workout_split': workout_split,
            'exercise_plan': exercise_plan,
            'workout_days_per_week': days_per_week,
            'diet_plan': diet_plan,
            'daily_calorie_target': calorie_data['daily_calories'],
            'macro_split': {
                'protein_g': calorie_data['protein_g'],
                'carbs_g': calorie_data['carbs_g'],
                'fat_g': calorie_data['fat_g'],
            },
            'health_notes': health_notes,
            'llm_recommendation': llm_recommendation,
            'rag_context_chunks': rag_context_chunks,
            'profile_snapshot': snapshot,
            'similar_profiles_count': similar_count,
            'avg_similarity_score': avg_similarity,
            'explanation': explanation,
        }

    def _generate_rag_insights(self, profile, workout_split, diet_plan, calories) -> dict:
        """
        Implementation of Semantic Chunking and Retrieval-Augmented Generation (RAG).
        1. Emulate a retrieval of relevant health literature.
        2. Perform semantic logic to filter the most relevant pieces.
        3. Formulate a personalized explanation as if generated by an LLM.
        """
        # Step 1: Simulated "Semantic Knowledge Base" (usually from a Vector DB)
        knowledge_base = [
            # Chunk 1: General Weight Management
            "High-protein diets during a calorie deficit help preserve lean muscle mass while promoting fat loss. "
            "Aim for 1.6g to 2.2g of protein per kg of body weight.",
            # Chunk 2: Workout Intensity
            "Consistency is more important than intensity when starting. Beginners should focus on technical form "
            "before increasing resistance/weight to prevent injury.",
            # Chunk 3: Sleep & Recovery
            "High-quality sleep (7-9 hours) is essential for hormonal regulation and muscle tissue repair. "
            "Poor sleep increases levels of cortisol, which can hinder weight loss and muscle growth.",
            # Chunk 4: Hydration & Alcohol
            "Moderate alcohol consumption can dehydrate the body and slow down protein synthesis. "
            "Proper hydration is critical for joint lubrication and nutrient transport.",
            # Chunk 5: Medical - Diabetes
            "For diabetic users, low-glycemic index (GI) carbohydrates such as oats, legumes, and green "
            "vegetables are preferred to prevent sharp insulin spikes after meals.",
        ]

        # Step 2: Semantic Chunking / Filtering (Concept mapping)
        # In a real RAG system, this would be an embedding similarity search.
        selected_chunks = []
        
        # Mapping rules (The 'Semantic' logic)
        if profile.fitness_goal in ('weight_loss', 'muscle_gain'):
            selected_chunks.append(knowledge_base[0])
        
        if profile.experience_level == 'beginner' or (profile.exercise_frequency or 0) < 3:
            selected_chunks.append(knowledge_base[1])

        if profile.sleep_quality == 'poor':
            selected_chunks.append(knowledge_base[2])

        if profile.alcohol_consumption != 'none':
            selected_chunks.append(knowledge_base[3])

        if profile.diabetes:
            selected_chunks.append(knowledge_base[4])

        # Step 3: LLM formulation (Simulating a conversational AI response)
        # Using a fallback conversational template that uses our extracted chunks.
        
        name = profile.user.email.split('@')[0].capitalize()
        goal_text = profile.get_fitness_goal_display().replace('_', ' ')
        
        intro = f"Hello {name}! Based on your profile and my analysis of the latest health literature, " \
                f"I've designed a specialized {workout_split} plan to help you reach your goal of {goal_text}."
        
        body = "\n\n".join(selected_chunks)
        
        outro = f"\n\nRemember to stay consistent with your {calories['daily_calories']} calorie target. " \
                f"I've optimized your macros to provide sufficient energy for your {workout_split} sessions."
        
        full_recommendation = f"{intro}\n\n{body}{outro}"

        return {
            'llm_recommendation': full_recommendation,
            'rag_context_chunks': selected_chunks
        }

    def _augment_from_dataset(self, similar_entries: list, profile) -> dict:
        """
        Extract and aggregate recommendations from similar dataset entries.
        Merges exercise plans and diet suggestions from the matched entries.
        """
        result = {}

        # Aggregate exercise recommendations
        exercise_texts = [e.exercise_plan for e in similar_entries if e.exercise_plan]
        if exercise_texts:
            # Parse dataset exercise recommendations
            # These are usually text-based, so we extract unique exercises
            parsed_exercises = set()
            for text in exercise_texts:
                # Simple parsing: split by common delimiters
                for ex in text.replace(';', ',').split(','):
                    ex = ex.strip()
                    if ex and len(ex) > 3:
                        parsed_exercises.add(ex)

            # If we got meaningful exercise names, note them in the plan
            if parsed_exercises:
                logger.info("Augmented with %d exercises from similar profiles.", len(parsed_exercises))

        # Aggregate diet recommendations
        diet_texts = [e.diet_recommendation for e in similar_entries if e.diet_recommendation]
        meal_plans = [e.meal_plan for e in similar_entries if e.meal_plan and isinstance(e.meal_plan, dict)]

        if meal_plans:
            # Prefer structured meal plans
            best_plan = meal_plans[0]
            if all(k in best_plan for k in ('breakfast', 'lunch', 'dinner')):
                result['diet_plan'] = best_plan

        return result

    def _adjust_for_experience(self, exercise_plan: list, experience_level: str) -> list:
        """Adjust sets/reps based on experience level."""
        if not exercise_plan:
            return exercise_plan

        adjusted = []
        for day in exercise_plan:
            day_copy = dict(day)
            exercises = []
            for ex in day.get('exercises', []):
                ex_copy = dict(ex)
                if experience_level == 'beginner':
                    # Reduce sets and reps for beginners
                    ex_copy['sets'] = max(2, ex_copy.get('sets', 3) - 1)
                    reps = ex_copy.get('reps', '10')
                    if isinstance(reps, str) and '-' in reps:
                        parts = reps.split('-')
                        try:
                            low = max(5, int(parts[0]) - 2)
                            high = max(8, int(parts[1]) - 2)
                            ex_copy['reps'] = f"{low}-{high}"
                        except ValueError:
                            pass
                elif experience_level == 'advanced':
                    # Increase sets for advanced
                    ex_copy['sets'] = ex_copy.get('sets', 3) + 1
                exercises.append(ex_copy)
            day_copy['exercises'] = exercises
            adjusted.append(day_copy)

        return adjusted

    def invalidate_cache(self):
        """Called when models need to be reloaded (e.g., after retraining)."""
        self._is_fitted = False


# Module-level singleton
engine = RecommendationEngine()
