"""Machine Learning service for resume categorization."""
import pickle
import streamlit as st
from typing import Tuple, Optional
import logging

from config.settings import TFIDF_MODEL_PATH, ML_MODEL_PATH, CATEGORY_MAPPING
from services.text_processing import clean_resume_for_categorization

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLCategorizationService:
    """Handles ML-based resume categorization."""
    
    def __init__(self):
        """Initialize ML service with models."""
        self.vectorizer = None
        self.model = None
        self.loaded = False
        self.load_error = None
        self._load_models()
    
    def _load_models(self):
        """Load TF-IDF vectorizer and ML model from pickle files."""
        try:
            import numpy as np
            import sys
            import os
            
            # Check if files exist
            if not os.path.exists(TFIDF_MODEL_PATH):
                raise FileNotFoundError(f"TF-IDF model not found at {TFIDF_MODEL_PATH}")
            if not os.path.exists(ML_MODEL_PATH):
                raise FileNotFoundError(f"ML model not found at {ML_MODEL_PATH}")
            
            # Map numpy._core to numpy.core for backward compatibility
            if 'numpy._core' not in sys.modules:
                sys.modules['numpy._core'] = np.core
                sys.modules['numpy._core.multiarray'] = np.core.multiarray
                sys.modules['numpy._core._multiarray_umath'] = np.core._multiarray_umath
            
            # Load models with error handling
            with open(TFIDF_MODEL_PATH, "rb") as f:
                self.vectorizer = pickle.load(f, encoding='latin1')
            with open(ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f, encoding='latin1')
            
            # Verify models are fitted
            if not hasattr(self.vectorizer, 'idf_'):
                raise ValueError("TF-IDF vectorizer is not fitted")
            
            self.loaded = True
            logger.info("ML models loaded successfully")
        except FileNotFoundError as e:
            self.load_error = f"Model files not found: {e}. Please ensure tfidf.pkl and model.pkl are in the project root."
            logger.error(self.load_error)
        except Exception as e:
            self.load_error = f"Error loading models: {e}"
            logger.error(self.load_error)
    
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self.loaded
    
    def predict_category(self, resume_text: str) -> Tuple[Optional[str], Optional[int], Optional[float]]:
        """
        Predict category for a resume.
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Tuple of (category_name, category_id, confidence_score)
        """
        if not self.loaded:
            logger.error("Models not loaded")
            return None, None, None
        
        try:
            # Clean text
            cleaned_text = clean_resume_for_categorization(resume_text)
            
            if not cleaned_text.strip():
                logger.warning("Cleaned text is empty")
                return "Unknown", None, 0.0
            
            # Transform and predict
            import numpy as np
            features = self.vectorizer.transform([cleaned_text])
            prediction_id = self.model.predict(features)[0]
            
            # Handle numpy types
            if hasattr(prediction_id, 'item'):
                prediction_id = prediction_id.item()
            
            # Get probability/confidence if available
            confidence = 0.0
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(features)[0]
                # Get the maximum probability and convert to percentage
                confidence = float(max(probabilities)) * 100.0
            
            category_name = CATEGORY_MAPPING.get(prediction_id, f"Unknown Category ({prediction_id})")
            
            logger.info(f"Prediction: {category_name} (ID: {prediction_id}, Confidence: {confidence:.2f}%)")
            return category_name, int(prediction_id), confidence
            
        except Exception as e:
            import traceback
            logger.error(f"Error during prediction: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "Prediction Error", None, 0.0
    
    def batch_predict(self, resume_texts: list) -> list:
        """
        Predict categories for multiple resumes.
        
        Args:
            resume_texts: List of resume texts
            
        Returns:
            List of tuples (category_name, category_id, confidence)
        """
        results = []
        for text in resume_texts:
            result = self.predict_category(text)
            results.append(result)
        return results


@st.cache_resource
def get_ml_service() -> MLCategorizationService:
    """Get or create ML service instance (cached)."""
    return MLCategorizationService()
