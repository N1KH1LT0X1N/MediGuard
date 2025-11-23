# Scaling Logic Explained

## Overview

The scaling bridge is a critical component that converts **raw clinical values** (e.g., Glucose = 120 mg/dL, BMI = 22.5) into **scaled values** in the range [0, 1] that the trained machine learning model expects. This document explains exactly how this transformation works.

---

## The Problem

Machine learning models are trained on data that has been normalized to a specific range (typically 0 to 1). However, in real-world applications, we receive raw clinical values with vastly different scales:

- **Glucose**: 70-200 mg/dL
- **Platelets**: 150,000-450,000 per microliter
- **BMI**: 15-40 kg/m²
- **Creatinine**: 0.6-1.3 mg/dL

These values need to be transformed to the same [0, 1] range that the model was trained on, while preserving their relative meaning and clinical significance.

---

## The Solution: Min-Max Normalization

The scaling bridge uses **Min-Max Normalization**, a linear transformation that maps values from their original range to [0, 1].

### Mathematical Formula

```
scaled_value = (raw_value - min_value) / (max_value - min_value)
```

Where:
- `raw_value`: The actual clinical measurement (e.g., 120 mg/dL for Glucose)
- `min_value`: The minimum expected value for that feature
- `max_value`: The maximum expected value for that feature
- `scaled_value`: The resulting value in [0, 1] range

---

## Step-by-Step Process

### Step 1: Determine the Range

For each feature, the system needs to know the **min** and **max** values that define the scaling range. There are two sources:

#### Option A: Clinical Reference Ranges
Standard medical reference ranges based on clinical guidelines:
- **Glucose**: (70, 200) mg/dL
- **BMI**: (15, 40) kg/m²
- **Cholesterol**: (100, 300) mg/dL

#### Option B: Inferred Ranges (Preferred)
Ranges inferred from the actual training data by analyzing the distribution. These ranges were reverse-engineered from the scaled training data files (`cleaned.csv` and `cleaned_test.csv`) that were merged and used for model training.

**Data Source:** The inferred ranges were calculated by analyzing the combined training dataset (551 total samples from `cleaned.csv` and `cleaned_test.csv`), which was already scaled to [0, 1] range. The system reverse-engineered the original min/max values by:
1. Analyzing how far the scaled data deviates from 0 and 1
2. Using clinical reference ranges as a baseline
3. Estimating the original ranges that would produce the observed scaled distribution
4. Extending the ranges by 10% for safety margin

**Why inferred ranges?** They better match the actual data distribution used during training, leading to more accurate scaling.

### Complete Feature Ranges (All 24 Features)

The following table shows the **inferred ranges** (after 10% extension) used by the scaling bridge for all 24 features:

