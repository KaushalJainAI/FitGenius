# FitGenius AI - Assignment Notebooks Documentation

## Overview

This document explains the 5 assignment notebooks that implement a fitness recommendation system aligned with the Information Retrieval & Recommender Systems (RS) syllabus.

---

## Notebook 1: Data Integration and Profiling (`01_data_integration_and_profiling.ipynb`)

### Purpose
Performs exploratory data analysis (EDA) on 4 source datasets before merging them into a unified 30-feature corpus.

### Source Datasets
| Dataset | Shape | Source |
|---------|-------|--------|
| `gym_recommendation.csv` | 14,589 x 15 | Mendeley |
| `diet_recommendations.csv` | 1,000 x 20 | nimsara55 |
| `personalized_medical_diet.csv` | 5,000 x 30 | ziya07 |
| `diet_workout_dataset.csv` | 2,600 x 5 | ziya07 |

### Technical Details

#### Missing Data Handling
- Uses heatmap visualization (`sns.heatmap`) to identify missing values
- Numeric features filled with median values
- Categorical features filled with 'None'

#### Preprocessing Pipeline
1. **Missing Value Detection**: Visual heatmaps per dataset
2. **Distribution Analysis**: Histograms for physique metrics (Age, Height, Weight, BMI)
3. **Categorical Analysis**: Count plots for Gender, Chronic_Disease, Fitness_Goal, Activity_Level
4. **Correlation Heatmaps**: `np.triu()` mask with `sns.heatmap` for feature correlations

#### Merged Dataset
- Final unified dataset: `merged_fitness_data.csv` with ~23,000 rows
- Violin plots for BMI by Gender and Chronic_Disease status
- Box plots for Age Demographics by Activity_Level

#### Key Visualizations
- Missing data density heatmaps
- Physique feature distributions
- Categorical frequency counts
- Feature correlation heatmaps

---

## Notebook 2: Content-Based Filtering (`02_content_based_filtering.ipynb`)

### Purpose
Implements feature extraction and similarity-based retrieval using K-Nearest Neighbors (KNN).

### Syllabus Alignment
**Unit 2: Feature Extraction and Similarity Retrieval**

### Technical Details

#### Preprocessing Pipeline
```python
ColumnTransformer([
    ('num', StandardScaler(), ['Age', 'Height', 'Weight']),
    ('cat', OneHotEncoder(handle_unknown='ignore'), 
     ['Gender', 'Chronic_Disease', 'Activity_Level', 'Dietary_Preference', 'Fitness_Goal'])
])
```

#### Model: K-Nearest Neighbors
```python
NearestNeighbors(n_neighbors=5, metric='cosine')
```

#### Algorithm Flow
1. **Feature Scaling**: `StandardScaler` normalizes numeric features (Age, Height, Weight)
2. **One-Hot Encoding**: `OneHotEncoder` converts categorical features to binary vectors
3. **Vector Space Model**: Combined features create user profile vectors
4. **Cosine Similarity**: KNN finds 5 most similar historical users based on vector distance
5. **Recommendation**: Returns diet/exercise plans from similar users

#### Key Concepts
- **User Profile Vector**: Concatenation of scaled numeric + one-hot encoded categorical features
- **Cosine Similarity**: `cosine_distance = 1 - cosine_similarity` measures angle between vectors
- **KNN Retrieval**: Returns k nearest neighbors in the feature space

---

## Notebook 3: Collaborative Filtering (`03_collaborative_filtering.ipynb`)

### Purpose
Implements Matrix Factorization using Truncated SVD to discover latent relationships between users and recommendations.

### Syllabus Alignment
**Unit 3: Matrix Factorization and Latent Factors**

### Technical Details

#### Interaction Matrix
```python
interaction_matrix = pd.crosstab(user_index, diet_recommendation)
```
- Rows: User indices (~18,551 unique users)
- Columns: Unique diet plans (~22 plans)
- Values: Implicit interaction counts

#### Matrix Factorization (Truncated SVD)
```python
svd = TruncatedSVD(n_components=10, random_state=42)
latent_space = svd.fit_transform(interaction_matrix)
```

#### Latent Space Interpretation
Each of the 10 latent factors represents hidden patterns:
- User fitness levels (beginner vs advanced)
- Health conditions (diabetic vs healthy)
- Dietary restrictions (vegan vs non-veg)
- Workout preferences (cardio vs strength)

