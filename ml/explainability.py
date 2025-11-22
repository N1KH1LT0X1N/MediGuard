"""
MediGuard AI Explainability Module

This module provides LIME-based explainability for disease predictions,
generating interactive risk indicator visualizations using Plotly.
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import warnings
import re

# Feature names in order (24 features, matching predict.py)
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

# Feature units mapping for tooltips
FEATURE_UNITS = {
    'Glucose': 'mg/dL',
    'Cholesterol': 'mg/dL',
    'Hemoglobin': 'g/dL',
    'Platelets': 'per microliter',
    'White Blood Cells': 'per microliter',
    'Red Blood Cells': 'million per microliter',
    'Hematocrit': '%',
    'Mean Corpuscular Volume': 'fL',
    'Mean Corpuscular Hemoglobin': 'pg',
    'Mean Corpuscular Hemoglobin Concentration': 'g/dL',
    'Insulin': 'μIU/mL',
    'BMI': 'kg/m²',
    'Systolic Blood Pressure': 'mmHg',
    'Diastolic Blood Pressure': 'mmHg',
    'Triglycerides': 'mg/dL',
    'HbA1c': '%',
    'LDL Cholesterol': 'mg/dL',
    'HDL Cholesterol': 'mg/dL',
    'ALT': 'U/L',
    'AST': 'U/L',
    'Heart Rate': 'bpm',
    'Creatinine': 'mg/dL',
    'Troponin': 'ng/mL',
    'C-reactive Protein': 'mg/L',
}

try:
    from lime.lime_tabular import LimeTabularExplainer
    HAS_LIME = True
except ImportError:
    HAS_LIME = False
    warnings.warn("LIME not available. Install with: pip install lime")

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    warnings.warn("Plotly not available. Install with: pip install plotly")


class MediGuardExplainer:
    """
    Explainability module for MediGuard AI predictions.
    
    Uses LIME to explain model predictions and generates interactive
    risk indicator visualizations using Plotly.
    """
    
    def __init__(self, model_path, encoder_path, training_data_path, scaling_bridge):
        """
        Initialize the explainer.
        
        Args:
            model_path: Path to the trained model (.pkl file)
            encoder_path: Path to the label encoder (.pkl file)
            training_data_path: Path to training data CSV (cleaned_test.csv)
            scaling_bridge: EnhancedScalingBridge instance for raw-to-scaled conversion
        """
        if not HAS_LIME:
            raise ImportError("LIME is required. Install with: pip install lime")
        if not HAS_PLOTLY:
            raise ImportError("Plotly is required. Install with: pip install plotly")
        
        # Load model and encoder
        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(encoder_path)
        
        # Store scaling bridge
        self.scaling_bridge = scaling_bridge
        if scaling_bridge is None:
            raise ValueError("Scaling bridge is required for explainability")
        
        # Load training data
        training_df = pd.read_csv(training_data_path)
        
        # Extract feature columns (exclude 'Disease' column)
        if 'Disease' in training_df.columns:
            self.training_data = training_df[FEATURE_NAMES].values
        else:
            # Assume all columns are features
            self.training_data = training_df.values
        
        # Note: training_data is already scaled (0-1) from cleaned_test.csv
        # But LIME needs to work with raw values for interpretability
        # So we'll pass raw values to explain_instance, and predict_proba_wrapper will scale them
        
        # Initialize LIME explainer with scaled training data
        # We use scaled data for the explainer initialization, but the predict_proba_wrapper
        # will handle conversion from raw to scaled
        self.explainer = LimeTabularExplainer(
            self.training_data,  # Scaled data (0-1) for LIME's internal use
            mode='classification',
            feature_names=FEATURE_NAMES,
            class_names=list(self.label_encoder.classes_),
            discretize_continuous=False
        )
        
        self.feature_names = FEATURE_NAMES
    
    def predict_proba_wrapper(self, raw_features_array):
        """
        Wrapper function for LIME that accepts raw clinical values.
        
        Args:
            raw_features_array: Numpy array of raw clinical values (shape: [n_samples, 24])
        
        Returns:
            Probability array from model (shape: [n_samples, n_classes])
        """
        # Convert array to feature dictionary
        n_samples = raw_features_array.shape[0]
        predictions = []
        
        for i in range(n_samples):
            # Create feature dict for this sample
            feature_dict = dict(zip(self.feature_names, raw_features_array[i]))
            
            # Scale using scaling bridge
            scaled_array = self.scaling_bridge.scale_to_array(
                feature_dict, 
                feature_order=self.feature_names
            )
            
            # Reshape for model input (1 sample, 24 features)
            scaled_array = scaled_array.reshape(1, -1)
            
            # Get probabilities
            proba = self.model.predict_proba(scaled_array)[0]
            predictions.append(proba)
        
        return np.array(predictions)
    
    def generate_interactive_plot(self, patient_data: Dict[str, float], output_dir: str = '.') -> str:
        """
        Generate interactive risk indicator plot using LIME explanations.
        
        Args:
            patient_data: Dictionary of raw feature values (24 features)
            output_dir: Directory to save HTML file (default: current directory)
        
        Returns:
            Absolute path to generated HTML file
        """
        if not HAS_LIME or not HAS_PLOTLY:
            raise ImportError("LIME and Plotly are required for visualization")
        
        # Scale patient data to match training data format (0-1 range)
        # LIME was initialized with scaled data, so we need to pass scaled values
        scaled_patient_array = self.scaling_bridge.scale_to_array(
            patient_data,
            feature_order=self.feature_names
        )
        
        # Get predicted class
        scaled_array = scaled_patient_array.reshape(1, -1)
        prediction = self.model.predict(scaled_array)[0]
        predicted_class_idx = int(prediction)
        
        # Create a wrapper that works with scaled values (since LIME expects same format as training data)
        def predict_proba_scaled_wrapper(scaled_features_array):
            """Wrapper for LIME that accepts already-scaled features."""
            # Handle both 1D and 2D arrays
            if len(scaled_features_array.shape) == 1:
                scaled_features_array = scaled_features_array.reshape(1, -1)
            
            n_samples = scaled_features_array.shape[0]
            predictions = []
            for i in range(n_samples):
                scaled_input = scaled_features_array[i].reshape(1, -1)
                proba = self.model.predict_proba(scaled_input)[0]
                predictions.append(proba)
            return np.array(predictions)
        
        # Generate LIME explanation using scaled values
        explanation = self.explainer.explain_instance(
            scaled_patient_array,  # Pass scaled values to match training data format
            predict_proba_scaled_wrapper,  # Use wrapper that expects scaled values
            num_features=24,  # Show all features
            top_labels=1
        )
        
        # Extract feature importance scores
        # Use as_map() which returns {feature_index: importance} - more reliable
        feature_importance = {}
        try:
            explanation_map = explanation.as_map()
            if predicted_class_idx in explanation_map:
                # Convert index-based map to feature names
                for idx, importance in explanation_map[predicted_class_idx]:
                    if 0 <= idx < len(self.feature_names):
                        feature_name = self.feature_names[idx]
                        feature_importance[feature_name] = importance
                # Debug: Check if we got values
                if not feature_importance or all(abs(v) < 1e-10 for v in feature_importance.values()):
                    # Try as_list as fallback
                    explanation_list = explanation.as_list(label=predicted_class_idx)
                    for feature_name, importance in explanation_list:
                        try:
                            idx = int(str(feature_name).strip())
                            if 0 <= idx < len(self.feature_names):
                                feature_name_clean = self.feature_names[idx]
                                if feature_name_clean not in feature_importance:
                                    feature_importance[feature_name_clean] = importance
                        except (ValueError, TypeError):
                            pass
            else:
                # Fallback to as_list
                explanation_list = explanation.as_list(label=predicted_class_idx)
                feature_importance = {}
                for feature_name, importance in explanation_list:
                    # Handle feature name extraction
                    matched_name = None
                    try:
                        idx = int(feature_name.strip())
                        if 0 <= idx < len(self.feature_names):
                            matched_name = self.feature_names[idx]
                    except (ValueError, TypeError):
                        # Try to match by name
                        base_name = feature_name
                        for separator in [' <=', ' >', ' <', ' >=', ' =']:
                            if separator in base_name:
                                base_name = base_name.split(separator)[0].strip()
                                break
                        for our_feature in self.feature_names:
                            if our_feature.lower() == base_name.lower():
                                matched_name = our_feature
                                break
                        if matched_name is None:
                            numbers = re.findall(r'\d+', str(feature_name))
                            if numbers:
                                try:
                                    idx = int(numbers[0])
                                    if 0 <= idx < len(self.feature_names):
                                        matched_name = self.feature_names[idx]
                                except (ValueError, IndexError):
                                    pass
                    
                    if matched_name:
                        if matched_name in feature_importance:
                            feature_importance[matched_name] += importance
                        else:
                            feature_importance[matched_name] = importance
        except Exception as e:
            # Fallback: use as_list
            try:
                explanation_list = explanation.as_list(label=predicted_class_idx)
                feature_importance = {}
                for feature_name, importance in explanation_list:
                    # Try to extract feature index or name
                    matched_name = None
                    try:
                        idx = int(str(feature_name).strip())
                        if 0 <= idx < len(self.feature_names):
                            matched_name = self.feature_names[idx]
                    except (ValueError, TypeError):
                        base_name = str(feature_name)
                        for separator in [' <=', ' >', ' <', ' >=', ' =']:
                            if separator in base_name:
                                base_name = base_name.split(separator)[0].strip()
                                break
                        for our_feature in self.feature_names:
                            if our_feature.lower() == base_name.lower():
                                matched_name = our_feature
                                break
                        if matched_name is None:
                            numbers = re.findall(r'\d+', base_name)
                            if numbers:
                                try:
                                    idx = int(numbers[0])
                                    if 0 <= idx < len(self.feature_names):
                                        matched_name = self.feature_names[idx]
                                except (ValueError, IndexError):
                                    pass
                    if matched_name:
                        if matched_name in feature_importance:
                            feature_importance[matched_name] += importance
                        else:
                            feature_importance[matched_name] = importance
            except Exception as e2:
                warnings.warn(f"Could not extract LIME explanations: {e}, {e2}")
                feature_importance = {}
        
        # Ensure all features are included (set missing ones to 0)
        for name in self.feature_names:
            if name not in feature_importance:
                feature_importance[name] = 0.0
        
        # Sort features by absolute importance (descending)
        sorted_features = sorted(
            self.feature_names,
            key=lambda x: abs(feature_importance.get(x, 0.0)),
            reverse=True
        )
        
        # Prepare data for plotting
        feature_names_plot = []
        importance_scores = []
        colors = []
        hover_texts = []
        
        for feature_name in sorted_features:
            importance = feature_importance.get(feature_name, 0.0)
            raw_value = patient_data[feature_name]
            unit = FEATURE_UNITS.get(feature_name, '')
            
            feature_names_plot.append(feature_name)
            importance_scores.append(importance)
            
            # Color: Green for negative (healthy), Red for positive (disease risk)
            if importance < 0:
                colors.append('#2ecc71')  # Green
            else:
                colors.append('#e74c3c')  # Red
            
            # Tooltip text
            hover_text = (
                f"<b>{feature_name}</b><br>"
                f"Value: {raw_value:.2f} {unit}<br>"
                f"Contribution: {importance:.4f}"
            )
            hover_texts.append(hover_text)
        
        # Create Plotly figure
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=importance_scores,
            y=feature_names_plot,
            orientation='h',
            marker=dict(color=colors),
            text=[f"{score:.4f}" for score in importance_scores],
            textposition='outside',
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_texts,
            name='Feature Contribution'
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Risk Indicator Analysis',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis_title='Contribution Score',
            yaxis_title='Clinical Features',
            template='plotly_white',
            height=800,
            showlegend=False,
            margin=dict(l=200, r=50, t=80, b=50),
            xaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=11)
            )
        )
        
        # Generate timestamp-based filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'explanation_{timestamp}.html'
        output_path = Path(output_dir) / filename
        output_path = output_path.resolve()
        
        # Save HTML file
        fig.write_html(str(output_path))
        
        return str(output_path)

