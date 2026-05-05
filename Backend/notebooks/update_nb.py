import json
import os

nb_path = 'c:/Users/91700/Desktop/RS/Project/Backend/notebooks/data_analysis.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Create a much better version of the notebook
cells = []

def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": [text + "\n"]}
def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in text.split("\n")]}

cells.append(md('# FitGenius AI Data Analysis & Model Training\nThis notebook loads the real `merged_fitness_data.csv`, conducts comprehensive data analysis (EDA), and builds the pre-trained KNN model.'))

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
DATA_PATH = './data/merged_fitness_data.csv'
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
    print(f"✓ Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
except FileNotFoundError:
    print(f"ERROR: {DATA_PATH} not found. Run merge_datasets.py first.")
    df = pd.DataFrame()

# Display first few rows
df.head()'''))

cells.append(code('''# Comprehensive info
df.info()'''))

cells.append(code('''# Statistical Summary
df.describe(include='all')'''))

cells.append(md('## 2. In-Depth Exploratory Data Analysis (EDA)\nAnalyzing distributions and correlations in the merged corpus.'))

cells.append(code('''# 1. Age Distribution
plt.figure()
sns.histplot(df['Age'].dropna(), kde=True, color='teal')
plt.title('Distribution of User Ages')
plt.show()'''))

cells.append(code('''# 2. Source Data Distribution
plt.figure()
df['source'].value_counts().plot(kind='pie', autopct='%1.1f%%', colors=sns.color_palette('pastel'))
plt.title('Contributions from Different Data Sources')
plt.ylabel('')
plt.show()'''))

cells.append(code('''# 3. Correlation Heatmap
plt.figure(figsize=(10, 8))
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix of Physiological Metrics')
plt.show()'''))

cells.append(md('## 3. Train K-Nearest Neighbors (KNN)\nMapping user features (Age, Gender, BMI, Disease, Goal) to find closest profiles.'))

cells.append(code('''# Define feature groups for model training
numeric_features = ['Age', 'BMI']
categorical_features = ['Gender', 'Fitness_Goal', 'Chronic_Disease']

# Pre-processing
X_data = df[numeric_features + categorical_features].copy()
for col in numeric_features:
    X_data[col] = pd.to_numeric(X_data[col], errors='coerce').fillna(X_data[col].median())
for col in categorical_features:
    X_data[col] = X_data[col].astype(str).fillna('None')

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

X_transformed = preprocessor.fit_transform(X_data)

knn = NearestNeighbors(n_neighbors=20, metric='cosine')
knn.fit(X_transformed)
print("KNN Model trained successfully with k=20 matches.")'''))

cells.append(md('## 4. Export Models (Static .pkl generation)'))

cells.append(code('''# Save the fitted Preprocessor pipeline
with open(os.path.join(MODEL_DIR, 'preprocessor.pkl'), 'wb') as f:
    pickle.dump(preprocessor, f)

# Save the KNN Model
with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'wb') as f:
    pickle.dump(knn, f)
    
# Export the dataframe as reference pool for Recommendation resolution
df.to_pickle(os.path.join(MODEL_DIR, 'reference_plans.pkl'))

print(f"✓ Exported all .pkl files to {MODEL_DIR} successfully.")'''))

nb['cells'] = cells

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print('Updated data_analysis.ipynb successfully.')
