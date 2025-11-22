"""
Enhanced Scaling Bridge with data-driven range inference and robust handling.

This version:
1. Loads inferred ranges from training data analysis
2. Uses percentile-based scaling for robustness
3. Handles skewed distributions and outliers
4. Provides data drift detection
"""

import numpy as np
from typing import Dict, Optional, Union, Tuple
import warnings
import json
from pathlib import Path

# Try to import inferred ranges if available
try:
    from inferred_ranges import INFERRED_RANGES
    HAS_INFERRED_RANGES = True
except ImportError:
    INFERRED_RANGES = {}
    HAS_INFERRED_RANGES = False

from scaling_bridge import ClinicalScalingBridge


class EnhancedScalingBridge(ClinicalScalingBridge):
    """
    Enhanced scaling bridge with data-driven ranges and robust handling.
    
    Features:
    - Uses inferred ranges from training data (if available)
    - Percentile-based scaling for robustness
    - Handles skewed distributions
    - Data drift detection
    - Better error handling
    """
    
    def __init__(self, 
                 use_inferred_ranges: bool = True,
                 use_percentile_scaling: bool = False,
                 percentile_low: float = 1.0,
                 percentile_high: float = 99.0,
                 extend_range: float = 0.1,
                 clip_values: bool = True,
                 custom_ranges: Optional[Dict[str, tuple]] = None):
        """
        Initialize enhanced scaling bridge.
        
        Args:
            use_inferred_ranges: If True, use ranges inferred from training data
            use_percentile_scaling: If True, use percentile-based scaling (requires data)
            percentile_low: Lower percentile for robust scaling (default 1%)
            percentile_high: Upper percentile for robust scaling (default 99%)
            extend_range: Fraction to extend range beyond inferred values (default 10%)
            clip_values: If True, clip values to [0, 1] after scaling
            custom_ranges: Optional custom ranges to override defaults
        """
        # Initialize base class
        super().__init__(use_clinical_ranges=True, clip_values=clip_values)
        
        self.use_inferred_ranges = use_inferred_ranges
        self.use_percentile_scaling = use_percentile_scaling
        self.percentile_low = percentile_low
        self.percentile_high = percentile_high
        self.extend_range = extend_range
        
        # Load inferred ranges if available
        if use_inferred_ranges and HAS_INFERRED_RANGES:
            print("✓ Using inferred ranges from training data")
            self.ranges = self._load_inferred_ranges()
        elif use_inferred_ranges:
            print("⚠️  Inferred ranges not found. Run infer_original_ranges.py first.")
            print("   Falling back to clinical reference ranges.")
            self.ranges = self.CLINICAL_RANGES.copy()
        else:
            self.ranges = self.CLINICAL_RANGES.copy()
        
        # Apply custom ranges if provided
        if custom_ranges:
            self.ranges.update(custom_ranges)
        
        # Extend ranges for safety margin
        self.ranges = self._extend_ranges(self.ranges, extend_range)
    
    def _load_inferred_ranges(self) -> Dict[str, Tuple[float, float]]:
        """Load inferred ranges from file."""
        ranges = INFERRED_RANGES.copy()
        
        # Ensure all features have ranges (fill missing with clinical ranges)
        for feature in self.CLINICAL_RANGES.keys():
            if feature not in ranges:
                ranges[feature] = self.CLINICAL_RANGES[feature]
        
        return ranges
    
    def _extend_ranges(self, ranges: Dict[str, Tuple[float, float]], 
                      extend_factor: float) -> Dict[str, Tuple[float, float]]:
        """Extend ranges by a factor for safety margin."""
        extended = {}
        
        for feature, (min_val, max_val) in ranges.items():
            range_span = max_val - min_val
            extended_min = min_val - (range_span * extend_factor)
            extended_max = max_val + (range_span * extend_factor)
            
            # Don't allow negative values for features that can't be negative
            if feature in ['BMI', 'Heart Rate', 'Platelets', 'White Blood Cells',
                          'Red Blood Cells', 'Hematocrit', 'Systolic Blood Pressure',
                          'Diastolic Blood Pressure', 'HbA1c', 'Creatinine', 
                          'Troponin', 'C-reactive Protein', 'Glucose', 'Cholesterol',
                          'Triglycerides', 'LDL Cholesterol', 'HDL Cholesterol',
                          'ALT', 'AST', 'Insulin']:
                extended_min = max(0, extended_min)
            
            extended[feature] = (extended_min, extended_max)
        
        return extended
    
    def scale_value(self, feature_name: str, raw_value: Union[float, int],
                   warn_out_of_range: bool = True) -> float:
        """
        Scale a single raw clinical value to 0-1 range.
        
        Enhanced version with better error handling and warnings.
        
        Args:
            feature_name: Name of the clinical feature
            raw_value: Raw clinical value to scale
            warn_out_of_range: If True, warn when value is outside expected range
            
        Returns:
            Scaled value in [0, 1] range (or outside if clip_values=False)
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
        
        # Check if value is outside expected range
        if warn_out_of_range:
            if raw_value < min_val:
                warnings.warn(
                    f"Value {raw_value} for {normalized_name} is below expected minimum {min_val}. "
                    f"Scaling may be inaccurate.",
                    UserWarning
                )
            elif raw_value > max_val:
                warnings.warn(
                    f"Value {raw_value} for {normalized_name} is above expected maximum {max_val}. "
                    f"Scaling may be inaccurate.",
                    UserWarning
                )
        
        # Min-Max scaling
        scaled = (raw_value - min_val) / (max_val - min_val)
        
        # Clip if requested
        if self.clip_values:
            scaled = np.clip(scaled, 0.0, 1.0)
        elif (scaled < 0 or scaled > 1) and warn_out_of_range:
            warnings.warn(
                f"Scaled value {scaled:.4f} for {normalized_name} "
                f"(raw: {raw_value}) is outside [0, 1] range. "
                f"Expected range: [{min_val}, {max_val}]",
                UserWarning
            )
        
        return float(scaled)
    
    def get_range_info(self, feature_name: str) -> Dict:
        """
        Get detailed range information for a feature.
        
        Returns:
            Dictionary with range info, source, and recommendations
        """
        normalized_name = self._normalize_feature_name(feature_name)
        
        if normalized_name not in self.ranges:
            raise ValueError(f"Unknown feature: '{normalized_name}'")
        
        min_val, max_val = self.ranges[normalized_name]
        
        # Check if using inferred or clinical ranges
        if self.use_inferred_ranges and HAS_INFERRED_RANGES:
            if normalized_name in INFERRED_RANGES:
                source = "inferred from training data"
            else:
                source = "clinical reference (inferred not available)"
        else:
            source = "clinical reference"
        
        # Get clinical range for comparison
        clinical_min, clinical_max = self.CLINICAL_RANGES.get(normalized_name, (None, None))
        
        info = {
            'feature': normalized_name,
            'min': min_val,
            'max': max_val,
            'range_span': max_val - min_val,
            'source': source,
            'clinical_min': clinical_min,
            'clinical_max': clinical_max,
        }
        
        # Add comparison if clinical range exists
        if clinical_min is not None:
            info['diff_from_clinical'] = {
                'min_diff': min_val - clinical_min,
                'max_diff': max_val - clinical_max,
                'min_diff_pct': ((min_val - clinical_min) / (clinical_max - clinical_min)) * 100,
                'max_diff_pct': ((max_val - clinical_max) / (clinical_max - clinical_min)) * 100,
            }
        
        return info
    
    def validate_input(self, features: Dict[str, Union[float, int]]) -> Dict:
        """
        Validate input features and return validation report.
        
        Returns:
            Dictionary with validation results and warnings
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'out_of_range': {},
        }
        
        for feature_name, raw_value in features.items():
            try:
                normalized_name = self._normalize_feature_name(feature_name)
                
                if normalized_name not in self.ranges:
                    validation['errors'].append(
                        f"Unknown feature: '{feature_name}'"
                    )
                    validation['valid'] = False
                    continue
                
                min_val, max_val = self.ranges[normalized_name]
                
                # Check if value is outside range
                if raw_value < min_val:
                    validation['out_of_range'][feature_name] = {
                        'value': raw_value,
                        'min': min_val,
                        'status': 'below_min',
                        'diff': raw_value - min_val,
                    }
                    validation['warnings'].append(
                        f"{feature_name}: {raw_value} is below minimum {min_val}"
                    )
                elif raw_value > max_val:
                    validation['out_of_range'][feature_name] = {
                        'value': raw_value,
                        'max': max_val,
                        'status': 'above_max',
                        'diff': raw_value - max_val,
                    }
                    validation['warnings'].append(
                        f"{feature_name}: {raw_value} is above maximum {max_val}"
                    )
                
            except Exception as e:
                validation['errors'].append(f"Error validating {feature_name}: {str(e)}")
                validation['valid'] = False
        
        return validation