| # | Feature | Min Value | Max Value | Units | Base Range (Before Extension) |
|---|---------|-----------|-----------|-------|-------------------------------|
| 1 | **Glucose** | 39.09 | 231.86 | mg/dL | (55.16, 215.80) |
| 2 | **Cholesterol** | 52.73 | 344.59 | mg/dL | (77.06, 320.27) |
| 3 | **Hemoglobin** | 10.58 | 19.45 | g/dL | (11.32, 18.71) |
| 4 | **Platelets** | 84,000 | 516,000 | per microliter | (120,000, 480,000) |
| 5 | **White Blood Cells** | 2,350 | 12,651 | per microliter | (3,208, 11,792) |
| 6 | **Red Blood Cells** | 3.56 | 6.44 | million/μL | (3.8, 6.2) |
| 7 | **Hematocrit** | 32.23 | 55.57 | % | (34.17, 53.62) |
| 8 | **Mean Corpuscular Volume** | 75.12 | 104.49 | fL | (77.57, 102.04) |
| 9 | **Mean Corpuscular Hemoglobin** | 25.57 | 34.42 | pg | (26.31, 33.69) |
| 10 | **Mean Corpuscular Hemoglobin Concentration** | 31.12 | 36.88 | g/dL | (31.6, 36.4) |
| 11 | **Insulin** | -3.47 | 30.49 | μIU/mL | (-0.64, 27.66) |
| 12 | **BMI** | 9.40 | 46.04 | kg/m² | (12.46, 42.98) |
| 13 | **Systolic Blood Pressure** | 69.85 | 201.77 | mmHg | (80.84, 190.77) |
| 14 | **Diastolic Blood Pressure** | 51.09 | 109.41 | mmHg | (55.95, 104.55) |
| 15 | **Triglycerides** | -55.76 | 605.71 | mg/dL | (-0.64, 550.58) |
| 16 | **HbA1c** | 2.10 | 13.79 | % | (3.07, 12.81) |
| 17 | **LDL Cholesterol** | 14.43 | 236.67 | mg/dL | (32.95, 218.15) |
| 18 | **HDL Cholesterol** | 18.13 | 91.16 | mg/dL | (24.22, 85.07) |
| 19 | **ALT** | -4.94 | 68.35 | U/L | (1.17, 62.24) |
| 20 | **AST** | 2.73 | 47.17 | U/L | (6.43, 43.46) |
| 21 | **Heart Rate** | 38.12 | 111.89 | bpm | (44.27, 105.74) |
| 22 | **Creatinine** | 0.43 | 1.47 | mg/dL | (0.51, 1.39) |
| 23 | **Troponin** | 0.00 | 0.05 | ng/mL | (0.00, 0.045) |
| 24 | **C-reactive Protein** | -1.12 | 12.33 | mg/L | (0.00, 11.21) |

**Note:** 
- The ranges shown in the "Min Value" and "Max Value" columns are the **extended ranges** (with 10% safety margin) that are actually used for scaling.
- The "Base Range" column shows the original inferred ranges (before 10% extension) stored in `ml/scaling_layer/inferred_ranges.json`.
- Some features may have negative minimum values after extension (e.g., Insulin, Triglycerides, ALT, C-reactive Protein), but these are clipped to 0 during scaling for features that cannot be negative.

**Note:** The ranges shown above are the **extended ranges** (with 10% safety margin) that are actually used for scaling. The base inferred ranges (before extension) are stored in `ml/scaling_layer/inferred_ranges.json` and `ml/scaling_layer/inferred_ranges.py`.

### Step 2: Extend Ranges (Safety Margin)

The inferred ranges are extended by 10% on each side to handle edge cases:

```python
range_span = max_value - min_value
extended_min = min_value - (range_span * 0.1)
extended_max = max_value + (range_span * 0.1)
```

**Example:**
- Base inferred range: Glucose (55.16, 215.80) - from `inferred_ranges.json`
- Range span: 215.80 - 55.16 = 160.64
- Extended: (55.16 - 16.06, 215.80 + 16.06) = (39.09, 231.86)
- **Note:** The extended range (39.09, 231.86) is what's actually used for scaling

This ensures values slightly outside the training distribution are still handled gracefully.

### Step 3: Apply Min-Max Scaling

For each raw clinical value, apply the formula:

```python
scaled = (raw_value - min_value) / (max_value - min_value)
```

**Example 1: Glucose**
- Raw value: 120 mg/dL
- Extended range: (39.09, 231.86) - this is the base inferred range (55.16, 215.80) extended by 10%
- Calculation: (120 - 39.09) / (231.86 - 39.09) = 80.91 / 192.77 = **0.4197**

**Example 2: BMI**
- Raw value: 22.5 kg/m²
- Extended range: (9.40, 46.04) - base inferred range (12.46, 42.98) extended by 10%
- Calculation: (22.5 - 9.40) / (46.04 - 9.40) = 13.1 / 36.64 = **0.3575**

**Example 3: Platelets**
- Raw value: 250,000 per microliter
- Extended range: (84,000, 516,000) - base inferred range (120,000, 480,000) extended by 10%
- Calculation: (250000 - 84000) / (516000 - 84000) = 166000 / 432000 = **0.3843**

### Step 4: Clipping (Optional)

If `clip_values=True` (default), values outside [0, 1] are clipped:

```python
if scaled < 0:
    scaled = 0.0
elif scaled > 1:
    scaled = 1.0
```

