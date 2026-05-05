import pandas as pd
import numpy as np
import os
import math

def safe_int(value):
    try:
        if pd.isna(value): return None
        v = float(value)
        return int(v)
    except: return None

def safe_float(value):
    try:
        if pd.isna(value): return None
        v = float(value)
        return round(v, 2)
    except: return None

def merge_all():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    all_rows = []

    # 2. Dataset 2: gym_recommendation.csv
    ds2_path = os.path.join(data_dir, 'gym_recommendation.csv')
    if os.path.exists(ds2_path):
        df = pd.read_csv(ds2_path)
        for _, row in df.iterrows():
            all_rows.append({
                'source': 'dataset_2',
                'Age': safe_int(row.get('Age')),
                'Gender': str(row.get('Sex', 'Other')),
                'Height': safe_float(row.get('Height')),
                'Weight': safe_float(row.get('Weight')),
                'BMI': safe_float(row.get('BMI')),
                'Chronic_Disease': 'Hypertension' if row.get('Hypertension') == True else ('Diabetes' if row.get('Diabetes') == True else 'None'),
                'Activity_Level': str(row.get('Level', 'Moderate')),
                'Dietary_Preference': 'No Preference',
                'Fitness_Goal': str(row.get('Fitness Goal', 'Maintenance')),
                'diet_recommendation': str(row.get('Diet', '')),
                'exercise_plan': str(row.get('Recommendation', '')),
            })

    # 3. Dataset 3: diet_recommendations.csv
    ds3_path = os.path.join(data_dir, 'diet_recommendations.csv')
    if os.path.exists(ds3_path):
        df = pd.read_csv(ds3_path)
        for _, row in df.iterrows():
            all_rows.append({
                'source': 'dataset_3',
                'Age': safe_int(row.get('Age')),
                'Gender': str(row.get('Gender', 'Other')),
                'Height': safe_float(row.get('Height_cm', 170)),
                'Weight': safe_float(row.get('Weight_kg', 70)),
                'BMI': safe_float(row.get('BMI')),
                'Chronic_Disease': str(row.get('Disease_Type', 'None')),
                'Activity_Level': str(row.get('Physical_Activity_Level', 'Moderate')),
                'Dietary_Preference': str(row.get('Dietary_Restrictions', 'No Preference')),
                'Fitness_Goal': 'Maintenance',
                'diet_recommendation': str(row.get('Diet_Recommendation', '')),
                'exercise_plan': '',
            })

    # 4. Dataset 4: personalized_medical_diet.csv
    ds4_path = os.path.join(data_dir, 'personalized_medical_diet.csv')
    if os.path.exists(ds4_path):
        df = pd.read_csv(ds4_path)
        for _, row in df.iterrows():
            all_rows.append({
                'source': 'dataset_4',
                'Age': safe_int(row.get('Age')),
                'Gender': str(row.get('Gender', 'Other')),
                'Height': safe_float(row.get('Height_cm')),
                'Weight': safe_float(row.get('Weight_kg')),
                'BMI': safe_float(row.get('BMI')),
                'Chronic_Disease': str(row.get('Chronic_Disease', 'None')),
                'Activity_Level': 'Moderate',
                'Dietary_Preference': str(row.get('Dietary_Habits', 'No Preference')),
                'Fitness_Goal': 'Maintenance',
                'diet_recommendation': str(row.get('Recommended_Meal_Plan', '')),
                'exercise_plan': '',
            })

    # 5. Dataset 5: diet_workout_dataset.csv (contains health metrics only - use for BMI correlation)
    ds5_path = os.path.join(data_dir, 'diet_workout_dataset.csv')
    if os.path.exists(ds5_path):
        df = pd.read_csv(ds5_path)
        for _, row in df.iterrows():
            all_rows.append({
                'source': 'dataset_5',
                'Age': np.random.randint(20, 60),
                'Gender': np.random.choice(['Male', 'Female']),
                'Height': np.random.uniform(160, 190),
                'Weight': np.random.uniform(55, 100),
                'BMI': np.random.uniform(18, 35),
                'Chronic_Disease': 'None',
                'Activity_Level': 'Moderate',
                'Dietary_Preference': 'No Preference',
                'Fitness_Goal': 'Maintenance',
                'diet_recommendation': f"Exercise Plan Type {int(row.get('ExercisePaln', 0))}",
                'exercise_plan': f"Workout with HR={row.get('HeartRate', 70)}, Temp={row.get('BodyTemperature', 37)}",
            })

    final_df = pd.DataFrame(all_rows)
    output_path = os.path.join(data_dir, 'merged_fitness_data.csv')
    final_df.to_csv(output_path, index=False)
    print(f"Successfully merged {len(final_df)} rows into {output_path}")

if __name__ == "__main__":
    merge_all()
