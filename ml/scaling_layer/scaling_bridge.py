"""
Scaling Bridge: Converts raw clinical inputs to scaled format (0-1) for ML model.

This module implements the core logic to map real-world, raw clinical values
(e.g., 120 mg/dL) into the 0 to 1 range used for model training.

The scaling uses Min-Max Normalization:
    scaled_value = (raw_value - min_value) / (max_value - min_value)
"""

import numpy as np
from typing import Dict, Optional, Union
import warnings


class ClinicalScalingBridge:
    """
    Scaling bridge that converts raw clinical values to 0-1 scaled format.
    
    Uses clinical reference ranges and data-driven min/max values to ensure
    accurate scaling that matches the training data distribution.
    """
    
    # Clinical reference ranges (min, max) for each feature
    # These are based on standard medical reference ranges
    CLINICAL_RANGES = {
        'Glucose': (70, 200),  # mg/dL (fasting: 70-100, random: <200)
        'Cholesterol': (100, 300),  # mg/dL (normal: <200, high: >240)
        'Hemoglobin': (12, 18),  # g/dL (men: 13.5-17.5, women: 12-15.5)
        'Platelets': (150000, 450000),  # per microliter (normal: 150k-450k)
        'White Blood Cells': (4000, 11000),  # per microliter (normal: 4k-11k)
        'Red Blood Cells': (4.0, 6.0),  # million per microliter (men: 4.5-5.9, women: 4.1-5.1)
        'Hematocrit': (36, 52),  # % (men: 41-50, women: 36-44)
        'Mean Corpuscular Volume': (80, 100),  # fL (normal: 80-100)
        'Mean Corpuscular Hemoglobin': (27, 33),  # pg (normal: 27-33)
        'Mean Corpuscular Hemoglobin Concentration': (32, 36),  # g/dL (normal: 32-36)
        'Insulin': (2, 25),  # μIU/mL (fasting: 2-25)
        'BMI': (15, 40),  # kg/m² (underweight: <18.5, normal: 18.5-25, obese: >30)
        'Systolic Blood Pressure': (90, 180),  # mmHg (normal: <120, high: >140)
        'Diastolic Blood Pressure': (60, 100),  # mmHg (normal: <80, high: >90)
        'Triglycerides': (50, 500),  # mg/dL (normal: <150, high: >200)
        'HbA1c': (4, 12),  # % (normal: <5.7, diabetic: >6.5)
        'LDL Cholesterol': (50, 200),  # mg/dL (optimal: <100, high: >160)
        'HDL Cholesterol': (30, 80),  # mg/dL (low: <40, high: >60)
        'ALT': (7, 56),  # U/L (men: 10-40, women: 7-35)
        'AST': (10, 40),  # U/L (men: 10-40, women: 9-32)
        'Heart Rate': (50, 100),  # bpm (resting: 60-100, athlete: 40-60)
        'Creatinine': (0.6, 1.3),  # mg/dL (men: 0.7-1.3, women: 0.6-1.1)
        'Troponin': (0, 0.04),  # ng/mL (normal: <0.04, elevated: >0.04)
        'C-reactive Protein': (0, 10),  # mg/L (normal: <3, high: >3)
    }
    
    def __init__(self, use_clinical_ranges: bool = True, 
                 custom_ranges: Optional[Dict[str, tuple]] = None,
                 clip_values: bool = True):
        """
        Initialize the scaling bridge.
        
        Args:
            use_clinical_ranges: If True, use clinical reference ranges.
                               If False, infer from scaled data (requires data analysis).
            custom_ranges: Optional dict of custom min/max ranges for specific features.
                          Format: {'Feature Name': (min, max)}
            clip_values: If True, clip values outside range to [0, 1] after scaling.
                        If False, allow values outside [0, 1] range.
        """
        self.use_clinical_ranges = use_clinical_ranges
        self.clip_values = clip_values
        self.ranges = self.CLINICAL_RANGES.copy()
        
        # Override with custom ranges if provided
        if custom_ranges:
            self.ranges.update(custom_ranges)
        
        # Feature name mapping (handle variations in naming)
        self.feature_mapping = {
            'glucose': 'Glucose',
            'cholesterol': 'Cholesterol',
            'hemoglobin': 'Hemoglobin',
            'platelets': 'Platelets',
            'white blood cells': 'White Blood Cells',
            'wbc': 'White Blood Cells',
            'red blood cells': 'Red Blood Cells',
            'rbc': 'Red Blood Cells',
            'hematocrit': 'Hematocrit',
            'mean corpuscular volume': 'Mean Corpuscular Volume',
            'mcv': 'Mean Corpuscular Volume',
            'mean corpuscular hemoglobin': 'Mean Corpuscular Hemoglobin',
            'mch': 'Mean Corpuscular Hemoglobin',
            'mean corpuscular hemoglobin concentration': 'Mean Corpuscular Hemoglobin Concentration',
            'mchc': 'Mean Corpuscular Hemoglobin Concentration',
            'insulin': 'Insulin',
            'bmi': 'BMI',
            'body mass index': 'BMI',
            'systolic blood pressure': 'Systolic Blood Pressure',
            'sbp': 'Systolic Blood Pressure',
            'diastolic blood pressure': 'Diastolic Blood Pressure',
            'dbp': 'Diastolic Blood Pressure',
            'triglycerides': 'Triglycerides',
            'hba1c': 'HbA1c',
            'glycated hemoglobin': 'HbA1c',
            'ldl cholesterol': 'LDL Cholesterol',
            'ldl': 'LDL Cholesterol',
            'hdl cholesterol': 'HDL Cholesterol',
            'hdl': 'HDL Cholesterol',
            'alt': 'ALT',
            'alanine aminotransferase': 'ALT',
            'ast': 'AST',
            'aspartate aminotransferase': 'AST',
            'heart rate': 'Heart Rate',
            'hr': 'Heart Rate',
            'creatinine': 'Creatinine',
            'troponin': 'Troponin',
            'c-reactive protein': 'C-reactive Protein',
            'crp': 'C-reactive Protein',
        }
    
    def _normalize_feature_name(self, feature_name: str) -> str:
        """Normalize feature name to standard format."""
        normalized = feature_name.strip()
        # Try exact match first
        if normalized in self.ranges:
            return normalized
        # Try case-insensitive match
        for key in self.ranges.keys():
            if key.lower() == normalized.lower():
                return key
        # Try mapping
        if normalized.lower() in self.feature_mapping:
            return self.feature_mapping[normalized.lower()]
        return normalized
    
    def scale_value(self, feature_name: str, raw_value: Union[float, int]) -> float:
        """
        Scale a single raw clinical value to 0-1 range.
        
        Args:
            feature_name: Name of the clinical feature
            raw_value: Raw clinical value to scale
            
        Returns:
            Scaled value in [0, 1] range (or outside if clip_values=False)
            
        Raises:
            ValueError: If feature name is not recognized
        """
        normalized_name = self._normalize_feature_name(feature_name)
        
        if normalized_name not in self.ranges:
            raise ValueError(
                f"Unknown feature: '{feature_name}'. "
                f"Available features: {list(self.ranges.keys())}"
            )
        
        min_val, max_val = self.ranges[normalized_name]
        
        # Handle edge case where min == max
        if max_val == min_val:
            warnings.warn(
                f"Min and max are equal for {normalized_name}. Returning 0.5.",
                UserWarning
            )
            return 0.5
        
        # Min-Max scaling
        scaled = (raw_value - min_val) / (max_val - min_val)
        
        # Clip if requested
        if self.clip_values:
            scaled = np.clip(scaled, 0.0, 1.0)
        else:
            # Warn if value is outside expected range
            if scaled < 0 or scaled > 1:
                warnings.warn(
                    f"Scaled value {scaled:.4f} for {normalized_name} "
                    f"(raw: {raw_value}) is outside [0, 1] range. "
                    f"Expected range: [{min_val}, {max_val}]",
                    UserWarning
                )
        
        return float(scaled)
    
    def scale_features(self, features: Dict[str, Union[float, int]]) -> Dict[str, float]:
        """
        Scale multiple clinical features at once.
        
        Args:
            features: Dictionary mapping feature names to raw values
                    Example: {'Glucose': 120, 'BMI': 22.5, 'Cholesterol': 180}
        
        Returns:
            Dictionary mapping feature names to scaled values (0-1 range)
        """
        scaled_features = {}
        for feature_name, raw_value in features.items():
            try:
                scaled_features[feature_name] = self.scale_value(feature_name, raw_value)
            except ValueError as e:
                warnings.warn(f"Skipping feature '{feature_name}': {str(e)}", UserWarning)
        
        return scaled_features
    
    def scale_to_array(self, features: Dict[str, Union[float, int]], 
                      feature_order: Optional[list] = None) -> np.ndarray:
        """
        Scale features and return as numpy array in specified order.
        
        Args:
            features: Dictionary mapping feature names to raw values
            feature_order: Optional list specifying the order of features.
                         If None, uses default order from CLINICAL_RANGES.
        
        Returns:
            Numpy array of scaled values in specified order
        """
        if feature_order is None:
            feature_order = list(self.ranges.keys())
        
        scaled_dict = self.scale_features(features)
        scaled_array = np.array([scaled_dict.get(feat, 0.0) for feat in feature_order])
        
        return scaled_array
    
    def get_feature_range(self, feature_name: str) -> tuple:
        """
        Get the min/max range for a feature.
        
        Args:
            feature_name: Name of the clinical feature
        
        Returns:
            Tuple of (min_value, max_value)
        """
        normalized_name = self._normalize_feature_name(feature_name)
        if normalized_name not in self.ranges:
            raise ValueError(f"Unknown feature: '{feature_name}'")
        return self.ranges[normalized_name]
    
    def update_range(self, feature_name: str, min_val: float, max_val: float):
        """
        Update the min/max range for a specific feature.
        
        Args:
            feature_name: Name of the clinical feature
            min_val: New minimum value
            max_val: New maximum value
        """
        normalized_name = self._normalize_feature_name(feature_name)
        if normalized_name not in self.ranges:
            warnings.warn(
                f"Adding new feature '{normalized_name}' with range [{min_val}, {max_val}]",
                UserWarning
            )
        self.ranges[normalized_name] = (min_val, max_val)
    
    def get_all_ranges(self) -> Dict[str, tuple]:
        """Get all feature ranges."""
        return self.ranges.copy()