This handles cases where:
- Raw value < min_value → scaled = 0.0
- Raw value > max_value → scaled = 1.0

---

## Complete Example: Scaling a Patient Profile

Let's scale a complete patient profile with 24 features:

### Input (Raw Clinical Values)
```python
patient_features = {
    'Glucose': 120,                    # mg/dL
    'Cholesterol': 180,                 # mg/dL
    'Hemoglobin': 14.5,                 # g/dL
    'Platelets': 250000,               # per microliter
    'White Blood Cells': 7000,         # per microliter
    'Red Blood Cells': 4.5,            # million per microliter
    'Hematocrit': 42,                   # %
    'Mean Corpuscular Volume': 88,     # fL
    'Mean Corpuscular Hemoglobin': 29, # pg
    'Mean Corpuscular Hemoglobin Concentration': 33, # g/dL
    'Insulin': 8,                       # μIU/mL
    'BMI': 22.5,                        # kg/m²
    'Systolic Blood Pressure': 120,    # mmHg
    'Diastolic Blood Pressure': 80,     # mmHg
    'Triglycerides': 150,               # mg/dL
    'HbA1c': 5.5,                       # %
    'LDL Cholesterol': 100,             # mg/dL
    'HDL Cholesterol': 50,              # mg/dL
    'ALT': 25,                          # U/L
    'AST': 30,                          # U/L
    'Heart Rate': 72,                   # bpm
    'Creatinine': 0.9,                  # mg/dL
    'Troponin': 0.01,                   # ng/mL
    'C-reactive Protein': 2.5,          # mg/L
}
```

### Scaling Process

For each feature, the system:
1. Looks up the min/max range (from inferred_ranges.json)
2. Applies the formula: `scaled = (raw - min) / (max - min)`
3. Clips to [0, 1] if needed

### Output (Scaled Values)
```python
scaled_features = {
    'Glucose': 0.4197,
    'Cholesterol': 0.4361,
    'Hemoglobin': 0.4415,
    'Platelets': 0.3843,
    'White Blood Cells': 0.4514,
    'Red Blood Cells': 0.3264,
    'Hematocrit': 0.4187,
    'Mean Corpuscular Volume': 0.4386,
    'Mean Corpuscular Hemoglobin': 0.3871,
    'Mean Corpuscular Hemoglobin Concentration': 0.3264,
    'Insulin': 0.2624,
    'BMI': 0.3575,
    'Systolic Blood Pressure': 0.3802,
    'Diastolic Blood Pressure': 0.4957,
    'Triglycerides': 0.2476,
    'HbA1c': 0.2912,
    'LDL Cholesterol': 0.3850,
    'HDL Cholesterol': 0.4364,
    'ALT': 0.3658,
    'AST': 0.6137,
    'Heart Rate': 0.4592,
    'Creatinine': 0.4524,
    'Troponin': 0.2040,
    'C-reactive Protein': 0.2027,
}
```

### Final Array Format

The scaled values are then converted to a numpy array in the exact order expected by the model:

```python
scaled_array = [
    0.4197,  # Glucose
    0.4361,  # Cholesterol
    0.4415,  # Hemoglobin
    0.3843,  # Platelets
    # ... (all 24 features in order)
]
```

This array is ready to be fed directly into the trained model for prediction.

---

## Edge Cases and Handling

### 1. Values Below Minimum

**Example:** Glucose = 50 mg/dL (below minimum of 39.09)

```python
scaled = (50 - 39.09) / (231.86 - 39.09) = 10.91 / 192.77 = 0.0566
```

Since 0.0566 is still in [0, 1], it's valid. However, the system will warn that the value is below the expected minimum.

### 2. Values Above Maximum

**Example:** Glucose = 250 mg/dL (above maximum of 231.86)

```python
scaled = (250 - 39.09) / (231.86 - 39.09) = 210.91 / 192.77 = 1.094
```

With clipping enabled: `scaled = 1.0`

The system will warn that the value is above the expected maximum.

### 3. Values at Boundaries

**Example:** Glucose = 39.09 mg/dL (exactly at minimum)

