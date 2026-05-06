import os
import django
import sys
import io

# Fix encoding for Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Set up Django environment
sys.path.append(os.path.join(os.getcwd()))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import HealthProfile, DailyCheckIn
from recommendations.engine import engine
from recommendations.apps import RecommendationsConfig
from datetime import date

User = get_user_model()

def create_dummy_data():
    email = "dummy_user@example.com"
    password = "dummy_password123"
    
    # Create User
    user, created = User.objects.get_or_create(email=email)
    if created:
        user.set_password(password)
        user.save()
        print(f"Created dummy user: {email}")
    else:
        print(f"User {email} already exists")

    # Create Health Profile (Try to match common patterns in dataset)
    profile, created = HealthProfile.objects.get_or_create(
        user=user,
        defaults={
            'age': 25,
            'gender': 'male',
            'height': 175,
            'weight': 70,
            'fitness_goal': 'muscle_gain',
            'activity_level': 'moderate',
            'dietary_preference': 'non_veg',
            'experience_level': 'intermediate',
            'available_equipment': 'full_gym',
            'preferred_workout_type': 'strength',
            'hypertension': False,
            'diabetes': False,
        }
    )
    if created:
        print("Created dummy health profile")
    else:
        # Update existing profile to ensure we have known data
        profile.age = 25
        profile.gender = 'male'
        profile.height = 175
        profile.weight = 70
        profile.fitness_goal = 'muscle_gain'
        profile.save()
        print("Updated existing health profile")

    # Create Daily Check-In
    checkin, created = DailyCheckIn.objects.get_or_create(
        user=user,
        date=date.today(),
        defaults={
            'energy_level': 4,
            'soreness_level': 2,
            'sleep_hours': 8,
            'available_minutes': 60,
            'preferred_intensity': 'moderate',
        }
    )
    if created:
        print("Created dummy daily check-in")
    else:
        print("Daily check-in for today already exists")

    return profile, checkin

def test_recommendation(profile, checkin):
    print("\n--- Model Check ---")
    print(f"KNN Model Loaded: {RecommendationsConfig.knn_model is not None}")
    print(f"Preprocessor Loaded: {RecommendationsConfig.preprocessor is not None}")
    print(f"Reference Plans Loaded: {RecommendationsConfig.reference_plans is not None}")

    print("\nGenerating recommendation...")
    try:
        result = engine.generate(profile, checkin)
        print("\n--- Recommendation Result ---")
        print(f"Status: {result['status']}")
        print(f"Algorithm Used: {result['algorithm_used']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Similar Profiles Count: {result.get('similar_profiles_count', 0)}")
        print(f"Avg Similarity Score: {result.get('avg_similarity_score')}")
        print(f"Workout Split: {result['workout_split']}")
        print(f"Daily Calorie Target: {result['daily_calorie_target']}")
        
        print("\nExplanation:")
        print(result['explanation'])
        
        print("\nWorkout Plan (Day 1):")
        if result['exercise_plan']:
            day1 = result['exercise_plan'][0]
            print(f"Focus: {day1['focus']}")
            for ex in day1['exercises'][:5]:
                print(f" - {ex['name']} ({ex['sets']} sets x {ex['reps']} reps)")
        
        print("\nDiet Plan:")
        for meal, detail in result['diet_plan'].items():
            print(f" - {meal.capitalize()}: {detail}")
            
        print("\nLLM Insights:")
        print(result.get('llm_recommendation', 'N/A')[:200] + "...")
            
    except Exception as e:
        print(f"Error generating recommendation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    profile, checkin = create_dummy_data()
    test_recommendation(profile, checkin)