#### Performance Metrics
- **Explained Variance Ratio**: ~72.31% - indicates how much variance the latent factors capture
- **Reconstruction Error (RMSE)**: 0.1087 - difference between original and reconstructed matrix

#### Algorithm Flow
1. **Build Interaction Matrix**: `crosstab` of users vs diet plans
2. **Apply SVD**: Decomposes matrix into user latent factors and item latent factors
3. **Reconstruct**: `inverse_transform` predicts ratings for unseen user-item pairs
4. **Output**: User embeddings ready for hybrid integration

---

## Notebook 4: Hybrid and Context-Aware (`04_hybrid_and_context_aware.ipynb`)

### Purpose
Implements cascade hybrid filtering with medical safety constraints and context-aware score adjustments.

### Syllabus Alignment
**Unit 4 & 6: Cascading Filters and Safety Constraints**

### Technical Details

#### Cascade Hybrid Architecture
```
Input User Profile → Content-Based Filter → Medical Safety Filter → Collaborative Ranking → Final Recommendations
```

#### Medical Safety Filter (Hard Constraints)
```python
def cascade_filter(plans, health_record):
    chronic_disease = str(health_record.get('Chronic_Disease', '')).lower()
    if 'diabetes' in chronic_disease or health_record.get('diabetes'):
        return [p for p in plans if 'Sugar' not in str(p)]  # Remove high-sugar plans
    return plans
```
- **Purpose**: Prevents harmful recommendations for diabetic users
- **Logic**: Removes diet plans containing "Sugar" for diabetes patients

#### Context-Aware Score Adjustment
```python
def context_aware_adjustment(score, context):
    sleep_quality = context.get('Sleep_Quality', 'Good')
    if sleep_quality == 'Poor':
        score *= 0.8  # Reduce high-intensity workout confidence
    
    daily_steps = context.get('Daily_Steps', 0)
    if daily_steps < 5000:
        score *= 0.9  # Further reduce based on activity
    return score
```

#### Contextual Features
| Context Signal | Adjustment |
|----------------|------------|
| Poor Sleep Quality | Score × 0.8 |
| Daily Steps < 5000 | Score × 0.9 |

#### Hybrid Strategy
1. **Primary Filter**: Content-based KNN similarity scores
2. **Medical Constraints**: Hard filter removes unsafe recommendations
3. **Collaborative Ranking**: SVD-based scores re-rank remaining candidates
4. **Context Adjustment**: Final scores modulated by wearable data

---

## Notebook 5: Evaluation Metrics (`05_evaluation_metrics.ipynb`)

### Purpose
Quantifies recommendation quality through offline evaluation metrics.

### Syllabus Alignment
**Unit 5: Accuracy, Catalog Coverage, and Recall**

### Technical Details

#### Metrics Implemented

##### 1. Classification Metrics (Fitness_Goal Prediction)
- **Random Forest Classifier**: 100 estimators, `random_state=42`
- **Accuracy**: Proportion of correct predictions
- **F1-Score (Macro)**: Harmonic mean of precision and recall

##### 2. Matrix Factorization Metrics
- **SVD Reconstruction RMSE**: Root mean square error between original and reconstructed interaction matrix

##### 3. Ranking Metrics
```python
def precision_at_k(recommended, actual, k):
    return len(set(recommended) & set(actual)) / len(recommended)

def recall_at_k(recommended, actual, k):
    return len(set(recommended) & set(actual)) / len(actual)
```

##### 4. Catalog Coverage
```python
coverage = len(recommended_items) / unique_diets
```
- Proportion of all diet plans ever recommended to any user

##### 5. Diversity (Jaccard)
- Intra-list similarity among recommended items
- Measures how varied the recommendation lists are

#### Evaluation Pipeline
1. **Train-Test Split**: 80-20 ratio with `random_state=42`
2. **KNN Model**: 20 neighbors, cosine metric
3. **SVD Model**: 10 latent components
4. **Metrics Calculation**: Precision@K, Recall@K for K=5

#### Expected Performance
| Metric | Typical Range |
|--------|---------------|
| Accuracy | 0.75 - 0.95 |
| F1-Score | 0.70 - 0.90 |
| SVD RMSE | 0.08 - 0.15 |
| Precision@5 | 0.60 - 0.85 |
| Recall@5 | 0.15 - 0.40 |
| Catalog Coverage | 0.70 - 0.95 |

