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
            if hasattr(np, '_core') and 'numpy._core' not in sys.modules:
                sys.modules['numpy._core'] = np._core
                sys.modules['numpy._core.multiarray'] = np._core.multiarray
                sys.modules['numpy._core._multiarray_umath'] = np._core._multiarray_umath
            
            # Load models with error handling
            with open(TFIDF_MODEL_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)
            with open(ML_MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            
            # Log model details
            logger.info("ML models loaded successfully")
            logger.info(f"Vectorizer type: {type(self.vectorizer)}")
            logger.info(f"Model type: {type(self.model)}")
            
            # Check and fix vectorizer attributes
            has_vocabulary = hasattr(self.vectorizer, 'vocabulary_') and self.vectorizer.vocabulary_
            has_idf = hasattr(self.vectorizer, 'idf_') and self.vectorizer.idf_ is not None
            
            logger.info(f"Has vocabulary_: {has_vocabulary}")
            logger.info(f"Has idf_: {has_idf}")
            
            if has_vocabulary:
                logger.info(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
            
            # If vocabulary exists but idf_ doesn't, try to fix the vectorizer
            if has_vocabulary and not has_idf:
                logger.warning("Vectorizer has vocabulary but missing idf_ - attempting to fix")
                try:
                    from sklearn.feature_extraction.text import TfidfTransformer
                    from sklearn.utils.validation import check_is_fitted
                    
                    # Try to get idf_ from _tfidf attribute if it exists
                    if hasattr(self.vectorizer, '_tfidf') and hasattr(self.vectorizer._tfidf, 'idf_'):
                        self.vectorizer.idf_ = self.vectorizer._tfidf.idf_
                        logger.info("Copied idf_ from _tfidf transformer")
                        has_idf = True
                    
                    # Verify it's now fitted
                    if has_idf:
                        try:
                            check_is_fitted(self.vectorizer)
                            logger.info("Vectorizer is now properly fitted")
                        except:
                            logger.warning("Vectorizer still not fitted after fix attempt")
                except Exception as fix_error:
                    logger.error(f"Failed to fix vectorizer: {fix_error}")
            
            if not has_vocabulary or not has_idf:
                raise ValueError(f"Vectorizer not properly fitted: vocabulary={has_vocabulary}, idf={has_idf}")
            
            self.loaded = True
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
            logger.error(f"Models not loaded. Error: {self.load_error}")
            return "Unknown", None, 0.0
        
        try:
            # Clean text
            cleaned_text = clean_resume_for_categorization(resume_text)
            
            if not cleaned_text.strip():
                logger.warning("Cleaned text is empty")
                return "Unknown", None, 0.0
            
            # Log for debugging
            logger.info(f"Attempting prediction with vectorizer type: {type(self.vectorizer)}")
            logger.info(f"Model type: {type(self.model)}")
            
            # Transform and predict
            import numpy as np
            try:
                # Detailed logging for debugging
                logger.info(f"Has vocabulary_: {hasattr(self.vectorizer, 'vocabulary_')}")
                logger.info(f"Has idf_: {hasattr(self.vectorizer, 'idf_')}")
                logger.info(f"Has _tfidf: {hasattr(self.vectorizer, '_tfidf')}")
                
                if hasattr(self.vectorizer, 'vocabulary_'):
                    logger.info(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
                
                features = self.vectorizer.transform([cleaned_text])
                logger.info(f"Text transformation successful. Feature shape: {features.shape}")
            except Exception as transform_error:
                logger.error(f"Transform failed: {transform_error}")
                logger.error(f"Vectorizer type: {type(self.vectorizer)}")
                logger.error(f"Vectorizer __dict__ keys: {list(self.vectorizer.__dict__.keys())}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return "Model Error", None, 0.0
            
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
