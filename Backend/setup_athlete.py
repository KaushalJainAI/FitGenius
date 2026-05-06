import os
import django
import sys
import io
from datetime import date, timedelta

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

User = get_user_model()

def setup_athlete_profile():
    email = "dummy_user@example.com"
    
    # Get or create User
    user = User.objects.get(email=email)
    print(f"Setting up Athlete data for: {email}")

    # Update Health Profile to Athlete status
    profile, created = HealthProfile.objects.update_or_create(
        user=user,
        defaults={
            'age': 22,
            'gender': 'male',
            'height': 180,
            'weight': 78,
            'fitness_goal': 'endurance',
            'activity_level': 'very_active',
            'exercise_frequency': 6,
            'dietary_preference': 'no_preference',
            'experience_level': 'advanced',
            'available_equipment': 'full_gym',
            'preferred_workout_type': 'mixed',
            'hypertension': False,
            'diabetes': False,
            'smoking_habit': False,
            'alcohol_consumption': 'none',
            'daily_steps': 15000,
            'avg_heart_rate': 55,
        }
    )
    print("Athlete Health Profile updated.")

    # Create historical check-ins for the last 7 days
    for i in range(7):
        checkin_date = date.today() - timedelta(days=i)
        DailyCheckIn.objects.update_or_create(
            user=user,
            date=checkin_date,
            defaults={
                'energy_level': 5 if i != 2 else 3,
                'soreness_level': 2 if i != 2 else 4,
                'sleep_hours': 8.5,
                'daily_steps': 16000 - (i * 500),
                'workout_completed': True,
                'available_minutes': 90,
                'preferred_intensity': 'high',
                'current_weight': 78.0,
            }
        )
    print("Created 7 days of historical Athlete check-ins.")

    return profile, DailyCheckIn.objects.filter(user=user).latest('date')

def generate_athlete_recommendation(profile, checkin):
    print("\n--- Generating Athlete Recommendation ---")
    try:
        result = engine.generate(profile, checkin)
        print(f"Algorithm: {result['algorithm_used']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Similar Profiles Count: {result.get('similar_profiles_count', 0)}")
        print(f"Workout Split: {result['workout_split']}")
        print(f"Calorie Target: {result['daily_calorie_target']} kcal")
        
        print("\nExplanation Snippet:")
        print(result['explanation'][:300] + "...")
        
        print("\nAthlete Diet Plan:")
        for meal, detail in result['diet_plan'].items():
            print(f" - {meal.capitalize()}: {detail}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    profile, checkin = setup_athlete_profile()
    generate_athlete_recommendation(profile, checkin)
