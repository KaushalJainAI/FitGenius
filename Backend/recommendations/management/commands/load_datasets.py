"""
Management command to load and normalize all 4 CSV datasets
into the DatasetEntry model for the recommendation engine.

Usage:
    python manage.py load_datasets
    python manage.py load_datasets --clear   # Clear existing entries first
    python manage.py load_datasets --source dataset_1  # Load only one dataset

Dataset files should be placed in PROJECT_ROOT/data/:
    - diet_workout_dataset.csv          (Dataset 1 - nimsara55)
    - gym_recommendation.csv            (Dataset 2 - Mendeley)
    - diet_recommendations.csv          (Dataset 3 - ziya07)
    - personalized_medical_diet.csv     (Dataset 4 - ziya07)
"""

import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('recommendations')


class Command(BaseCommand):
    help = 'Load CSV datasets into the DatasetEntry model for the recommendation engine.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing dataset entries before loading.',
        )
        parser.add_argument(
            '--source',
            type=str,
            default='all',
            choices=['all', 'dataset_1', 'dataset_2', 'dataset_3', 'dataset_4'],
            help='Which dataset to load (default: all).',
        )

    def handle(self, *args, **options):
        import pandas as pd
        from recommendations.models import DatasetEntry

        data_dir = settings.DATASET_DIR
        if not data_dir.exists():
            os.makedirs(data_dir, exist_ok=True)
            self.stdout.write(self.style.WARNING(
                f"Created data directory at {data_dir}. "
                f"Please place CSV files there and re-run."
            ))
            return

        if options['clear']:
            count = DatasetEntry.objects.count()
            DatasetEntry.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {count} existing dataset entries."))

        source = options['source']
        total_loaded = 0

        # ==================== DATASET 1 ====================
        if source in ('all', 'dataset_1'):
            total_loaded += self._load_dataset_1(data_dir, pd)

        # ==================== DATASET 2 ====================
        if source in ('all', 'dataset_2'):
            total_loaded += self._load_dataset_2(data_dir, pd)

        # ==================== DATASET 3 ====================
        if source in ('all', 'dataset_3'):
            total_loaded += self._load_dataset_3(data_dir, pd)

        # ==================== DATASET 4 ====================
        if source in ('all', 'dataset_4'):
            total_loaded += self._load_dataset_4(data_dir, pd)

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Total loaded: {total_loaded} dataset entries."
        ))

    def _load_dataset_1(self, data_dir, pd):
        """Diet & Exercise Plan (nimsara55)"""
        filepath = data_dir / 'diet_workout_dataset.csv'
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f"⏭ Skipped Dataset 1: {filepath} not found"))
            return 0

        from recommendations.models import DatasetEntry

        df = pd.read_csv(filepath)
        self.stdout.write(f"📂 Loading Dataset 1: {len(df)} rows from {filepath.name}")

        entries = []
        for _, row in df.iterrows():
            entries.append(DatasetEntry(
                source='dataset_1',
                age=self._safe_int(row.get('Age')),
                gender=self._norm_gender(row.get('Gender', '')),
                height=self._safe_float(row.get('Height')),
                weight=self._safe_float(row.get('Weight')),
                bmi=self._safe_float(row.get('BMI')),
                fitness_goal=self._norm_goal(row.get('Fitness Goal', '')),
                dietary_preference=self._norm_diet(row.get('Diet Type', '')),
                workout_type=str(row.get('Workout Type', '')).strip(),
                exercise_plan=str(row.get('Exercise Plan', '')).strip(),
                diet_recommendation=str(row.get('Meal Plan', '')).strip(),
            ))

        DatasetEntry.objects.bulk_create(entries, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Dataset 1: {len(entries)} entries loaded"))
        return len(entries)

    def _load_dataset_2(self, data_dir, pd):
        """Gym Recommendation (Mendeley)"""
        filepath = data_dir / 'gym_recommendation.csv'
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f"⏭ Skipped Dataset 2: {filepath} not found"))
            return 0

        from recommendations.models import DatasetEntry

        df = pd.read_csv(filepath)
        self.stdout.write(f"📂 Loading Dataset 2: {len(df)} rows from {filepath.name}")

        entries = []
        for _, row in df.iterrows():
            entries.append(DatasetEntry(
                source='dataset_2',
                source_id=str(row.get('ID', '')),
                age=self._safe_int(row.get('Age')),
                gender=self._norm_gender(row.get('Sex', '')),
                height=self._safe_float(row.get('Height')),  # Note: in meters
                weight=self._safe_float(row.get('Weight')),
                bmi=self._safe_float(row.get('BMI')),
                bmi_level=self._norm_bmi_level(row.get('Level', '')),
                hypertension=self._safe_bool(row.get('Hypertension')),
                diabetes=self._safe_bool(row.get('Diabetes')),
                fitness_goal=self._norm_goal(row.get('Fitness Goal', '')),
                fitness_type=str(row.get('Fitness Type', '')).strip(),
                exercise_plan=str(row.get('Exercises', '')).strip(),
                equipment=str(row.get('Equipment', '')).strip(),
                diet_recommendation=str(row.get('Diet', '')).strip(),
                general_recommendation=str(row.get('Recommendation', '')).strip(),
            ))

        # Convert height from meters to cm if needed
        for entry in entries:
            if entry.height and entry.height < 3:  # Likely in meters
                entry.height = round(entry.height * 100, 1)

        DatasetEntry.objects.bulk_create(entries, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Dataset 2: {len(entries)} entries loaded"))
        return len(entries)

    def _load_dataset_3(self, data_dir, pd):
        """Diet Recommendations (ziya07)"""
        filepath = data_dir / 'diet_recommendations.csv'
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f"⏭ Skipped Dataset 3: {filepath} not found"))
            return 0

        from recommendations.models import DatasetEntry

        df = pd.read_csv(filepath)
        self.stdout.write(f"📂 Loading Dataset 3: {len(df)} rows from {filepath.name}")

        entries = []
        for _, row in df.iterrows():
            meal_plan = {}
            if row.get('Breakfast Suggestion'):
                meal_plan['breakfast'] = str(row['Breakfast Suggestion']).strip()
            if row.get('Lunch Suggestion'):
                meal_plan['lunch'] = str(row['Lunch Suggestion']).strip()
            if row.get('Dinner Suggestion'):
                meal_plan['dinner'] = str(row['Dinner Suggestion']).strip()
            if row.get('Snack Suggestion'):
                meal_plan['snacks'] = str(row['Snack Suggestion']).strip()

            entries.append(DatasetEntry(
                source='dataset_3',
                age=self._safe_int(row.get('Age')),
                gender=self._norm_gender(row.get('Gender', '')),
                activity_level=self._norm_activity(row.get('Activity Level', '')),
                dietary_preference=self._norm_diet(row.get('Dietary Preference', '')),
                chronic_disease=str(row.get('Disease', '')).strip(),
                bmi=self._safe_float(row.get('BMI')),
                meal_plan=meal_plan,
                diet_recommendation='; '.join(
                    f"{k}: {v}" for k, v in meal_plan.items()
                ) if meal_plan else '',
            ))

        DatasetEntry.objects.bulk_create(entries, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Dataset 3: {len(entries)} entries loaded"))
        return len(entries)

    def _load_dataset_4(self, data_dir, pd):
        """Personalized Medical Diet Recommendations (ziya07)"""
        filepath = data_dir / 'personalized_medical_diet.csv'
        if not filepath.exists():
            self.stdout.write(self.style.WARNING(f"⏭ Skipped Dataset 4: {filepath} not found"))
            return 0

        from recommendations.models import DatasetEntry

        df = pd.read_csv(filepath)
        self.stdout.write(f"📂 Loading Dataset 4: {len(df)} rows from {filepath.name}")

        entries = []
        for _, row in df.iterrows():
            entries.append(DatasetEntry(
                source='dataset_4',
                source_id=str(row.get('Patient_ID', '')),
                age=self._safe_int(row.get('Age')),
                gender=self._norm_gender(row.get('Gender', '')),
                height=self._safe_float(row.get('Height')),
                weight=self._safe_float(row.get('Weight')),
                bmi=self._safe_float(row.get('BMI')),
                chronic_disease=str(row.get('Chronic_Disease', '')).strip(),
                activity_level=self._norm_activity(row.get('Activity_Level', '')),
                exercise_frequency=self._safe_int(row.get('Exercise_Frequency')),
                daily_steps=self._safe_int(row.get('Daily_Steps')),
                sleep_quality=self._norm_sleep(row.get('Sleep_Quality', '')),
                alcohol_consumption=self._norm_alcohol(row.get('Alcohol_Consumption', '')),
                smoking_habit=self._safe_bool(row.get('Smoking_Habit')),
                caloric_intake=self._safe_float(row.get('Caloric_Intake')),
                protein_intake=self._safe_float(row.get('Protein_Intake')),
                carbohydrate_intake=self._safe_float(row.get('Carbohydrate_Intake')),
                fat_intake=self._safe_float(row.get('Fat_Intake')),
                dietary_preference=self._norm_diet(row.get('Dietary_Habit', '')),
                cuisine_preference=str(row.get('Cuisine_Preference', '')).strip(),
                food_aversion=str(row.get('Food_Aversion', '')).strip(),
                diet_recommendation=str(row.get('Recommended_Diet_Plan', '')).strip(),
            ))

        DatasetEntry.objects.bulk_create(entries, batch_size=500)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Dataset 4: {len(entries)} entries loaded"))
        return len(entries)

    # ==================== NORMALIZATION HELPERS ====================

    @staticmethod
    def _safe_int(value):
        try:
            import math
            v = float(value)
            if math.isnan(v):
                return None
            return int(v)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_float(value):
        try:
            import math
            v = float(value)
            if math.isnan(v):
                return None
            return round(v, 2)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in ('yes', 'true', '1')
        return bool(value) if value is not None else None

    @staticmethod
    def _norm_gender(value):
        v = str(value).strip().lower()
        if v in ('m', 'male'):
            return 'male'
        elif v in ('f', 'female'):
            return 'female'
        return 'other'

    @staticmethod
    def _norm_goal(value):
        v = str(value).strip().lower()
        mapping = {
            'weight loss': 'weight_loss',
            'weight gain': 'weight_gain',
            'muscle gain': 'muscle_gain',
            'maintenance': 'maintenance',
            'endurance': 'endurance',
        }
        return mapping.get(v, v.replace(' ', '_'))

    @staticmethod
    def _norm_diet(value):
        v = str(value).strip().lower()
        mapping = {
            'vegetarian': 'vegetarian',
            'veg': 'vegetarian',
            'non-veg': 'non_veg',
            'non-vegetarian': 'non_veg',
            'non vegetarian': 'non_veg',
            'vegan': 'vegan',
            'regular': 'regular',
            'low_sodium': 'low_sodium',
            'low sodium': 'low_sodium',
            'low_sugar': 'low_sugar',
            'low sugar': 'low_sugar',
            'pescatarian': 'pescatarian',
            'keto': 'keto',
            'paleo': 'paleo',
            'mediterranean': 'mediterranean',
        }
        return mapping.get(v, 'no_preference')

    @staticmethod
    def _norm_activity(value):
        v = str(value).strip().lower()
        mapping = {
            'sedentary': 'sedentary',
            'low': 'low',
            'moderate': 'moderate',
            'moderately active': 'moderate',
            'active': 'active',
            'very active': 'very_active',
            'high': 'very_active',
        }
        return mapping.get(v, 'moderate')

    @staticmethod
    def _norm_sleep(value):
        v = str(value).strip().lower()
        if v in ('poor', 'bad'):
            return 'poor'
        elif v in ('fair', 'average'):
            return 'fair'
        elif v in ('good', 'excellent'):
            return 'good'
        return ''

    @staticmethod
    def _norm_alcohol(value):
        v = str(value).strip().lower()
        if v in ('none', 'no', '0'):
            return 'none'
        elif v in ('occasional', 'moderate', 'social'):
            return 'occasional'
        elif v in ('regular', 'heavy', 'frequent'):
            return 'regular'
        return ''

    @staticmethod
    def _norm_bmi_level(value):
        v = str(value).strip().lower()
        mapping = {
            'underweight': 'underweight',
            'normal': 'normal',
            'overweight': 'overweight',
            'obese': 'obese',
        }
        return mapping.get(v, '')
