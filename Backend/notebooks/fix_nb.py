import json
import os

nb_path = 'c:/Users/91700/Desktop/RS/Project/Backend/notebooks/data_analysis.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = []

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": [text + "\n"]}
def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in text.split("\n")]}

cells.append(md('# FitGenius AI Data Analysis & Model Training\nThis notebook loads `gym_members_exercise_tracking.csv`, conducts comprehensive data analysis (EDA), and builds the pre-trained KNN model.'))

cells.append(code('''import pandas as pd
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Setup Paths
DATA_PATH = './data/gym_members_exercise_tracking.csv'
MODEL_DIR = '../recommendations/models/'
os.makedirs(MODEL_DIR, exist_ok=True)

# Set premium aesthetic style for charts
sns.set_theme(style='darkgrid', palette='muted')
plt.rcParams['figure.figsize'] = (10, 6)
'''))

cells.append(md('## 1. Load Data & Basic Profiling'))

cells.append(code('''# Load the actual dataset
try:
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
except FileNotFoundError:
    print(f"ERROR: {DATA_PATH} not found.")

# Display first few rows
df.head()'''))

cells.append(code('''# Comprehensive info
df.info()'''))

cells.append(code('''# Statistical Summary
df.describe(include='all')'''))

cells.append(md('## 2. In-Depth Exploratory Data Analysis (EDA)\nWe analyze missing values, detect distributions, and map correlations.'))

cells.append(code('''# Missing Value Analysis
missing_values = df.isnull().sum()
print("Missing Values:\\n", missing_values[missing_values > 0])
'''))

cells.append(code('''# 1. Distribution of Target Recommendations (Workout Types)
plt.figure()
sns.countplot(y='Workout_Type', data=df, order=df['Workout_Type'].value_counts().index, palette='magma')
plt.title('Distribution of Target Workout Types')
plt.xlabel('Count')
plt.ylabel('Workout Type')
plt.show()'''))

cells.append(code('''# 2. Experience Level vs Calories Burned
plt.figure()
sns.boxplot(x='Experience_Level', y='Calories_Burned', data=df, palette='Set2')
plt.title('Calories Burned Breakdown by Experience Level')
plt.show()'''))

cells.append(code('''# 3. Correlation Heatmap
plt.figure(figsize=(12, 8))
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation between Physiological Metrics')
plt.show()'''))

cells.append(code('''# 4. Pairplot for Key Metrics
sns.pairplot(df[['Age', 'BMI', 'Calories_Burned', 'Experience_Level']], hue='Experience_Level', corner=True)
plt.show()'''))

cells.append(md('## 3. Train K-Nearest Neighbors (KNN)\nWe map user features (Age, Gender, BMI, etc) to find closest profiles.'))

cells.append(code('''# Define feature groups for model training
numeric_features = ['Age', 'Height (m)', 'Weight (kg)', 'BMI']
categorical_features = ['Gender', 'Experience_Level']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

X = df[numeric_features + categorical_features].copy()
for col in numeric_features:
    X[col] = X[col].fillna(X[col].median())
for col in categorical_features:
    X[col] = X[col].fillna(X[col].mode()[0])

X_transformed = preprocessor.fit_transform(X)

knn = NearestNeighbors(n_neighbors=5, metric='cosine')
knn.fit(X_transformed)
print("KNN Model trained successfully.")'''))

cells.append(md('## 4. Export Models (Static .pkl generation)'))

cells.append(code('''# Save the fitted Preprocessor pipeline
with open(os.path.join(MODEL_DIR, 'preprocessor.pkl'), 'wb') as f:
    pickle.dump(preprocessor, f)

# Save the KNN Model
with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'wb') as f:
    pickle.dump(knn, f)
    
df[['Workout_Type']].to_pickle(os.path.join(MODEL_DIR, 'reference_plans.pkl'))

print(f"Exported all .pkl files to {MODEL_DIR} successfully.")'''))

nb['cells'] = cells

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Fixed data_analysis.ipynb successfully.')
