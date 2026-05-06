from collections import defaultdict
import csv
import gzip
import logging
from functools import lru_cache

from django.conf import settings

from .models import ExerciseFeedback, MealFeedback
from profiles.models import HealthProfile

logger = logging.getLogger('recommendations')


def find_similar_user_ids(profile) -> list:
    """Find user IDs with similar basic characteristics (goal, gender)."""
    if not profile.fitness_goal or not profile.gender:
        return []
        
    similar = HealthProfile.objects.filter(
        fitness_goal=profile.fitness_goal,
        gender=profile.gender
    ).exclude(user_id=profile.user_id)
    
    return list(similar.values_list('user_id', flat=True))


def get_synthetic_cf_scores(profile) -> tuple[dict, dict]:
    """
    Aggregate synthetic collaborative interactions for users similar to the profile.
    Returns (exercise_scores, meal_scores).
    """
    rows = _load_synthetic_interactions()
    if not rows:
        return {}, {}

    exercise_scores = defaultdict(float)
    meal_scores = defaultdict(float)
    exercise_counts = defaultdict(int)
    meal_counts = defaultdict(int)

    matched = 0
    for row in rows:
        if not _matches_profile(row, profile):
            continue

        item_name = (row.get('item_name') or '').lower().strip()
        item_type = (row.get('item_type') or '').lower().strip()
        if not item_name or item_type not in {'exercise', 'meal'}:
            continue

        score = _synthetic_row_score(row)
        matched += 1
        if item_type == 'exercise':
            exercise_scores[item_name] += score
            exercise_counts[item_name] += 1
        else:
            meal_scores[item_name] += score
            meal_counts[item_name] += 1

    logger.debug("Loaded %d synthetic CF interactions for profile cohort.", matched)
    return (
        _average_scores(exercise_scores, exercise_counts),
        _average_scores(meal_scores, meal_counts),
    )


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


def merge_cf_scores(*score_maps: dict) -> dict:
    """Merge score maps, preserving real user feedback while adding synthetic priors."""
    merged = defaultdict(float)
    for weight, score_map in score_maps:
        for key, score in (score_map or {}).items():
            merged[key] += float(score) * weight
    return dict(merged)


@lru_cache(maxsize=1)
def _load_synthetic_interactions() -> tuple[dict, ...]:
    path = getattr(settings, 'CF_SYNTHETIC_INTERACTIONS_PATH', None)
    if not path:
        return ()

    path = str(path)
    try:
        opener = gzip.open if path.endswith('.gz') else open
        with opener(path, 'rt', encoding='utf-8', newline='') as file:
            reader = csv.DictReader(file)
            rows = tuple(
                row for row in reader
                if (row.get('data_quality_noise_flag') or 'none') == 'none'
            )
        logger.info("Loaded %d synthetic CF interactions from %s", len(rows), path)
        return rows
    except FileNotFoundError:
        logger.warning("Synthetic CF interactions file not found: %s", path)
    except Exception as exc:
        logger.warning("Failed to load synthetic CF interactions from %s: %s", path, exc)
    return ()


def _matches_profile(row, profile) -> bool:
    goal_aliases = _goal_aliases(getattr(profile, 'fitness_goal', '') or '')
    gender = (getattr(profile, 'gender', '') or '').lower()
    experience = (getattr(profile, 'experience_level', '') or '').lower()
    diet_aliases = _diet_aliases(getattr(profile, 'dietary_preference', '') or '')

    row_goal = _normalize_goal(row.get('fitness_goal', '') or '')
    row_gender = (row.get('gender') or '').lower()
    row_experience = (row.get('experience_level') or '').lower()
    row_diet = _normalize_diet(row.get('diet_preference') or '')

    if row_goal not in goal_aliases:
        return False

    matches = 0
    matches += 1 if row_gender == gender else 0
    matches += 1 if row_experience == experience else 0
    matches += 1 if row_diet in diet_aliases else 0
    return matches >= 2



def _synthetic_row_score(row) -> float:
    score = _to_float(row.get('implicit_feedback_score'), 0.0)
    score += _to_float(row.get('rating_1_5'), 0.0)
    score += 2.0 if _to_bool(row.get('completed')) else 0.0
    score += 1.0 if _to_bool(row.get('started_or_eaten')) else 0.0
    score -= 2.0 if _to_bool(row.get('skipped')) else 0.0
    score -= 5.0 if _to_bool(row.get('pain_reported')) else 0.0
    score -= 8.0 if _to_bool(row.get('safety_violation_flag')) else 0.0
    score += _to_float(row.get('final_rank_score'), 0.0)
    return max(min(score, 8.0), -8.0)


def _average_scores(scores, counts) -> dict:
    averaged = {}
    for key, score in scores.items():
        count = max(counts.get(key, 1), 1)
        averaged[key] = score / count
    return averaged


def _normalize_goal(value: str) -> str:
    mapping = {
        'weight_loss': 'fat_loss',
        'weight_gain': 'muscle_gain',
        'muscle_gain': 'muscle_gain',
        'maintenance': 'general_fitness',
        'endurance': 'heart_health',
    }
    return mapping.get(value.lower(), value.lower())


def _normalize_diet(value: str) -> str:
    mapping = {
        'no_preference': 'any',
        'non_veg': 'non_vegetarian',
        'non-vegetarian': 'non_vegetarian',
        'non vegetarian': 'non_vegetarian',
        'low_sodium': 'low_sodium',
        'low_sugar': 'low_sugar',
    }
    return mapping.get(value.lower(), value.lower())


def _goal_aliases(value: str) -> set[str]:
    normalized = _normalize_goal(value)
    aliases = {normalized}
    if normalized == 'muscle_gain':
        aliases.add('strength')
    if normalized == 'general_fitness':
        aliases.update({'mobility', 'heart_health'})
    return aliases


def _diet_aliases(value: str) -> set[str]:
    normalized = _normalize_diet(value)
    if normalized == 'any':
        return {'non_vegetarian', 'vegetarian', 'eggetarian', 'vegan', 'pescatarian'}
    return {normalized}


def _to_float(value, default=0.0) -> float:
    try:
        if value in (None, ''):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_bool(value) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes', 'y'}
