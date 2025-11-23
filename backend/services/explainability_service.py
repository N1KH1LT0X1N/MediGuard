"""
Explainability Service for generating LIME explanations and Plotly visualizations.
"""

import sys
from pathlib import Path
from typing import Dict, Tuple, Optional
import tempfile

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

try:
    from explainability import MediGuardExplainer
    HAS_EXPLAINABILITY = True
except ImportError:
    HAS_EXPLAINABILITY = False
    MediGuardExplainer = None

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


class ExplainabilityService:
    """Service for generating explainability results."""
    
    def __init__(self):
        """Initialize explainability service."""
        self.explainer = None
        self._init_explainer()
    
    def _init_explainer(self):
        """Initialize MediGuardExplainer."""
        if not HAS_EXPLAINABILITY:
            return
        
        try:
            model_path = PROJECT_ROOT / "models" / "disease_prediction_model.pkl"
            encoder_path = PROJECT_ROOT / "models" / "label_encoder.pkl"
            training_data_path = PROJECT_ROOT / "test_data" / "cleaned_test.csv"
            
            # Initialize scaling bridge
            sys.path.insert(0, str(PROJECT_ROOT / "ml" / "scaling_layer"))
            from enhanced_scaling_bridge import create_bridge_from_inferred_ranges
            inferred_json = PROJECT_ROOT / "ml" / "scaling_layer" / "inferred_ranges.json"
            if inferred_json.exists():
                scaling_bridge = create_bridge_from_inferred_ranges(str(inferred_json))
            else:
                scaling_bridge = create_bridge_from_inferred_ranges()
            
            # Check if files exist
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
            if not encoder_path.exists():
                raise FileNotFoundError(f"Encoder file not found: {encoder_path}")
            if not training_data_path.exists():
                raise FileNotFoundError(f"Training data file not found: {training_data_path}")
            
            self.explainer = MediGuardExplainer(
                model_path=str(model_path),
                encoder_path=str(encoder_path),
                training_data_path=str(training_data_path),
                scaling_bridge=scaling_bridge
            )
            print(f"✓ Explainability service: MediGuardExplainer initialized successfully")
        except Exception as e:
            import traceback
            print(f"⚠️  Warning: Could not initialize explainability service: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            self.explainer = None
    
    def generate_explanation(self, features: Dict[str, float]) -> Tuple[Dict[str, float], str]:
        """
        Generate explainability results (JSON data and Plotly HTML).
        
        Args:
            features: Dictionary mapping feature names to raw clinical values
            
        Returns:
            Tuple of (explainability_json, explainability_html)
            explainability_json: Dict mapping feature names to importance scores
            explainability_html: Plotly HTML string for inline embedding
        """
        if not self.explainer:
            # Return empty results if explainability not available
            print("⚠️  Explainability service: explainer not initialized, returning empty results")
            return {}, ""
        
        try:
            # Generate Plotly HTML
            with tempfile.TemporaryDirectory() as tmpdir:
                html_path = self.explainer.generate_interactive_plot(
                    patient_data=features,
                    output_dir=tmpdir
                )
                
                # Read HTML content
                with open(html_path, 'r', encoding='utf-8') as f:
                    explainability_html = f.read()
            
            # Extract feature importance for JSON
            # We need to regenerate LIME explanation to get JSON data
            # Reuse the logic from explainability.py but extract JSON
            explainability_json = self._extract_feature_importance(features)
            
            return explainability_json, explainability_html
        
        except Exception as e:
            import traceback
            print(f"❌ Error generating explanation: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            # Return empty results on error
            return {}, ""
    
    def _extract_feature_importance(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Extract feature importance scores from LIME explanation.
        
        Args:
            features: Dictionary mapping feature names to raw clinical values
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.explainer:
            return {}
        
        try:
            # Scale patient data
            scaled_patient_array = self.explainer.scaling_bridge.scale_to_array(
                features,
                feature_order=self.explainer.feature_names
            )
            
            # Get predicted class
            scaled_array = scaled_patient_array.reshape(1, -1)
            prediction = self.explainer.model.predict(scaled_array)[0]
            predicted_class_idx = int(prediction)
            
            # Create wrapper for LIME
            import numpy as np
            def predict_proba_scaled_wrapper(scaled_features_array):
                if len(scaled_features_array.shape) == 1:
                    scaled_features_array = scaled_features_array.reshape(1, -1)
                n_samples = scaled_features_array.shape[0]
                predictions = []
                for i in range(n_samples):
                    scaled_input = scaled_features_array[i].reshape(1, -1)
                    proba = self.explainer.model.predict_proba(scaled_input)[0]
                    predictions.append(proba)
                return np.array(predictions)
            
            # Generate LIME explanation
            explanation = self.explainer.explainer.explain_instance(
                scaled_patient_array,
                predict_proba_scaled_wrapper,
                num_features=24,
                top_labels=1
            )
            
            # Extract feature importance
            feature_importance = {}
            try:
                explanation_map = explanation.as_map()
                if predicted_class_idx in explanation_map:
                    for idx, importance in explanation_map[predicted_class_idx]:
                        if 0 <= idx < len(self.explainer.feature_names):
                            feature_name = self.explainer.feature_names[idx]
                            feature_importance[feature_name] = float(importance)
            except Exception:
                # Fallback to as_list
                try:
                    explanation_list = explanation.as_list(label=predicted_class_idx)
                    for item in explanation_list:
                        feature_name_str, importance = item
                        # Try to extract feature index
                        try:
                            idx = int(str(feature_name_str).strip())
                            if 0 <= idx < len(self.explainer.feature_names):
                                feature_name = self.explainer.feature_names[idx]
                                feature_importance[feature_name] = float(importance)
                        except (ValueError, TypeError):
                            pass
                except Exception:
                    pass
            
            # Ensure all features are included (set missing ones to 0)
            for name in self.explainer.feature_names:
                if name not in feature_importance:
                    feature_importance[name] = 0.0
            
            return feature_importance
        
        except Exception as e:
            print(f"Error extracting feature importance: {e}")
            return {}


# Global instance (will be initialized in main.py)
explainability_service: Optional[ExplainabilityService] = None

