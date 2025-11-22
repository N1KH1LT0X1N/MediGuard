# Clinical Scaling Bridge

A crucial interface layer that accurately converts raw clinical inputs (e.g., BMI = 22.5, Glucose = 120 mg/dL) into the scaled format (0 to 1) required by the trained ML model.

## Overview

The Scaling Bridge implements the core logic to map real-world, raw clinical values into the 0 to 1 range used for model training. This is essential for ensuring that new patient data is properly formatted before being fed into the trained model.

## Features

- **Min-Max Normalization**: Uses standard Min-Max scaling formula
- **Clinical Reference Ranges**: Pre-configured with standard medical reference ranges for all 24 features
- **Flexible Input**: Accepts individual values or complete patient profiles
- **Array Output**: Can output numpy arrays ready for model input
- **Custom Ranges**: Supports updating ranges for fine-tuning
- **Error Handling**: Validates inputs and handles edge cases

## Installation

No additional dependencies beyond standard Python libraries:
- `numpy`
- `typing` (built-in)

## Quick Start

### Basic Usage

```python
from scaling_bridge import ClinicalScalingBridge

# Create bridge instance
bridge = ClinicalScalingBridge()

# Scale individual values
glucose_scaled = bridge.scale_value('Glucose', 120)  # Returns 0.5 (approximately)
bmi_scaled = bridge.scale_value('BMI', 22.5)  # Returns ~0.5

# Scale multiple features
patient_data = {
    'Glucose': 120,
    'BMI': 22.5,
    'Cholesterol': 180,
    'Hemoglobin': 14.5,
    # ... all 24 features
}
scaled_features = bridge.scale_features(patient_data)

# Get array output for model
scaled_array = bridge.scale_to_array(patient_data)
```

### Integration with Model

```python
import pickle
import numpy as np
from scaling_bridge import ClinicalScalingBridge

# Load model
with open('disease_prediction_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load label encoder
with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

# Create bridge
bridge = ClinicalScalingBridge()

# Patient data (raw values)
patient_data = {
    'Glucose': 120,
    'BMI': 22.5,
    # ... all features
}

# Scale and predict
scaled_array = bridge.scale_to_array(patient_data).reshape(1, -1)
prediction = model.predict(scaled_array)
disease = label_encoder.inverse_transform(prediction)[0]

print(f"Predicted: {disease}")
```

## Supported Features

The bridge supports all 24 clinical features:

1. Glucose (mg/dL)
2. Cholesterol (mg/dL)
3. Hemoglobin (g/dL)
4. Platelets (per microliter)
5. White Blood Cells (per microliter)
6. Red Blood Cells (million per microliter)
7. Hematocrit (%)
8. Mean Corpuscular Volume (fL)
9. Mean Corpuscular Hemoglobin (pg)
10. Mean Corpuscular Hemoglobin Concentration (g/dL)
11. Insulin (μIU/mL)
12. BMI (kg/m²)
13. Systolic Blood Pressure (mmHg)
14. Diastolic Blood Pressure (mmHg)
15. Triglycerides (mg/dL)
16. HbA1c (%)
17. LDL Cholesterol (mg/dL)
18. HDL Cholesterol (mg/dL)
19. ALT (U/L)
20. AST (U/L)
21. Heart Rate (bpm)
22. Creatinine (mg/dL)
23. Troponin (ng/mL)
24. C-reactive Protein (mg/L)

## Clinical Reference Ranges

The bridge uses standard medical reference ranges for scaling. These can be customized if needed:

```python
# Update a specific range
bridge.update_range('Glucose', 60, 250)  # Custom min, max

# Get current range
min_val, max_val = bridge.get_feature_range('Glucose')
```

## Scaling Formula

The bridge uses Min-Max normalization:

```
scaled_value = (raw_value - min_value) / (max_value - min_value)
```

Values are automatically clipped to [0, 1] range by default, but this can be disabled.

## Testing

Run the test suite to verify functionality:

```bash
python test_scaling_bridge.py
```

## Files

- `scaling_bridge.py`: Main implementation
- `test_scaling_bridge.py`: Test suite
- `analyze_and_refine_ranges.py`: Analysis tool for refining ranges
- `creating_layer.ipynb`: Example notebook
- `README.md`: This file

## Notes

- The scaling ranges are based on clinical reference ranges, which may need adjustment based on your specific training data
- Values outside the expected range will be clipped to [0, 1] by default
- Feature names are case-insensitive and support common abbreviations (e.g., "WBC" for "White Blood Cells")

## Example Output

```
Glucose 120 mg/dL → 0.5000
BMI 22.5 → 0.5000
Cholesterol 180 mg/dL → 0.4000
```

## License

Part of the GGW Redact MediGuard project.

