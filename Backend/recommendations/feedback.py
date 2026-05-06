from django.db.models import Count, Q
from .models import ExerciseFeedback, MealFeedback, UserPreferenceMemory


def process_feedback(user):
    """
    Process recent feedback from a user and update their UserPreferenceMemory.
    This creates an implicit profile of likes and dislikes.
    """
    memory, _ = UserPreferenceMemory.objects.get_or_create(user=user)

    # Thresholds for moving items into preferred/disliked
    DISLIKE_THRESHOLD = 2
    PREFER_THRESHOLD = 3

    # ==================== EXERCISE PREFERENCES ====================
    # Count bad signals (skipped, too hard, pain, or rating <= 2)
    bad_exercise_signals = ExerciseFeedback.objects.filter(
        user=user
    ).filter(
        Q(skipped=True) | Q(too_hard=True) | Q(pain_reported=True) | Q(rating__lte=2)
    ).values('exercise_name').annotate(count=Count('id'))

    disliked_exercises = set(memory.disliked_exercises)
    for item in bad_exercise_signals:
        if item['count'] >= DISLIKE_THRESHOLD:
            disliked_exercises.add(item['exercise_name'].lower())

    # Count good signals (completed + not too easy/hard + rating >= 4)
    good_exercise_signals = ExerciseFeedback.objects.filter(
        user=user, completed=True
    ).filter(
        Q(rating__gte=4) | Q(rating__isnull=True)  # if completed without explicit rating, still positive
    ).exclude(
        Q(too_hard=True) | Q(pain_reported=True)
    ).values('exercise_name').annotate(count=Count('id'))

    preferred_exercises = set(memory.preferred_exercises)
    for item in good_exercise_signals:
        if item['count'] >= PREFER_THRESHOLD:
            name_lower = item['exercise_name'].lower()
            if name_lower not in disliked_exercises:
                preferred_exercises.add(name_lower)

    memory.disliked_exercises = list(disliked_exercises)
    memory.preferred_exercises = list(preferred_exercises)

    # ==================== MEAL PREFERENCES ====================
    # Count bad signals
    bad_meal_signals = MealFeedback.objects.filter(
        user=user
    ).filter(
        Q(skipped=True) | Q(too_expensive=True) | Q(hard_to_prepare=True) | Q(rating__lte=2)
    ).values('meal_name').annotate(count=Count('id'))

    disliked_foods = set(memory.disliked_foods)
    for item in bad_meal_signals:
        if item['count'] >= DISLIKE_THRESHOLD:
            disliked_foods.add(item['meal_name'].lower())

    # Count good signals
    good_meal_signals = MealFeedback.objects.filter(
        user=user, eaten=True
    ).filter(
        Q(rating__gte=4) | Q(rating__isnull=True)
    ).exclude(
        Q(too_expensive=True) | Q(hard_to_prepare=True)
    ).values('meal_name').annotate(count=Count('id'))

    preferred_foods = set(memory.preferred_foods)
    for item in good_meal_signals:
        if item['count'] >= PREFER_THRESHOLD:
            name_lower = item['meal_name'].lower()
            if name_lower not in disliked_foods:
                preferred_foods.add(name_lower)
                
    # Check for specific disliked ingredients
    disliked_ingredients = MealFeedback.objects.filter(
        user=user
    ).exclude(
        disliked_ingredient=''
    ).values_list('disliked_ingredient', flat=True)
    
    for ingredient in disliked_ingredients:
        if ingredient:
            for ing in ingredient.split(','):
                ing = ing.strip().lower()
                if ing:
                    disliked_foods.add(ing)

    memory.disliked_foods = list(disliked_foods)
    memory.preferred_foods = list(preferred_foods)

    memory.save()
