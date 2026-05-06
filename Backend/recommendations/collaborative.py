from collections import defaultdict
from .models import ExerciseFeedback, MealFeedback
from profiles.models import HealthProfile


def find_similar_user_ids(profile) -> list:
    """Find user IDs with similar basic characteristics (goal, gender)."""
    if not profile.fitness_goal or not profile.gender:
        return []
        
    similar = HealthProfile.objects.filter(
        fitness_goal=profile.fitness_goal,
        gender=profile.gender
    ).exclude(user_id=profile.user_id)
    
    return list(similar.values_list('user_id', flat=True))


def get_exercise_scores_from_similar_users(similar_user_ids: list) -> dict:
    """
    Compute collaborative filtering scores for exercises based on similar users' feedback.
    Returns: { 'exercise_name_lower': total_score }
    """
    if not similar_user_ids:
        return {}

    feedbacks = ExerciseFeedback.objects.filter(user_id__in=similar_user_ids)
    
    scores = defaultdict(float)

    for fb in feedbacks:
        name_lower = fb.exercise_name.lower().strip()
        
        score = 0
        if fb.completed:
            score += 2
        if fb.rating:
            score += fb.rating
        if fb.skipped:
            score -= 2
        if fb.too_hard:
            score -= 1
        if fb.pain_reported:
            score -= 5
            
        scores[name_lower] += score
        
    return dict(scores)


def get_meal_scores_from_similar_users(similar_user_ids: list) -> dict:
    """
    Compute collaborative filtering scores for meals based on similar users' feedback.
    Returns: { 'meal_name_lower': total_score }
    """
    if not similar_user_ids:
        return {}

    feedbacks = MealFeedback.objects.filter(user_id__in=similar_user_ids)
    
    scores = defaultdict(float)

    for fb in feedbacks:
        name_lower = fb.meal_name.lower().strip()
        
        score = 0
        if fb.eaten:
            score += 2
        if fb.rating:
            score += fb.rating
        if fb.skipped:
            score -= 2
        if fb.hard_to_prepare:
            score -= 1
        if fb.too_expensive:
            score -= 1
            
        scores[name_lower] += score
        
    return dict(scores)
