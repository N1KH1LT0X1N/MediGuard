# MediGuard AI: Intelligent Triage Assistant - Project Context

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Project Architecture](#project-architecture)
4. [Implementation Status](#implementation-status)
5. [Technical Components](#technical-components)
6. [Data Pipeline](#data-pipeline)
7. [Model Details](#model-details)
8. [Scaling Bridge System](#scaling-bridge-system)
9. [Prediction System](#prediction-system)
10. [File Structure](#file-structure)
11. [Usage Guide](#usage-guide)
12. [Performance Metrics](#performance-metrics)
13. [Dependencies](#dependencies)
14. [Future Work](#future-work)
15. [Troubleshooting](#troubleshooting)

---

## Executive Summary

**MediGuard AI** is an Intelligent Triage Assistant that analyzes 24 pre-scaled blood test parameters to predict the likelihood of multiple diseases (Heart Disease, Diabetes, Anemia, Thalassemia, Thrombocytopenia, and Healthy status). The system serves as a crucial second opinion for triage nurses, routing patients efficiently and safely.

### Key Achievements

- ✅ **Module A (Model)**: Robust Multi-Class Classification model trained with XGBoost/Gradient Boosting
- ✅ **Module B (Scaling Bridge)**: Complete interface layer converting raw clinical inputs to scaled format
- ✅ **Module C (Frontend)**: React + Vite frontend with modern UI components (UI complete, backend integration pending)
- ⚠️ **Module C (Backend API)**: FastAPI backend pending implementation
- ⚠️ **Blockchain Feature**: Not yet implemented (planned: Immutable logging of predictions)

### Current Status

- **Model Training**: Complete and production-ready
- **Scaling Bridge**: Fully functional with inferred ranges
- **CLI Prediction Tool**: Complete and tested with explainability
- **Frontend UI**: Complete with React + Vite, routing, forms, and file upload interfaces
- **Backend API**: Pending implementation (FastAPI endpoints needed)
- **Frontend-Backend Integration**: Pending (API client and integration needed)
- **Blockchain Logging**: Pending implementation

---

## Problem Statement

### Original Requirements

**TITLE**: MediGuard AI: Intelligent Triage Assistant for Multi-Disease Prediction

**BRIEF EXPLANATION**: Develop an Intelligent Triage Assistant that analyzes 24 pre-scaled blood test parameters (e.g., Glucose, Troponin, BMI) to predict the likelihood of multiple diseases (Heart Disease, Diabetes, etc.). The primary engineering challenge is to create a crucial interface layer that accurately converts raw clinical inputs (e.g., BMI = 22.5) into the scaled format (0 to 1) required by the trained ML model. The final output must be a dashboard with clear predictions and medical explainability.

### Core Challenges Addressed

1. **Multi-Disease Classification**: Predicting 6 different disease classes from 24 clinical features
2. **Scaling Bridge**: Converting raw clinical values (various units and scales) to normalized [0, 1] range
3. **Class Imbalance**: Handling rare diseases (e.g., Healthy: 4 samples) vs common ones (e.g., Diabetes: 62 samples)
4. **High Recall Requirement**: Minimizing dangerous False Negatives in medical diagnosis
5. **Explainability**: Providing feature-level insights for clinical decision-making

---

## Project Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    MediGuard AI System                          │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Module A:    │    │  Module B:    │    │  Module C:    │
│  ML Model     │    │  Scaling      │    │  Dashboard    │
│  Training     │    │  Bridge       │    │  (Frontend ✅) │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ XGBoost /     │    │ Enhanced       │    │ React + Vite  │
│ Gradient      │    │ Scaling        │    │ + Tailwind    │
│ Boosting      │    │ Bridge         │    │ (Backend ⚠️)  │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Prediction     │
                    │  Pipeline       │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Disease        │
                    │  Prediction     │
                    │  + Explainability│
                    └─────────────────┘
```

### Data Flow

```
Raw Clinical Values (24 features)
    │
    ▼
[Scaling Bridge] → Converts to [0, 1] range
    │
    ▼
Scaled Features Array (24 values)
    │
    ▼
[Trained Model] → Gradient Boosting Classifier
    │
    ▼
Prediction + Probabilities
    │
    ▼
[Label Decoder] → Disease Name
    │
    ▼
Output: Disease Prediction + Risk Indicators
```

---

## Implementation Status

### ✅ Completed Components

#### 1. **Module A: ML Model Training** (100% Complete)

- **File**: `train_model.py`
- **Status**: Production-ready
- **Features**:
  - Data loading and merging (`cleaned.csv` + `cleaned_test.csv`)
  - Missing value imputation (median strategy)
  - Stratified train-test split (80/20)
  - Label encoding (string → numeric)
  - Class imbalance handling (SMOTE or manual oversampling)
  - Gradient Boosting Classifier training
  - Model evaluation (accuracy, F1-score, confusion matrix)
  - Model pcanersistence (joblib format)
  - Label encoder persistence

#### 2. **Module B: Scaling Bridge** (100% Complete)

- **Files**:
  - `ml/scaling_layer/scaling_bridge.py` (base implementation)
  - `ml/scaling_layer/enhanced_scaling_bridge.py` (enhanced version)
  - `ml/scaling_layer/inferred_ranges.json` (data-driven ranges)
  - `ml/scaling_layer/inferred_ranges.py` (Python module)
- **Status**: Fully functional
- **Features**:
  - Min-Max normalization
  - Clinical reference ranges (24 features)
  - Inferred ranges from training data
  - 10% range extension for safety margin
  - Input validation
  - Edge case handling
  - Feature name normalization

#### 3. **Prediction CLI Tool** (100% Complete)

- **File**: `predict.py`
- **Status**: Production-ready
- **Features**:
  - Multiple input methods (positional args, CSV string, file)
  - Automatic scaling detection
  - Model loading with compatibility handling
  - Prediction with probabilities
  - JSON output support
  - Verbose mode for debugging
  - Input validation
  - Explainability integration (LIME-based)

#### 4. **Explainability Module** (100% Complete)

- **File**: `ml/explainability.py`
- **Status**: Production-ready
- **Features**:
  - LIME-based feature importance analysis
  - Interactive Plotly visualizations
  - Risk indicator charts
  - HTML export with interactive plots
  - Integration with prediction pipeline

#### 5. **Frontend Application** (UI Complete, Backend Integration Pending)

- **Directory**: `frontend/`
- **Status**: UI Complete (90%), Backend Integration Pending
- **Tech Stack**:
  - React 19.1.0
  - Vite 6.3.5
  - React Router DOM 7.9.6
  - Tailwind CSS 4.1.8
  - GSAP 3.13.0 (animations)
  - Framer Motion 12.23.24
  - Recharts 3.4.1 (data visualization)
- **Features Implemented**:
  - Landing page with hero section
  - Patient and Doctor dashboard layouts
  - Disease prediction interface with manual data entry
  - File upload UI (Image, PDF, CSV/Excel)
  - Form validation for all 24 clinical parameters
  - Responsive navigation components
  - Smooth animations and transitions
- **Features Pending**:
  - Backend API integration
  - Real-time prediction calls
  - File processing (OCR/parsing)
  - Data visualization of results
  - Explainability visualization integration

#### 6. **Documentation** (100% Complete)

- **Files**:
  - `MODEL_TRAINING_LOGIC.md` (comprehensive training documentation)
  - `SCALING_LOGIC_EXPLAINED.md` (detailed scaling documentation)
  - `ml/scaling_layer/README.md` (scaling bridge documentation)
  - `README.md` (project overview)

### ⚠️ Pending Components

#### 1. **Module C: Backend API** (0% Complete)

- **Status**: Not implemented
- **Tech Stack**:
  - **Backend**: FastAPI (Python)
  - **Architecture**: RESTful API with CORS support for React frontend
- **Required Endpoints**:
  - `POST /api/predict`: Accept 24 clinical values, return prediction
  - `POST /api/upload/image`: Process image files (OCR extraction)
  - `POST /api/upload/pdf`: Process PDF files (text extraction)
  - `POST /api/upload/csv`: Process CSV/Excel files (data parsing)
  - `GET /api/features`: Return feature names and metadata
- **Integration Requirements**:
  - Connect to existing `predict.py` functionality
  - Use existing scaling bridge
  - Integrate explainability module
  - Return JSON responses compatible with frontend
  - Handle file uploads and processing

#### 2. **Frontend-Backend Integration** (0% Complete)

- **Status**: Pending backend implementation
- **Required Work**:
  - Create API client utility (`src/lib/api.js` or `src/api/client.js`)
  - Update `PredictDisease.jsx` to call API endpoints
  - Add error handling and loading states
  - Display prediction results with visualizations
  - Integrate explainability results display
  - Add file upload processing feedback

#### 3. **Blockchain Feature** (0% Complete)

- **Status**: Not implemented
- **Requirements**:
  - Timestamp predictions
  - Create immutable log entries
  - Hash patient ID + prediction + timestamp
  - Conceptual blockchain implementation
  - Auditable medical record trail

---

## Technical Components

### 1. Model Training Pipeline (`train_model.py`)

#### Architecture

```
Data Loading → Preprocessing → Balancing → Training → Evaluation → Saving
```

#### Key Functions

**`prepare_datasets()`**

- Loads `cleaned.csv` and `cleaned_test.csv`
- Merges datasets (551 total samples)
- Handles missing values (median imputation)
- Performs stratified train-test split (80/20)
- Returns: X_train, X_test, y_train, y_test

**`preprocess_and_balance(X_train, y_train)`**

- Encodes disease labels (string → numeric)
- Handles class imbalance:
  - **SMOTE** (preferred): Synthetic Minority Oversampling
  - **Manual oversampling** (fallback): Duplicate minority classes
- Post-resampling cleanup
- Returns: X_train_resampled, y_train_resampled, label_encoder

**`train_gradient_boosting(X_train, y_train, X_test, y_test, le)`**

- Creates GradientBoostingClassifier
- Hyperparameters:
  - `n_estimators=100` (number of trees)
  - `learning_rate=0.1` (shrinkage factor)
  - `max_depth=3` (tree depth)
  - `random_state=42` (reproducibility)
- Trains model
- Evaluates on test set
- Returns: trained model

**`save_model(model, label_encoder, output_dir='.')`**

- Saves model as `disease_prediction_model.pkl`
- Saves encoder as `label_encoder.pkl`
- Verifies saved files
- Returns: success status

#### Model Performance

- **Accuracy**: ~95.5%
- **F1-Score (Weighted)**: ~0.95
- **Per-Class Performance**: Varies (common diseases: 95-99%, rare: 50-80%)

### 2. Scaling Bridge System

#### Architecture

```
Raw Clinical Values → Range Lookup → Min-Max Scaling → Clipping → Scaled Array
```

#### Components

**Base Class: `ClinicalScalingBridge`**

- Location: `ml/scaling_layer/scaling_bridge.py`
- Features:
  - Clinical reference ranges (24 features)
  - Min-Max normalization formula
  - Feature name normalization
  - Value clipping

**Enhanced Class: `EnhancedScalingBridge`**

- Location: `ml/scaling_layer/enhanced_scaling_bridge.py`
- Extends: `ClinicalScalingBridge`
- Additional Features:
  - Inferred ranges from training data
  - 10% range extension
  - Input validation
  - Range information queries
  - Better error handling

**Inferred Ranges**

- Location: `ml/scaling_layer/inferred_ranges.json`
- Source: Reverse-engineered from training data
- Method: Analyzed scaled data distribution to infer original min/max
- Extension: 10% safety margin applied automatically

#### Scaling Formula

```
scaled_value = (raw_value - min_value) / (max_value - min_value)
```

#### Example Transformation

```
Glucose: 120 mg/dL
  → Range: (39.09, 231.86) [extended from inferred base]
  → Scaled: (120 - 39.09) / (231.86 - 39.09) = 0.4197
```

### 3. Prediction System (`predict.py`)

#### Architecture

```
Input Parsing → Feature Dictionary → Scaling → Model Prediction → Output
```

#### Key Features

**Input Methods**

1. **Positional Arguments**: `python predict.py 120 180 14.5 ...`
2. **CSV String**: `python predict.py --csv "120,180,14.5,..."`
3. **File Input**: `python predict.py --file input.csv`

**Auto-Detection**

- Detects if inputs are already scaled (0-1 range)
- Automatically skips scaling for pre-scaled values

**Output Formats**

- **Human-readable**: Disease name + probabilities
- **JSON**: Structured output for API integration

**Error Handling**

- Numpy version compatibility workarounds
- Model loading fallbacks
- Input validation warnings

---

## Data Pipeline

### Training Data

**Source Files**

- `cleaned.csv`: 63 training samples
- `cleaned_test.csv`: 488 test samples
- **Combined**: 551 total samples

**Data Format**

- 24 feature columns (already scaled to [0, 1])
- 1 target column: `Disease` (categorical)

**Disease Classes**

1. **Anemia** (~25 samples)
2. **Diabetes** (~77 samples)
3. **Healthy** (~5 samples)
4. **Heart Di** (~10 samples)
5. **Thalasse** (~16 samples)
6. **Thromboc** (~5 samples)

### Data Preprocessing Pipeline

```
Raw CSV Files
    │
    ▼
[Load & Merge] → Combined Dataset (551 samples)
    │
    ▼
[Feature-Target Separation] → X (24 features), y (Disease)
    │
    ▼
[Missing Value Imputation] → Median imputation
    │
    ▼
[Stratified Split] → Train (440), Test (111)
    │
    ▼
[Label Encoding] → String → Numeric (0-5)
    │
    ▼
[Class Balancing] → SMOTE/Manual Oversampling
    │
    ▼
Balanced Training Set (~1,488 samples)
```

### Prediction Pipeline

```
Raw Clinical Values (24 features)
    │
    ▼
[Input Parsing] → Feature Dictionary
    │
    ▼
[Scaling Bridge] → Min-Max Normalization
    │
    ▼
Scaled Array (24 values in [0, 1])
    │
    ▼
[Model Prediction] → Numeric Class (0-5)
    │
    ▼
[Label Decoding] → Disease Name
    │
    ▼
Output: Disease + Probabilities
```

---

## Model Details

### Algorithm: Gradient Boosting Classifier

**Why Gradient Boosting?**

- Handles non-linear relationships
- Works with mixed feature types
- Provides feature importance
- Achieves high accuracy on medical data
- Handles class imbalance effectively

### Hyperparameters

| Parameter             | Value | Purpose                                          |
| --------------------- | ----- | ------------------------------------------------ |
| `n_estimators`      | 100   | Number of decision trees                         |
| `learning_rate`     | 0.1   | Shrinkage factor (prevents overfitting)          |
| `max_depth`         | 3     | Maximum tree depth (captures 3-way interactions) |
| `min_samples_split` | 2     | Minimum samples to split node                    |
| `min_samples_leaf`  | 1     | Minimum samples in leaf                          |
| `subsample`         | 1.0   | Fraction of samples per tree                     |
| `random_state`      | 42    | Reproducibility seed                             |

### Model Performance

**Overall Metrics**

- **Accuracy**: 95.50%
- **F1-Score (Weighted)**: 0.95
- **Macro F1**: 0.87

**Per-Class Performance** (Example)

```
              precision    recall  f1-score   support
      Anemia       0.95      0.95      0.95        20
    Diabetes       0.98      0.98      0.98        62
     Healthy       0.67      0.50      0.57         4
    Heart Di       0.89      1.00      0.94         8
    Thalasse       1.00      1.00      1.00        13
    Thromboc       0.75      0.75      0.75         4
```

**Key Observations**

- Common diseases (Diabetes, Anemia) have excellent performance
- Rare diseases (Healthy, Thromboc) have lower recall
- Model prioritizes recall (minimizing False Negatives) as required

### Feature Importance

The model tracks feature importance based on:

- Frequency of feature usage in splits
- Improvement in loss function from each feature

**Top Features** (Hypothetical - actual values from model)

- Glucose, HbA1c, Cholesterol, Hemoglobin, Troponin

---

## Scaling Bridge System

### Overview

The Scaling Bridge is the **critical interface layer** that converts raw clinical values into the [0, 1] range required by the trained model.

### Range Sources

#### 1. Clinical Reference Ranges

- **Source**: Standard medical guidelines
- **Pros**: Based on established medical knowledge
- **Cons**: May not match training data distribution

#### 2. Inferred Ranges (Preferred)

- **Source**: Reverse-engineered from training data
- **Method**: Analyzed scaled data to infer original min/max
- **Pros**: Matches exact training distribution
- **Cons**: Requires access to training data

### Complete Feature Ranges (24 Features)

| #  | Feature                                   | Min    | Max     | Units       | Extended Range        |
| -- | ----------------------------------------- | ------ | ------- | ----------- | --------------------- |
| 1  | Glucose                                   | 39.09  | 231.86  | mg/dL       | Base: (55.16, 215.80) |
| 2  | Cholesterol                               | 52.73  | 344.59  | mg/dL       | Base: (77.06, 320.27) |
| 3  | Hemoglobin                                | 10.58  | 19.45   | g/dL        | Base: (11.32, 18.71)  |
| 4  | Platelets                                 | 84,000 | 516,000 | /μL        | Base: (120k, 480k)    |
| 5  | White Blood Cells                         | 2,350  | 12,651  | /μL        | Base: (3,208, 11,792) |
| 6  | Red Blood Cells                           | 3.56   | 6.44    | million/μL | Base: (3.8, 6.2)      |
| 7  | Hematocrit                                | 32.23  | 55.57   | %           | Base: (34.17, 53.62)  |
| 8  | Mean Corpuscular Volume                   | 75.12  | 104.49  | fL          | Base: (77.57, 102.04) |
| 9  | Mean Corpuscular Hemoglobin               | 25.57  | 34.42   | pg          | Base: (26.31, 33.69)  |
| 10 | Mean Corpuscular Hemoglobin Concentration | 31.12  | 36.88   | g/dL        | Base: (31.6, 36.4)    |
| 11 | Insulin                                   | -3.47  | 30.49   | μIU/mL     | Base: (-0.64, 27.66)  |
| 12 | BMI                                       | 9.40   | 46.04   | kg/m²      | Base: (12.46, 42.98)  |
| 13 | Systolic Blood Pressure                   | 69.85  | 201.77  | mmHg        | Base: (80.84, 190.77) |
| 14 | Diastolic Blood Pressure                  | 51.09  | 109.41  | mmHg        | Base: (55.95, 104.55) |
| 15 | Triglycerides                             | -55.76 | 605.71  | mg/dL       | Base: (-0.64, 550.58) |
| 16 | HbA1c                                     | 2.10   | 13.79   | %           | Base: (3.07, 12.81)   |
| 17 | LDL Cholesterol                           | 14.43  | 236.67  | mg/dL       | Base: (32.95, 218.15) |
| 18 | HDL Cholesterol                           | 18.13  | 91.16   | mg/dL       | Base: (24.22, 85.07)  |
| 19 | ALT                                       | -4.94  | 68.35   | U/L         | Base: (1.17, 62.24)   |
| 20 | AST                                       | 2.73   | 47.17   | U/L         | Base: (6.43, 43.46)   |
| 21 | Heart Rate                                | 38.12  | 111.89  | bpm         | Base: (44.27, 105.74) |
| 22 | Creatinine                                | 0.43   | 1.47    | mg/dL       | Base: (0.51, 1.39)    |
| 23 | Troponin                                  | 0.00   | 0.05    | ng/mL       | Base: (0.00, 0.045)   |
| 24 | C-reactive Protein                        | -1.12  | 12.33   | mg/L        | Base: (0.00, 11.21)   |

**Note**: Extended ranges include 10% safety margin on each side.

### Scaling Process Example

**Input**: Complete patient profile

```python
{
    'Glucose': 120,           # mg/dL
    'BMI': 22.5,              # kg/m²
    'Cholesterol': 180,        # mg/dL
    'Hemoglobin': 14.5,        # g/dL
    # ... all 24 features
}
```

**Scaling**:

```python
Glucose: (120 - 39.09) / (231.86 - 39.09) = 0.4197
BMI: (22.5 - 9.40) / (46.04 - 9.40) = 0.3575
Cholesterol: (180 - 52.73) / (344.59 - 52.73) = 0.4361
# ... all 24 features
```

**Output**: Scaled array ready for model

```python
[0.4197, 0.4361, 0.4415, 0.3843, ...]  # 24 values in [0, 1]
```

---

## Prediction System

### CLI Tool: `predict.py`

#### Usage Examples

**1. Positional Arguments**

```bash
python predict.py 120 180 14.5 250000 7000 4.5 42 88 29 33 8 22.5 120 80 150 5.5 100 50 25 30 72 0.9 0.01 2.5
```

**2. CSV String**

```bash
python predict.py --csv "120,180,14.5,250000,7000,4.5,42,88,29,33,8,22.5,120,80,150,5.5,100,50,25,30,72,0.9,0.01,2.5"
```

**3. File Input**

```bash
python predict.py --file cleaned_test.csv
```

**4. Verbose Mode**

```bash
python predict.py --verbose 120 180 14.5 ...
```

**5. JSON Output**

```bash
python predict.py --json 120 180 14.5 ...
```

#### Output Format

**Human-Readable**

```
================================================================================
PREDICTION RESULT
================================================================================

Predicted Disease: Heart Di

Prediction Probabilities:
  Heart Di                         54.48%
  Healthy                          29.85%
  Diabetes                          7.01%
  ...

================================================================================
```

**JSON**

```json
{
  "predicted_disease": "Heart Di",
  "input_features": {
    "Glucose": 120,
    "BMI": 22.5,
    ...
  },
  "scaled_features": {
    "Glucose": 0.4197,
    "BMI": 0.3575,
    ...
  },
  "probabilities": {
    "Heart Di": 0.5448,
    "Healthy": 0.2985,
    ...
  }
}
```

---

## File Structure

```
ggw_redact/
│
├── train_model.py                 # Model training pipeline
├── predict.py                     # CLI prediction tool
│
├── disease_prediction_model.pkl   # Trained model (generated)
├── label_encoder.pkl              # Label encoder (generated)
│
├── cleaned.csv                    # Training data (63 samples)
├── cleaned_test.csv               # Test data (488 samples)
│
├── MODEL_TRAINING_LOGIC.md        # Comprehensive training docs
├── SCALING_LOGIC_EXPLAINED.md     # Detailed scaling docs
├── README.md                       # Project overview
├── PROJECT_CONTEXT.md             # This file
│
├── ml/
│   └── scaling_layer/
│       ├── scaling_bridge.py              # Base scaling bridge
│       ├── enhanced_scaling_bridge.py     # Enhanced version
│       ├── inferred_ranges.py            # Python ranges module
│       ├── inferred_ranges.json          # JSON ranges file
│       └── README.md                      # Scaling bridge docs
│
├── ml/
│   ├── explainability.py         # LIME-based explainability module
│   └── scaling_layer/
│       ├── scaling_bridge.py              # Base scaling bridge
│       ├── enhanced_scaling_bridge.py     # Enhanced version
│       ├── inferred_ranges.py            # Python ranges module
│       ├── inferred_ranges.json          # JSON ranges file
│       └── README.md                      # Scaling bridge docs
│
├── backend/                        # FastAPI backend (planned)
│   ├── api/
│   │   ├── main.py                # FastAPI application
│   │   ├── routes/
│   │   │   └── predict.py         # Prediction endpoints
│   │   └── models/
│   │       └── schemas.py         # Pydantic models
│   └── requirements.txt           # Python dependencies
│
└── frontend/                       # React + Vite frontend (✅ UI Complete)
    ├── src/
    │   ├── main.jsx               # React application entry point
    │   ├── App.jsx                # Main routing component
    │   ├── index.css              # Global styles with Tailwind
    │   ├── pages/                 # Page components
    │   │   ├── HomePage.jsx       # Landing page
    │   │   ├── PredictDisease.jsx # Disease prediction interface
    │   │   ├── PatientHomePage.jsx # Patient dashboard layout
    │   │   ├── DoctorHomePage.jsx # Doctor dashboard layout
    │   │   ├── patient/           # Patient-specific pages
    │   │   └── doctor/            # Doctor-specific pages
    │   ├── components/            # Reusable components
    │   │   ├── NavBar.jsx         # Main navigation
    │   │   ├── PatientNavBar.jsx  # Patient navigation
    │   │   ├── DoctorNavBar.jsx   # Doctor navigation
    │   │   └── ui/                # UI components
    │   ├── sections/              # Page sections
    │   │   ├── HeroSection.jsx     # Hero section
    │   │   ├── FooterSection.jsx   # Footer
    │   │   └── ...
    │   ├── constants/             # Constants
    │   └── lib/                    # Utilities
    ├── public/                    # Static assets
    │   ├── images/                # Image assets
    │   ├── videos/                # Video assets
    │   └── fonts/                 # Custom fonts
    ├── package.json               # Node.js dependencies
    └── vite.config.js            # Vite configuration
```

### File Descriptions

**Core Scripts**

- `train_model.py`: Complete training pipeline (284 lines)
- `predict.py`: CLI prediction tool (479 lines)

**Model Files** (Generated)

- `disease_prediction_model.pkl`: Trained Gradient Boosting model
- `label_encoder.pkl`: Disease label encoder

**Data Files**

- `cleaned.csv`: Training samples (63 rows, 25 columns)
- `cleaned_test.csv`: Test samples (488 rows, 25 columns)

**Documentation**

- `MODEL_TRAINING_LOGIC.md`: 936 lines of training documentation
- `SCALING_LOGIC_EXPLAINED.md`: 540 lines of scaling documentation
- `PROJECT_CONTEXT.md`: This comprehensive context document

**Scaling Layer**

- `scaling_bridge.py`: Base implementation with clinical ranges
- `enhanced_scaling_bridge.py`: Enhanced version with inferred ranges
- `inferred_ranges.json`: Data-driven ranges (24 features)
- `inferred_ranges.py`: Python module version

**Explainability Module**

- `ml/explainability.py`: LIME-based explainability with Plotly visualizations

**Backend** (Planned)

- `backend/api/main.py`: FastAPI application with prediction endpoints
- `backend/api/routes/predict.py`: Prediction route handlers
- `backend/api/models/schemas.py`: Pydantic request/response models

**Frontend** (✅ UI Complete, Backend Integration Pending)

- `frontend/src/App.jsx`: Main React routing component
- `frontend/src/pages/PredictDisease.jsx`: Disease prediction interface with manual entry and file upload
- `frontend/src/pages/HomePage.jsx`: Landing page with hero section
- `frontend/src/components/NavBar.jsx`: Navigation components
- `frontend/src/sections/HeroSection.jsx`: Animated hero section
- `frontend/src/index.css`: Global styles with Tailwind CSS
- `frontend/package.json`: Dependencies (React, Vite, GSAP, Framer Motion, Recharts)

---

## Usage Guide

### Training the Model

**Step 1: Prepare Data**

- Ensure `cleaned.csv` and `cleaned_test.csv` are in the project root
- Data should have 24 feature columns + 1 Disease column

**Step 2: Install Dependencies**

```bash
pip install pandas numpy scikit-learn joblib imbalanced-learn
```

**Step 3: Run Training**

```bash
python train_model.py
```

**Output**

- `disease_prediction_model.pkl`: Trained model
- `label_encoder.pkl`: Label encoder
- Console output with performance metrics

### Making Predictions

**Method 1: Positional Arguments**

```bash
python predict.py 120 180 14.5 250000 7000 4.5 42 88 29 33 8 22.5 120 80 150 5.5 100 50 25 30 72 0.9 0.01 2.5
```

**Method 2: CSV String**

```bash
python predict.py --csv "120,180,14.5,250000,7000,4.5,42,88,29,33,8,22.5,120,80,150,5.5,100,50,25,30,72,0.9,0.01,2.5"
```

**Method 3: File Input**

```bash
python predict.py --file input.csv
```

**Options**

- `--verbose`: Show detailed scaling information
- `--json`: Output in JSON format
- `--model PATH`: Specify custom model path
- `--encoder PATH`: Specify custom encoder path
- `--already-scaled`: Skip scaling (for pre-scaled inputs)

### Feature Order (24 Features)

1. Glucose
2. Cholesterol
3. Hemoglobin
4. Platelets
5. White Blood Cells
6. Red Blood Cells
7. Hematocrit
8. Mean Corpuscular Volume
9. Mean Corpuscular Hemoglobin
10. Mean Corpuscular Hemoglobin Concentration
11. Insulin
12. BMI
13. Systolic Blood Pressure
14. Diastolic Blood Pressure
15. Triglycerides
16. HbA1c
17. LDL Cholesterol
18. HDL Cholesterol
19. ALT
20. AST
21. Heart Rate
22. Creatinine
23. Troponin
24. C-reactive Protein

---

## Performance Metrics

### Model Performance

**Overall Metrics**

- **Accuracy**: 95.50%
- **F1-Score (Weighted)**: 0.95
- **Macro F1**: 0.87

**Per-Class Metrics** (Test Set)

- **Anemia**: Precision 0.95, Recall 0.95, F1 0.95
- **Diabetes**: Precision 0.98, Recall 0.98, F1 0.98
- **Healthy**: Precision 0.67, Recall 0.50, F1 0.57
- **Heart Di**: Precision 0.89, Recall 1.00, F1 0.94
- **Thalasse**: Precision 1.00, Recall 1.00, F1 1.00
- **Thromboc**: Precision 0.75, Recall 0.75, F1 0.75

**Key Observations**

- High recall for critical diseases (Heart Di: 100%)
- Common diseases have excellent performance
- Rare diseases have lower but acceptable performance
- Model prioritizes recall (minimizing False Negatives)

### Scaling Bridge Accuracy

**Range Coverage**

- All 24 features have inferred ranges
- 10% safety margin extends ranges
- Handles edge cases gracefully

**Validation**

- Input validation warns about out-of-range values
- Clipping ensures values stay in [0, 1]
- Feature name normalization handles variations

---

## Dependencies

### Python Version

- **Required**: Python 3.7+
- **Recommended**: Python 3.8+

### Core Libraries

**Data Processing**

- `pandas`: Data manipulation and CSV handling
- `numpy`: Numerical operations and arrays

**Machine Learning**

- `scikit-learn`: Model training and evaluation
  - `GradientBoostingClassifier`
  - `LabelEncoder`
  - `SimpleImputer`
  - `train_test_split`
  - `classification_report`, `confusion_matrix`, `accuracy_score`, `f1_score`

**Model Persistence**

- `joblib`: Efficient model serialization

**Class Balancing** (Optional but Recommended)

- `imbalanced-learn`: SMOTE for class balancing
  - Falls back to manual oversampling if not available

**Backend API** (For Dashboard - Planned)

- `fastapi`: Modern, fast web framework for building APIs
- `uvicorn`: ASGI server for FastAPI
- `pydantic`: Data validation using Python type annotations
- `python-multipart`: For handling form data

**Frontend** (For Dashboard - ✅ Implemented)

- `react` (19.1.0): UI library
- `vite` (6.3.5): Build tool and dev server
- `react-router-dom` (7.9.6): Client-side routing
- `tailwindcss` (4.1.8): Utility-first CSS framework
- `@tailwindcss/vite` (4.1.8): Vite plugin for Tailwind
- `gsap` (3.13.0): Animation library
- `@gsap/react` (2.1.2): React hooks for GSAP
- `framer-motion` (12.23.24): Animation library
- `recharts` (3.4.1): Data visualization
- `lucide-react` (0.554.0): Icon library
- `react-responsive` (10.0.1): Responsive design utilities
- `three` (0.181.2): 3D graphics library
- `dotted-map` (2.2.3): Map visualization

### Installation

**Backend (Python) - Minimal Installation**

```bash
pip install pandas numpy scikit-learn joblib
```

**Backend (Python) - Full Installation** (Recommended)

```bash
pip install pandas numpy scikit-learn joblib imbalanced-learn
```

**Backend (Python) - With FastAPI** (For Dashboard)

```bash
pip install fastapi uvicorn pydantic python-multipart
```

**Frontend (Node.js) - Setup** (✅ Already Configured)

```bash
cd frontend
npm install
npm run dev  # Start development server
```

**Frontend (Node.js) - Production Build**

```bash
cd frontend
npm run build  # Build for production
npm run preview  # Preview production build
```

### Version Compatibility

**Known Issues**

- Numpy version compatibility with saved models
- Workarounds implemented in `predict.py`

**Solutions**

- Use consistent numpy versions for training and prediction
- Or re-save model with current numpy version

---

## Future Work

### 1. Backend API Implementation (Module C - Backend)

**Status**: Not Started

**Tech Stack**

- **Backend**: FastAPI (Python)
- **Architecture**: RESTful API with CORS support for React frontend

**Requirements**

- Prediction endpoint accepting 24 clinical values
- File upload endpoints (image, PDF, CSV)
- Integration with existing `predict.py` functionality
- Integration with explainability module
- JSON responses compatible with frontend
- Error handling and validation

**Implementation Plan**

**Backend: FastAPI** (`backend/api/main.py`)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from predict import predict, FEATURE_NAMES, load_model, create_bridge_from_inferred_ranges

app = FastAPI(title="MediGuard AI API")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and bridge once at startup
model, label_encoder = load_model(
    Path(__file__).parent.parent.parent / "disease_prediction_model.pkl",
    Path(__file__).parent.parent.parent / "label_encoder.pkl"
)
bridge = create_bridge_from_inferred_ranges()

class PredictionRequest(BaseModel):
    features: Dict[str, float]

class PredictionResponse(BaseModel):
    predicted_disease: str
    probabilities: Dict[str, float]
    scaled_features: Dict[str, float]
    input_features: Dict[str, float]

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_disease(request: PredictionRequest):
    try:
        disease, prediction_proba, scaled_array = predict(
            model, label_encoder, bridge, request.features
        )
      
        classes = label_encoder.classes_
        probabilities = {
            cls: float(prob) for cls, prob in zip(classes, prediction_proba)
        }
      
        scaled_features = {
            name: float(val) for name, val in zip(FEATURE_NAMES, scaled_array[0])
        }
      
        return PredictionResponse(
            predicted_disease=disease,
            probabilities=probabilities,
            scaled_features=scaled_features,
            input_features=request.features
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/features")
async def get_features():
    return {"features": FEATURE_NAMES}
```

**Frontend Integration** (Update `frontend/src/pages/PredictDisease.jsx`)

**Frontend Integration Steps**

1. Create API client utility (`frontend/src/lib/api.js`):
```javascript
const API_BASE_URL = 'http://localhost:8000/api';

export const predictDisease = async (features) => {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ features })
  });
  return response.json();
};
```

2. Update `PredictDisease.jsx` to integrate API calls
3. Add loading states and error handling
4. Display prediction results with Recharts visualizations
5. Integrate explainability results display

**Features to Implement**

1. **API Integration**: Connect manual entry form to backend
2. **File Upload Processing**: Connect file uploads to backend endpoints
3. **Prediction Display**: Show disease prediction with probabilities
4. **Probability Visualization**: Use Recharts to display probability charts
5. **Feature Importance**: Display LIME-based feature importance
6. **Explainability Integration**: Show interactive explainability plots
7. **Error Handling**: User-friendly error messages and loading states

### 2. Blockchain Feature

**Status**: Not Started

**Requirements**

- Timestamp predictions
- Create immutable log entries
- Hash patient ID + prediction + timestamp
- Conceptual blockchain implementation
- Auditable medical record trail

**Proposed Implementation**

**Simple Blockchain Structure**

```python
# blockchain.py (to be created)
import hashlib
import json
from datetime import datetime

class MedicalBlock:
    def __init__(self, patient_id, prediction, timestamp, previous_hash):
        self.patient_id = patient_id
        self.prediction = prediction
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
  
    def calculate_hash(self):
        data = f"{self.patient_id}{self.prediction}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class MedicalBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
  
    def create_genesis_block(self):
        return MedicalBlock("GENESIS", "GENESIS", datetime.now(), "0")
  
    def add_prediction(self, patient_id, prediction):
        previous_block = self.chain[-1]
        new_block = MedicalBlock(
            patient_id, prediction, datetime.now(), previous_block.hash
        )
        self.chain.append(new_block)
        return new_block
  
    def verify_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
          
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True
```

**Integration with FastAPI Backend**

```python
# In backend/api/routes/predict.py
from blockchain import MedicalBlockchain

blockchain = MedicalBlockchain()

@app.post("/api/predict")
async def predict_disease(request: PredictionRequest):
    # ... prediction logic ...
  
    # Log to blockchain
    block = blockchain.add_prediction(patient_id, disease)
  
    return {
        "prediction": disease,
        "blockchain": {
            "block_number": len(blockchain.chain) - 1,
            "hash": block.hash,
            "timestamp": block.timestamp.isoformat()
        }
    }
```

**Features**

1. **Immutable Logging**: Each prediction creates a block
2. **Chain Verification**: Verify integrity of chain
3. **Audit Trail**: Complete history of all predictions
4. **Patient Privacy**: Hash patient IDs (not store directly)
5. **Timestamp**: Exact time of each prediction

### 3. Additional Enhancements

**Model Improvements**

- Hyperparameter tuning (GridSearchCV)
- Feature engineering
- Ensemble methods (combine multiple models)
- Cross-validation for better evaluation

**Scaling Bridge Improvements**

- Dynamic range updates
- Data drift detection
- Automatic range recalculation
- Support for new features

**Dashboard Enhancements**

- Patient history tracking
- Batch prediction support
- Export predictions to CSV/PDF
- Integration with hospital systems

**Explainability**

- SHAP values integration
- LIME explanations
- Feature interaction analysis
- Risk score visualization

---

## Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Error**: `ValueError: BitGenerator` or `MT19937` error
**Cause**: Numpy version incompatibility
**Solution**:

```bash
# Option 1: Update numpy
pip install --upgrade numpy

# Option 2: Re-save model with current numpy
python train_model.py

# Option 3: Use specific numpy version
pip install numpy==1.24.0
```

#### 2. Missing Data Files

**Error**: `FileNotFoundError: cleaned.csv not found`
**Solution**: Ensure data files are in project root directory

#### 3. Class Imbalance Warning

**Warning**: `Using manual oversampling fallback`
**Solution**: Install imbalanced-learn

```bash
pip install imbalanced-learn
```

#### 4. Scaling Bridge Import Error

**Error**: `Could not import EnhancedScalingBridge`
**Solution**: Ensure `ml/scaling_layer/` directory exists with all files

#### 5. Feature Count Mismatch

**Error**: `Expected 24 feature values, got X`
**Solution**: Check that all 24 features are provided in correct order

### Debugging Tips

**Verbose Mode**

```bash
python predict.py --verbose 120 180 ...
```

**Check Model**

```python
import joblib
model = joblib.load('disease_prediction_model.pkl')
print(type(model))
print(hasattr(model, 'predict'))
```

**Check Scaling**

```python
from ml.scaling_layer.enhanced_scaling_bridge import create_bridge_from_inferred_ranges
bridge = create_bridge_from_inferred_ranges()
scaled = bridge.scale_value('Glucose', 120)
print(f"Scaled: {scaled}")
```

---

## Summary

### What's Complete ✅

1. **Model Training**: Full pipeline with Gradient Boosting/XGBoost
2. **Scaling Bridge**: Complete with inferred ranges
3. **CLI Prediction Tool**: Fully functional with explainability
4. **Explainability Module**: LIME-based with Plotly visualizations
5. **Frontend UI**: Complete React + Vite application with:
   - Landing page with hero section
   - Patient and Doctor dashboard layouts
   - Disease prediction interface with manual entry
   - File upload UI for images, PDFs, and CSV
   - Form validation for all 24 clinical parameters
   - Responsive navigation and animations
6. **Documentation**: Comprehensive docs for all components

### What's Pending ⚠️

1. **Backend API**: FastAPI implementation with prediction endpoints
2. **Frontend-Backend Integration**: API client and integration
3. **File Processing**: OCR for images/PDFs, CSV parsing
4. **Blockchain**: Immutable logging of predictions
5. **Real-time Predictions**: Live prediction calls from frontend

### Key Achievements

- ✅ 95.5% accuracy on test set
- ✅ High recall for critical diseases
- ✅ Robust scaling bridge with inferred ranges
- ✅ Production-ready prediction pipeline
- ✅ Comprehensive documentation

### Next Steps

1. ✅ ~~Implement React + Vite frontend~~ (Complete)
2. Build FastAPI backend with prediction endpoints
3. Integrate frontend with backend API
4. Add file processing (OCR/parsing) capabilities
5. Add blockchain logging feature
6. Deploy to production environment

---

**Last Updated**: Based on current implementation status
**Project Status**: 
- ✅ Core ML components complete (Module A & B)
- ✅ Frontend UI complete (Module C - Frontend)
- ⚠️ Backend API pending (Module C - Backend)
- ⚠️ Blockchain feature pending
**Version**: 1.0 (Core Implementation + Frontend UI)
