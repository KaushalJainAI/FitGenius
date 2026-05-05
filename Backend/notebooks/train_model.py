import pandas as pd
import numpy as np
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD

# Paths - use relative paths from the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'data', 'merged_fitness_data.csv')
MODEL_DIR = os.path.join(SCRIPT_DIR, '..', 'recommendations', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    """ Load the real merged dataset """
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        print(f"[OK] Loaded merged data from {DATA_FILE} ({len(df)} rows)")
        return df
    
    raise FileNotFoundError(f"ERROR: {DATA_FILE} not found. Run merge_datasets.py first.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    df = load_data()
    
    # Define features matching the merged dataset schema
    numeric_features = ['Age', 'Height', 'Weight', 'BMI']
    categorical_features = ['Gender', 'Chronic_Disease', 'Activity_Level', 'Dietary_Preference', 'Fitness_Goal']
    
    # Pre-processing with safe handling
    for col in categorical_features:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna('None')
        else:
            df[col] = 'None'
    
    for col in numeric_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val if not np.isnan(median_val) else 25.0)
        else:
            df[col] = 25.0
    
    # Fill target variables
    df['diet_recommendation'] = df['diet_recommendation'].fillna('Balanced Nutrition Plan').astype(str)
    df['exercise_plan'] = df['exercise_plan'].fillna('General Fitness Routine').astype(str)

    print("[OK] Fitting Scalers and Encoders for Hybrid Recommendation Engine...")
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    X = df[numeric_features + categorical_features]
    X_transformed = preprocessor.fit_transform(X)
    
    # 2. Content-Based Model: KNN Similarity
    print("[OK] Training K-Nearest Neighbors...")
    knn = NearestNeighbors(n_neighbors=20, metric='cosine')
    knn.fit(X_transformed)
    
    # 3. Collaborative Filtering Model: SVD
    print("[OK] Training Matrix Factorization (SVD)...")
    interaction_matrix = pd.crosstab(df.index, df['diet_recommendation'])
    
    if interaction_matrix.shape[1] > 1:
        n_components = min(12, interaction_matrix.shape[1]-1)
        svd = TruncatedSVD(n_components=n_components, random_state=42)
        svd.fit(interaction_matrix)
    else:
        svd = None
        print("[WARN] Warning: Not enough unique diet recommendations for SVD")
    
    # 4. Exporting the Hybrid Models
    print(f"\n[OK] Exporting models to {MODEL_DIR}")
    
    with open(os.path.join(MODEL_DIR, 'preprocessor.pkl'), 'wb') as f:
        pickle.dump(preprocessor, f)
        
    with open(os.path.join(MODEL_DIR, 'knn_model.pkl'), 'wb') as f:
        pickle.dump(knn, f)
        
    if svd is not None:
        with open(os.path.join(MODEL_DIR, 'svd_model.pkl'), 'wb') as f:
            pickle.dump(svd, f)
    
    # Export the dataframe as reference pool
    df.to_pickle(os.path.join(MODEL_DIR, 'reference_plans.pkl'))
    
    print("[OK] Export Complete! Models synchronized with engine.py.")