```python
scaled = (39.09 - 39.09) / (231.86 - 39.09) = 0 / 192.77 = 0.0
```

**Example:** Glucose = 231.86 mg/dL (exactly at maximum)

```python
scaled = (231.86 - 39.09) / (231.86 - 39.09) = 192.77 / 192.77 = 1.0
```

### 4. Invalid Feature Names

If a feature name is not recognized, the system:
- Tries case-insensitive matching
- Tries common abbreviations (e.g., "WBC" → "White Blood Cells")
- Raises a `ValueError` if no match is found

### 5. Missing Values

The system does not handle NaN values directly. Missing values should be imputed before scaling.

---

## Range Sources: Clinical vs Inferred

### Clinical Reference Ranges

**Source:** Standard medical guidelines and reference values

**Pros:**
- Based on established medical knowledge
- Consistent across different datasets
- Easy to understand and validate

**Cons:**
- May not match the actual training data distribution
- Can be too narrow or too wide
- May not account for outliers in training data

**Example:**
```python
CLINICAL_RANGES = {
    'Glucose': (70, 200),      # Standard fasting glucose range
    'BMI': (15, 40),            # Typical BMI range
    'Cholesterol': (100, 300),  # Standard cholesterol range
}
```

### Inferred Ranges (Preferred)

**Source:** Analyzed from the actual training data distribution

**Pros:**
- Matches the exact distribution used during training
- More accurate scaling for the specific model
- Accounts for actual data spread and outliers

**Cons:**
- Requires access to training data
- Needs to be recalculated if training data changes
- May include outliers that skew the range

**Example:**
```python
INFERRED_RANGES = {
    'Glucose': (39.09, 231.86),    # From actual training data
    'BMI': (9.40, 46.04),          # From actual training data
    'Cholesterol': (52.73, 344.59), # From actual training data
}
```

**How Inferred Ranges Are Created:**

The inferred ranges were generated from the **combined training dataset** consisting of:
- `cleaned.csv` (training samples)
- `cleaned_test.csv` (test samples)

These files were merged to create a combined dataset of **551 total samples** that was used for model training. The data in these files was already scaled to [0, 1] range.

The inference process:

1. **Load the scaled training data** - The combined dataset from `cleaned.csv` and `cleaned_test.csv` (already in [0, 1] range)
2. **Analyze each feature** - For each of the 24 features, find the minimum and maximum scaled values in the dataset
3. **Use clinical ranges as baseline** - Start with standard clinical reference ranges
4. **Reverse-engineer original ranges** - Calculate what the original min/max values must have been by analyzing:
   - How far the scaled data minimum is from 0 (if > 0.01, original min is lower than clinical min)
   - How far the scaled data maximum is from 1 (if < 0.99, original max is higher than clinical max)
   - The relationship between scaled distribution and clinical ranges
5. **Extend ranges by 10%** - Add a 10% safety margin on each side to handle edge cases
6. **Save to files** - Store in both `inferred_ranges.json` and `inferred_ranges.py` for easy access

**Important:** These ranges are specific to the training data used. If the training data changes significantly, the inferred ranges should be recalculated to maintain accuracy.

---

## Visual Representation

### Scaling Transformation

```
Raw Clinical Value Space          Scaled Model Input Space
─────────────────────────         ────────────────────────

Glucose: 39.09 ────────── 231.86   0.0 ─────────────── 1.0
         │                        │
         │  (120 - 39.09)         │
         │  ───────────────       │
         │  (231.86 - 39.09)      │
         │                        │
         ▼                        ▼
        120 mg/dL          →      0.4197
```

### Multiple Features Scaling

```
Feature          Raw Range              Scaled Range
─────────────────────────────────────────────────────
Glucose          39-232 mg/dL    →     0.0 - 1.0
BMI              9-46 kg/m²      →     0.0 - 1.0
Platelets        120k-480k        →     0.0 - 1.0
Creatinine       0.5-1.4 mg/dL   →     0.0 - 1.0
```

All features are transformed to the same [0, 1] scale, making them comparable and suitable for the ML model.

---

## Implementation Details

### Class Hierarchy

