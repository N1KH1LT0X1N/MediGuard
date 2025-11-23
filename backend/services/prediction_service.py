"""
Prediction Service for disease prediction using the trained model.
"""

import sys
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import joblib
import warnings

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "ml" / "scaling_layer"))

try:
    from enhanced_scaling_bridge import EnhancedScalingBridge, create_bridge_from_inferred_ranges
except ImportError:
    raise ImportError("Could not import EnhancedScalingBridge. Make sure ml/scaling_layer exists.")

# Feature names in order (24 features)
FEATURE_NAMES = [
    'Glucose',
    'Cholesterol',
    'Hemoglobin',
    'Platelets',
    'White Blood Cells',
    'Red Blood Cells',
    'Hematocrit',
    'Mean Corpuscular Volume',
    'Mean Corpuscular Hemoglobin',
    'Mean Corpuscular Hemoglobin Concentration',
    'Insulin',
    'BMI',
    'Systolic Blood Pressure',
    'Diastolic Blood Pressure',
    'Triglycerides',
    'HbA1c',
    'LDL Cholesterol',
    'HDL Cholesterol',
    'ALT',
    'AST',
    'Heart Rate',
    'Creatinine',
    'Troponin',
    'C-reactive Protein',
]


class PredictionService:
    """Service for making disease predictions."""
    
    def __init__(self, model_path: Optional[Path] = None, encoder_path: Optional[Path] = None):
        """
        Initialize prediction service.
        
        Args:
            model_path: Path to model file (default: PROJECT_ROOT/disease_prediction_model.pkl)
            encoder_path: Path to encoder file (default: PROJECT_ROOT/label_encoder.pkl)
        """
        if model_path is None:
            model_path = PROJECT_ROOT / "disease_prediction_model.pkl"
        if encoder_path is None:
            encoder_path = PROJECT_ROOT / "label_encoder.pkl"
        
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.model = None
        self.label_encoder = None
        self.scaling_bridge = None
        
        # Load model and encoder
        self._load_model()
        
        # Initialize scaling bridge
        self._init_scaling_bridge()
    
    def _load_model(self):
        """Load the trained model and label encoder."""
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                try:
                    self.model = joblib.load(self.model_path)
                    self.label_encoder = joblib.load(self.encoder_path)
                except (ValueError, TypeError, AttributeError) as joblib_error:
                    error_str = str(joblib_error)
                    if 'BitGenerator' in error_str or 'MT19937' in error_str:
                        # Try pickle as fallback
                        try:
                            with open(self.model_path, 'rb') as f:
                                try:
                                    self.model = pickle.load(f)
                                except:
                                    f.seek(0)
                                    self.model = pickle.load(f, encoding='latin1')
                            with open(self.encoder_path, 'rb') as f:
                                try:
                                    self.label_encoder = pickle.load(f)
                                except:
                                    f.seek(0)
                                    self.label_encoder = pickle.load(f, encoding='latin1')
                        except Exception as pickle_error:
                            raise Exception(f"Could not load model: {error_str}")
                    else:
                        # Other joblib error, try pickle
                        try:
                            with open(self.model_path, 'rb') as f:
                                self.model = pickle.load(f)
                            with open(self.encoder_path, 'rb') as f:
                                self.label_encoder = pickle.load(f)
                        except Exception as pickle_error:
                            raise Exception(f"Failed to load model: {joblib_error}")
            
            # Validate model
            if not hasattr(self.model, 'predict'):
                raise ValueError("Loaded model does not have 'predict' method")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Model file not found: {e}")
        except Exception as e:
            raise Exception(f"Error loading model: {e}")
    
    def _init_scaling_bridge(self):
        """Initialize the scaling bridge."""
        try:
            inferred_json = PROJECT_ROOT / "ml" / "scaling_layer" / "inferred_ranges.json"
            if inferred_json.exists():
                self.scaling_bridge = create_bridge_from_inferred_ranges(str(inferred_json))
            else:
                self.scaling_bridge = create_bridge_from_inferred_ranges()
        except Exception as e:
            raise Exception(f"Error initializing scaling bridge: {e}")
    
    def predict(self, features: Dict[str, float]) -> Tuple[str, Dict[str, float], np.ndarray]:
        """
        Make a prediction from feature dictionary.
        
        Args:
            features: Dictionary mapping feature names to values (raw clinical values)
            
        Returns:
            Tuple of (predicted_disease, probabilities_dict, scaled_array)
        """
        # Validate features
        missing_features = [name for name in FEATURE_NAMES if name not in features]
        if missing_features:
            raise ValueError(f"Missing features: {missing_features}")
        
        # Scale features
        scaled_array = self.scaling_bridge.scale_to_array(
            features, 
            feature_order=FEATURE_NAMES
        )
        
        # Reshape for model input (1 sample, 24 features)
        scaled_array = scaled_array.reshape(1, -1)
        
        # Make prediction
        prediction = self.model.predict(scaled_array)
        prediction_proba = self.model.predict_proba(scaled_array)[0] if hasattr(self.model, 'predict_proba') else None
        
        # Decode prediction
        disease = self.label_encoder.inverse_transform(prediction)[0]
        
        # Create probabilities dictionary
        probabilities = {}
        if prediction_proba is not None:
            classes = self.label_encoder.classes_
            for cls, prob in zip(classes, prediction_proba):
                probabilities[cls] = float(prob)
        
        return disease, probabilities, scaled_array[0]


# Global instance (will be initialized in main.py)
prediction_service: Optional[PredictionService] = None

