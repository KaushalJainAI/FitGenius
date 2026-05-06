import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from profiles.models import HealthProfile, DailyCheckIn
from recommendations.engine import engine

User = get_user_model()

# Create dummy user
user, created = User.objects.get_or_create(email='test_recommender@example.com', username='test_recommender')
if created:
    user.set_password('password123')
    user.save()

profile, _ = HealthProfile.objects.get_or_create(
    user=user,
    defaults={
        'age': 25,
        'gender': 'male',
        'height': 175,
        'weight': 70,
        'fitness_goal': 'muscle_gain',
        'activity_level': 'moderate',
        'dietary_preference': 'non_veg',
        'available_equipment': 'dumbbells',
    }
)

checkin, _ = DailyCheckIn.objects.get_or_create(
    user=user,
    date='2026-05-06',
    defaults={
        'energy_level': 3,
        'soreness_level': 2,
        'sleep_hours': 8,
        'pain_or_injury': False,
    }
)

print("Running engine.generate...")
try:
    result = engine.generate(profile, checkin)
    print("Success! Algorithm used:", result.get('algorithm_used'))
    print("Days in exercise plan:", len(result.get('exercise_plan', [])))
    explanation = result.get('explanation', '')
    print("Explanation:", explanation.encode('ascii', 'ignore').decode('ascii'))
except Exception as e:
    import traceback
    traceback.print_exc()
