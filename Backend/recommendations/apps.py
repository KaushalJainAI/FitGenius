import os
import pickle
import logging
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger('recommendations')

class RecommendationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recommendations'
    
    knn_model = None
    preprocessor = None
    reference_plans = None

    def ready(self):
        models_dir = os.path.join(settings.BASE_DIR, 'recommendations', 'models')
        try:
            with open(os.path.join(models_dir, 'knn_model.pkl'), 'rb') as f:
                RecommendationsConfig.knn_model = pickle.load(f)
            with open(os.path.join(models_dir, 'preprocessor.pkl'), 'rb') as f:
                RecommendationsConfig.preprocessor = pickle.load(f)
            
            import pandas as pd
            RecommendationsConfig.reference_plans = pd.read_pickle(os.path.join(models_dir, 'reference_plans.pkl'))
            logger.info("Successfully loaded static ML models into memory.")
        except Exception as e:
            logger.warning(f"Failed to load ML models on startup: {e}")
