from types import SimpleNamespace
from unittest import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import (
    ExerciseFeedback,
    MealFeedback,
    Recommendation,
    RecommendationFeedback,
)
from .serializers import (
    ExerciseFeedbackSerializer,
    MealFeedbackSerializer,
    RecommendationFeedbackSerializer,
)
from .safety import assess_medical_safety


class MedicalSafetyAssessmentTests(TestCase):
    def test_chest_pain_blocks_with_emergency_level(self):
        assessment = assess_medical_safety(text="I have chest pain. Can I do HIIT?")

        self.assertEqual(assessment["level"], "emergency")
        self.assertTrue(assessment["blocks_plan"])

    def test_kidney_disease_requires_clinician_review(self):
        profile = SimpleNamespace(
            chronic_disease="Kidney disease",
            hypertension=False,
            diabetes=False,
        )

        assessment = assess_medical_safety(profile=profile)

        self.assertEqual(assessment["level"], "clinician_review")
        self.assertTrue(assessment["blocks_plan"])

    def test_knee_pain_is_caution_not_full_block(self):
        profile = SimpleNamespace(
            chronic_disease="",
            hypertension=False,
            diabetes=False,
        )
        checkin = SimpleNamespace(
            pain_or_injury=True,
            injury_area="knee",
            notes="",
            preferred_intensity="low",
            soreness_level=2,
        )

        assessment = assess_medical_safety(profile=profile, checkin=checkin)

        self.assertEqual(assessment["level"], "caution")
        self.assertFalse(assessment["blocks_plan"])

    def test_diabetes_medication_question_requires_clinician_review(self):
        profile = SimpleNamespace(
            chronic_disease="",
            hypertension=False,
            diabetes=True,
        )

        assessment = assess_medical_safety(
            profile=profile,
            text="Should I change my insulin dose before training?",
        )

        self.assertEqual(assessment["level"], "clinician_review")
        self.assertTrue(assessment["blocks_plan"])


class FeedbackSerializerValidationTests(TestCase):
    def test_plan_feedback_rejects_ratings_outside_one_to_five(self):
        serializer = RecommendationFeedbackSerializer(data={
            "rating": 999,
            "difficulty_rating": 0,
            "satisfaction_rating": 6,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)
        self.assertIn("difficulty_rating", serializer.errors)
        self.assertIn("satisfaction_rating", serializer.errors)

    def test_exercise_feedback_rejects_rating_outside_one_to_five(self):
        serializer = ExerciseFeedbackSerializer(data={
            "exercise_name": "Push-Ups",
            "rating": 999,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)

    def test_meal_feedback_rejects_rating_outside_one_to_five(self):
        serializer = MealFeedbackSerializer(data={
            "meal_name": "Oats",
            "meal_type": "breakfast",
            "rating": 999,
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn("rating", serializer.errors)


class RecommendationMetricsTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="metrics-user",
            email="metrics-user@example.com",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="other-metrics-user",
            email="other-metrics-user@example.com",
            password="pass12345",
        )
        self.recommendation = Recommendation.objects.create(
            user=self.user,
            workout_split="Full Body",
        )
        self.other_recommendation = Recommendation.objects.create(
            user=self.other_user,
            workout_split="Full Body",
        )

        RecommendationFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            rating=4,
        )
        ExerciseFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            exercise_name="Push-Ups",
            completed=True,
        )
        MealFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            meal_name="Oats",
            meal_type="breakfast",
            eaten=True,
        )

        RecommendationFeedback.objects.create(
            user=self.other_user,
            recommendation=self.other_recommendation,
            rating=1,
        )
        ExerciseFeedback.objects.create(
            user=self.other_user,
            recommendation=self.other_recommendation,
            exercise_name="Squats",
            completed=False,
        )
        MealFeedback.objects.create(
            user=self.other_user,
            recommendation=self.other_recommendation,
            meal_name="Rice",
            meal_type="lunch",
            eaten=False,
        )

    def test_metrics_are_scoped_to_authenticated_user(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/recommendations/metrics/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["average_plan_rating"], 4)
        self.assertEqual(response.data["workout_completion_rate"], 1)
        self.assertEqual(response.data["meal_completion_rate"], 1)
        self.assertEqual(response.data["feedback_count"], 1)