---

## Dataset Schema (30 Features)

### Numeric Features
| Feature | Description |
|---------|-------------|
| Age | User age in years |
| Height / Height_cm | Height in cm |
| Weight / Weight_kg | Weight in kg |
| BMI | Body Mass Index |

### Categorical Features
| Feature | Description |
|---------|-------------|
| Gender | male/female |
| Chronic_Disease | None/diabetes/etc. |
| Activity_Level | Sedentary/Moderate/Active |
| Dietary_Preference | No Preference/vegan/etc. |
| Fitness_Goal | weight_loss/muscle_gain/etc. |

### Target Features
| Feature | Description |
|---------|-------------|
| diet_recommendation | Assigned diet plan |
| exercise_plan | Assigned workout plan |
| source | Origin dataset identifier |

---

## Production Pipeline (`train_model.py`)

### Purpose
Automated script that trains the hybrid pipeline and exports models for Django deployment.

### Output
- `.pkl` model files in `recommendations/models/`
- Low-latency inference for web application

### Dependencies
- scikit-learn for preprocessing and ML models
- pandas/numpy for data manipulation
- joblib for model serialization

---

## Viva Technical Questions & Answers

### Q1: Why use Truncated SVD instead of regular SVD?
**A:** Regular SVD requires the matrix to be full rank and has O(n³) complexity. Truncated SVD:
- Works with sparse matrices directly
- Has O(n²k) complexity where k << n
- Extracts only the top-k singular values/vectors
- Perfect for high-dimensional user-item matrices

### Q2: How does Cosine Similarity work in KNN?
**A:** Cosine similarity measures the cosine angle between two vectors:
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```
- Value of 1 = identical vectors (perfect match)
- Value of 0 = orthogonal vectors (no similarity)
- Used because it works well with high-dimensional sparse vectors

### Q3: What is the difference between User-based and Item-based Collaborative Filtering?
**A:**
| Aspect | User-Based | Item-Based |
|--------|------------|------------|
| Similarity | Users are similar | Items are similar |
| Formula | User-user | Item-item |
| Stability | Changes frequently | More stable |
| Use Case | Small, dynamic datasets | Large, static datasets |

### Q4: Why is Cascade Hybrid better than Weighted Hybrid?
**A:** Cascade Hybrid:
- **Efficient**: Filters reduce candidate set before expensive computation
- **Safe**: Medical constraints eliminate harmful recommendations first
- **Explainable**: Clear logical flow (filter → rank → adjust)
- **No Weight Tuning**: Avoids manual tuning of combination weights

### Q5: How does Context-Aware adjustment work?
**A:** Post-filtering score modulation using contextual signals:
1. Fetch user context (sleep, steps, time of day)
2. Apply domain rules (poor sleep → reduce high-intensity scores)
3. Multiply base score by adjustment factors
4. Re-rank based on adjusted scores

### Q6: What is the purpose of One-Hot Encoding?
**A:** Converts categorical variables into binary vectors:
- "Male" → [1, 0]
- "Female" → [0, 1]
- Allows similarity computation between categorical values
- Combined with StandardScaler for numeric features

### Q7: How do you handle Cold Start Problem?
**A:** In this implementation:
1. **Content-Based**: Falls back to feature similarity for new users
2. **Default Recommendations**: New users get popular/global recommendations
3. **Hybrid**: Combines content features with collaborative signals

### Q8: Why StandardScaler before KNN?
**A:** Ensures all features contribute equally:
- Age (20-80) vs Height (150-200) vs Weight (40-150)
- Without scaling, Weight would dominate distance calculations
- StandardScaler: `z = (x - μ) / σ`

### Q9: What is Reconstruction Error in SVD?
**A:** Measures how well the latent factors reconstruct the original matrix:
```
RMSE = √(Σ(original - reconstructed)² / n)
```
- Lower RMSE = better latent representation
- ~0.10 in this project indicates good fit

### Q10: How is Catalog Coverage calculated?
**A:** 
```python
recommended_items = set()  # All unique items recommended
for user in test_users:
    recommendations = knn.predict(user)
    recommended_items.update(recommendations)
coverage = len(recommended_items) / total_unique_items
```
- High coverage = system recommends diverse items
- Low coverage = system recommends same items to everyone
