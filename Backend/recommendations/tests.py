from types import SimpleNamespace
from unittest import TestCase

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