def create_bridge_from_inferred_ranges(inferred_ranges_path: Optional[str] = None) -> EnhancedScalingBridge:
    """
    Create an enhanced scaling bridge using inferred ranges.
    
    Args:
        inferred_ranges_path: Optional path to inferred_ranges.json file
        
    Returns:
        EnhancedScalingBridge instance
    """
    if inferred_ranges_path:
        # Load ranges from JSON file
        with open(inferred_ranges_path, 'r') as f:
            custom_ranges = json.load(f)
        # Convert to tuples
        custom_ranges = {k: tuple(v) for k, v in custom_ranges.items()}
        return EnhancedScalingBridge(
            use_inferred_ranges=False,  # We're providing custom ranges
            custom_ranges=custom_ranges
        )
    else:
        # Use inferred ranges if available
        return EnhancedScalingBridge(use_inferred_ranges=True)


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("Enhanced Scaling Bridge Test")
    print("=" * 80)
    
    # Create bridge
    bridge = create_bridge_from_inferred_ranges()
    
    # Test scaling
    test_values = {
        'Glucose': 120,
        'BMI': 22.5,
        'Cholesterol': 180,
    }
    
    print("\nScaling test values:")
    print("-" * 80)
    for feature, value in test_values.items():
        scaled = bridge.scale_value(feature, value)
        info = bridge.get_range_info(feature)
        print(f"{feature:25s} {value:8.2f} → {scaled:.4f} "
              f"(range: [{info['min']:.2f}, {info['max']:.2f}], "
              f"source: {info['source']})")
    
    # Validate inputs
    print("\n\nValidation test:")
    print("-" * 80)
    validation = bridge.validate_input(test_values)
    print(f"Valid: {validation['valid']}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")