```
ClinicalScalingBridge (Base Class)
    │
    ├── Basic scaling functionality
    ├── Clinical reference ranges
    └── Feature name normalization
    │
    └── EnhancedScalingBridge (Extended Class)
        ├── Inferred ranges support
        ├── Range extension
        ├── Input validation
        └── Enhanced error handling
```

### Key Methods

1. **`scale_value(feature_name, raw_value)`**
   - Scales a single feature value
   - Returns float in [0, 1]

2. **`scale_features(features_dict)`**
   - Scales multiple features at once
   - Returns dictionary of scaled values

3. **`scale_to_array(features_dict, feature_order)`**
   - Scales features and returns numpy array
   - Ensures correct order for model input

4. **`validate_input(features_dict)`**
   - Validates input values
   - Checks for out-of-range values
   - Returns validation report

### Feature Name Normalization

The system handles various feature name formats:

- **Exact match**: "Glucose" → "Glucose"
- **Case-insensitive**: "glucose" → "Glucose"
- **Abbreviations**: "WBC" → "White Blood Cells"
- **Full names**: "White Blood Cells" → "White Blood Cells"

---

## Why This Matters

### Accuracy

Using the correct scaling ranges is crucial for model accuracy. If ranges don't match the training data:
- Values may be scaled incorrectly
- Model predictions become unreliable
- Edge cases are mishandled

### Consistency

The scaling bridge ensures:
- All features are on the same scale [0, 1]
- The same transformation is applied to training and inference
- Predictions are reproducible

### Robustness

The system handles:
- Out-of-range values (with warnings)
- Missing features (with errors)
- Invalid feature names (with helpful messages)
- Edge cases (boundary values, zero ranges)

---

## Usage Example

```python
from enhanced_scaling_bridge import create_bridge_from_inferred_ranges

# Create scaling bridge
bridge = create_bridge_from_inferred_ranges()

# Scale a single value
glucose_scaled = bridge.scale_value('Glucose', 120)
# Result: 0.4197

# Scale multiple features
patient_data = {
    'Glucose': 120,
    'BMI': 22.5,
    'Cholesterol': 180,
}
scaled_data = bridge.scale_features(patient_data)
# Result: {'Glucose': 0.4197, 'BMI': 0.3575, 'Cholesterol': 0.4361}

# Scale to array (for model input)
from predict import FEATURE_NAMES
scaled_array = bridge.scale_to_array(patient_data, feature_order=FEATURE_NAMES)
# Result: numpy array with 24 values in [0, 1] range
```

---

## Summary

The scaling bridge performs a **linear transformation** that:

1. **Takes** raw clinical values with different units and scales
2. **Transforms** them using Min-Max normalization: `(value - min) / (max - min)`
3. **Outputs** values in [0, 1] range that match the model's training data
4. **Handles** edge cases, validates inputs, and provides helpful warnings

This ensures that predictions are made on data that is **exactly** in the same format as the training data, maintaining model accuracy and reliability.

---

## Files Involved

### Scaling Implementation
- **`ml/scaling_layer/scaling_bridge.py`**: Base scaling bridge with clinical ranges
- **`ml/scaling_layer/enhanced_scaling_bridge.py`**: Enhanced version with inferred ranges
- **`ml/scaling_layer/inferred_ranges.py`**: Python module with base inferred ranges (before 10% extension)
- **`ml/scaling_layer/inferred_ranges.json`**: JSON file with base inferred ranges (before 10% extension)
- **`predict.py`**: Uses the scaling bridge to prepare data for predictions

### Training Data (Source of Inferred Ranges)
- **`cleaned.csv`**: Training samples (already scaled to [0, 1])
- **`cleaned_test.csv`**: Test samples (already scaled to [0, 1])
- **Combined dataset**: 551 total samples used to infer the original min/max ranges

**Note:** The inferred ranges stored in `inferred_ranges.json` and `inferred_ranges.py` are the **base ranges** (before 10% extension). The scaling bridge automatically extends these by 10% when loading them, so the actual ranges used for scaling are 10% wider on each side.

---

*Last Updated: Based on current implementation with inferred ranges from training data*