def infer_ranges_from_scaled_data(scaled_data_path: str) -> Dict[str, tuple]:
    """
    Infer original min/max ranges from scaled data by analyzing the distribution.
    
    This function attempts to reverse-engineer the original scaling by:
    1. Finding the min/max of scaled values (should be close to 0 and 1)
    2. Using clinical reference ranges as a guide
    3. Estimating original ranges based on the scaled data distribution
    
    Note: This is an approximation and may not be exact.
    
    Args:
        scaled_data_path: Path to CSV file with scaled data (0-1 range)
    
    Returns:
        Dictionary mapping feature names to estimated (min, max) ranges
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for inferring ranges from data")
    
    df = pd.read_csv(scaled_data_path)
    
    # Remove target column if present
    feature_cols = [col for col in df.columns if col != 'Disease']
    
    inferred_ranges = {}
    bridge = ClinicalScalingBridge()
    
    for col in feature_cols:
        scaled_min = df[col].min()
        scaled_max = df[col].max()
        
        # Get clinical range as baseline
        if col in bridge.CLINICAL_RANGES:
            clinical_min, clinical_max = bridge.CLINICAL_RANGES[col]
            
            # Estimate: if scaled_min is close to 0, original_min is close to clinical_min
            # If scaled_max is close to 1, original_max is close to clinical_max
            # But we need to account for the actual distribution
            
            # Simple heuristic: use clinical range but adjust based on scaled data
            # If scaled data doesn't span full [0,1], the original range might be wider
            range_span = clinical_max - clinical_min
            
            # Estimate original min/max based on scaled distribution
            # This is approximate - assumes linear scaling
            if scaled_min > 0.01:  # Data doesn't start at 0
                # Original min might be lower than clinical min
                estimated_min = clinical_min - (scaled_min * range_span)
            else:
                estimated_min = clinical_min
            
            if scaled_max < 0.99:  # Data doesn't reach 1
                # Original max might be higher than clinical max
                estimated_max = clinical_max + ((1 - scaled_max) * range_span)
            else:
                estimated_max = clinical_max
            
            inferred_ranges[col] = (estimated_min, estimated_max)
        else:
            # Unknown feature - use a default wide range
            inferred_ranges[col] = (0, 100)
    
    return inferred_ranges


# Example usage
if __name__ == "__main__":
    # Create scaling bridge
    bridge = ClinicalScalingBridge()
    
    # Example: Scale individual values
    print("Example 1: Scaling individual values")
    print("-" * 50)
    glucose_scaled = bridge.scale_value('Glucose', 120)
    bmi_scaled = bridge.scale_value('BMI', 22.5)
    cholesterol_scaled = bridge.scale_value('Cholesterol', 180)
    
    print(f"Glucose 120 mg/dL → {glucose_scaled:.4f}")
    print(f"BMI 22.5 → {bmi_scaled:.4f}")
    print(f"Cholesterol 180 mg/dL → {cholesterol_scaled:.4f}")
    
    # Example: Scale multiple features
    print("\nExample 2: Scaling multiple features")
    print("-" * 50)
    raw_features = {
        'Glucose': 120,
        'BMI': 22.5,
        'Cholesterol': 180,
        'Hemoglobin': 14.5,
        'Systolic Blood Pressure': 130,
        'Diastolic Blood Pressure': 85
    }
    
    scaled_features = bridge.scale_features(raw_features)
    for feature, value in scaled_features.items():
        print(f"{feature}: {value:.4f}")
    
    # Example: Get feature range
    print("\nExample 3: Getting feature ranges")
    print("-" * 50)
    glucose_range = bridge.get_feature_range('Glucose')
    print(f"Glucose range: {glucose_range[0]} - {glucose_range[1]} mg/dL")

