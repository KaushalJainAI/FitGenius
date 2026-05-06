import logging
from copy import deepcopy

logger = logging.getLogger('recommendations')

def score_item(name_lower: str, content_score: float, cf_scores: dict, user_memory, item_type: str, context_score: float = 1.0) -> float:
    """
    Computes final hybrid score for an item.
    final_score = 0.45(content) + 0.25(collab) + 0.20(personal) + 0.10(context)
    """
    collab_score = cf_scores.get(name_lower, 0.0)
    
    personal_score = 0.0
    if item_type == 'exercise':
        if name_lower in user_memory.preferred_exercises:
            personal_score = 5.0
        elif name_lower in user_memory.disliked_exercises:
            personal_score = -5.0
    elif item_type == 'meal':
        if name_lower in user_memory.preferred_foods:
            personal_score = 5.0
        elif name_lower in user_memory.disliked_foods:
            personal_score = -5.0
            
    # Normalize collab_score roughly (assuming it can go up to 10 or more)
    norm_collab = min(max(collab_score, -5.0), 5.0)
    
    final_score = (
        0.45 * content_score +
        0.25 * norm_collab +
        0.20 * personal_score +
        0.10 * context_score
    )
    
    return final_score


def get_alternative_exercise(muscle: str, avoid_names: list) -> dict:
    """Very basic fallback if an exercise is rejected."""
    alternatives = {
        'chest': {'name': 'Push-Ups (Kneeling/Wall)', 'muscle': 'Chest', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '10'},
        'back': {'name': 'Resistance Band Rows', 'muscle': 'Back', 'equipment': 'Bands', 'sets': 3, 'reps': '12'},
        'legs': {'name': 'Bodyweight Squats', 'muscle': 'Quads', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '15'},
        'core': {'name': 'Dead Bug', 'muscle': 'Core', 'equipment': 'Bodyweight', 'sets': 3, 'reps': '10/side'},
        'full body': {'name': 'Brisk Walking', 'muscle': 'Cardio', 'equipment': 'None', 'sets': 1, 'reps': '15 min'},
    }
    
    muscle_lower = muscle.lower()
    for key, alt in alternatives.items():
        if key in muscle_lower and alt['name'].lower() not in avoid_names:
            return alt
            
    return alternatives['full body']


def rerank_plan_items(base_plan: dict, cf_exercise_scores: dict, cf_meal_scores: dict, user_memory) -> tuple:
    """
    Reranks and modifies the base plan based on feedback scores.
    Returns (reranked_plan, explanation_notes)
    """
    reranked_plan = deepcopy(base_plan)
    explanation_notes = []
    
    # 1. Rerank Exercises
    exercise_plan = reranked_plan.get('exercise_plan', [])
    avoid_names = [name.lower() for name in user_memory.disliked_exercises]
    
    for day in exercise_plan:
        new_exercises = []
        for ex in day.get('exercises', []):
            name_lower = ex.get('name', '').lower()
            
            # Content score is roughly 3.0 for template baseline
            score = score_item(name_lower, 3.0, cf_exercise_scores, user_memory, 'exercise')
            
            if score < 0 or name_lower in user_memory.disliked_exercises:
                # Replace it
                alt = get_alternative_exercise(ex.get('muscle', ''), avoid_names)
                new_exercises.append(alt)
                avoid_names.append(alt['name'].lower())
                explanation_notes.append(f"Replaced '{ex.get('name')}' with '{alt['name']}' based on your preferences or similar users' feedback.")
            else:
                # Keep it, maybe adjust volume if score is very high (progress difficulty)
                if score > 4.0:
                    ex_copy = dict(ex)
                    sets_val = ex_copy.get('sets', 3)
                    if isinstance(sets_val, int):
                        ex_copy['sets'] = sets_val + 1
                    new_exercises.append(ex_copy)
                    explanation_notes.append(f"Increased volume for '{ex.get('name')}' since you and similar users handle it well.")
                else:
                    new_exercises.append(ex)
                    
        day['exercises'] = new_exercises
        
    reranked_plan['exercise_plan'] = exercise_plan
    
    # 2. Rerank Meals
    diet_plan = reranked_plan.get('diet_plan', {})
    new_diet_plan = {}
    
    for meal_type, meal_desc in diet_plan.items():
        meal_lower = meal_desc.lower()
        score = score_item(meal_lower, 3.0, cf_meal_scores, user_memory, 'meal')
        
        # If score is very low or explicitly disliked
        is_disliked = any(disliked in meal_lower for disliked in user_memory.disliked_foods)
        if score < 0 or is_disliked:
            explanation_notes.append(f"Modified {meal_type} based on your food preferences.")
            new_diet_plan[meal_type] = f"Alternative {meal_type} (Avoiding disliked items)"
        else:
            new_diet_plan[meal_type] = meal_desc
            
    reranked_plan['diet_plan'] = new_diet_plan
    
    return reranked_plan, explanation_notes
