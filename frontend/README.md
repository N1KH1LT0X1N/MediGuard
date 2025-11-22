# MediGuard AI: Intelligent Triage Assistant

An intelligent triage assistant that analyzes 24 pre-scaled blood test parameters to predict the likelihood of multiple diseases (Heart Disease, Diabetes, Anemia, Thalassemia, Thrombocytopenia, and Healthy status). The system serves as a crucial second opinion for triage nurses, routing patients efficiently and safely.

## 🎯 Project Overview

MediGuard AI is a machine learning system that predicts diseases from clinical blood test parameters. The system consists of three main modules:

- **Module A (Model)**: ✅ **Complete** - Robust Multi-Class Classification model trained with XGBoost (saved model) / Gradient Boosting (train_model.py)
- **Module B (Scaling Bridge)**: ✅ **Complete** - Complete interface layer converting raw clinical inputs to scaled format
- **Module C (Dashboard)**: ⚠️ **Pending** - Planned: React + Vite + shadcn + Acernity UI frontend with FastAPI backend

## ✨ Key Features

- **Multi-Disease Classification**: Predicts 6 different disease classes from 24 clinical features
- **Scaling Bridge**: Converts raw clinical values (various units and scales) to normalized [0, 1] range
- **High Accuracy**: 95.5% accuracy on test set with high recall for critical diseases
- **Production-Ready**: Complete CLI prediction tool with multiple input methods
- **Comprehensive Documentation**: Detailed documentation for all components

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Components](#components)
6. [Performance Metrics](#performance-metrics)
7. [Documentation](#documentation)
8. [Future Work](#future-work)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy scikit-learn joblib imbalanced-learn
```

### 2. Train the Model

```bash
python train_model.py
```

This will:
- Load and merge training data (`cleaned.csv` + `cleaned_test.csv`)
- Train a Gradient Boosting classifier
- Save the model as `disease_prediction_model.pkl`
- Save the label encoder as `label_encoder.pkl`

### 3. Make Predictions

```bash
# Using raw clinical values (24 features in order)
python predict.py 120 180 14.5 250000 7000 4.5 42 88 29 33 8 22.5 120 80 150 5.5 100 50 25 30 72 0.9 0.01 2.5

# Using CSV string
python predict.py --csv "120,180,14.5,250000,7000,4.5,42,88,29,33,8,22.5,120,80,150,5.5,100,50,25,30,72,0.9,0.01,2.5"

# Using CSV file
python predict.py --file cleaned_test.csv
```

## 📦 Installation

### Requirements

- Python 3.7+ (recommended: Python 3.8+)
- Required packages:
  - `pandas`: Data manipulation
  - `numpy`: Numerical operations
  - `scikit-learn`: Machine learning
  - `joblib`: Model serialization
  - `xgboost`: XGBoost classifier (required for saved model)
  - `imbalanced-learn`: Class balancing (optional but recommended)

### Install Dependencies

```bash
# Minimal installation
pip install pandas numpy scikit-learn joblib xgboost

# Full installation (recommended)
pip install pandas numpy scikit-learn joblib xgboost imbalanced-learn
```

## 💻 Usage

### Training the Model

```bash
python train_model.py
```

**Output:**
- `disease_prediction_model.pkl`: Trained model
- `label_encoder.pkl`: Label encoder for disease names

### Making Predictions

The `predict.py` script supports multiple input methods:

#### 1. Positional Arguments

```bash
python predict.py <value1> <value2> ... <value24>
```

#### 2. CSV String

```bash
python predict.py --csv "value1,value2,...,value24"
```

#### 3. File Input

```bash
python predict.py --file input.csv
```

#### Options

- `--verbose` or `-v`: Show detailed scaling information
- `--json`: Output result as JSON
- `--model PATH`: Specify custom model path (default: `disease_prediction_model.pkl`)
- `--encoder PATH`: Specify custom encoder path (default: `label_encoder.pkl`)
- `--already-scaled`: Skip scaling for pre-scaled inputs (0-1 range)

### Feature Order (24 Features)

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

## 📁 Project Structure

```
ggw_redact/
│
├── train_model.py                 # Model training pipeline
├── predict.py                     # CLI prediction tool
│
├── disease_prediction_model.pkl   # Trained model (generated)
├── label_encoder.pkl              # Label encoder (generated)
│
├── cleaned.csv                    # Training data (65 samples)
├── cleaned_test.csv               # Test data (486 samples)
│
├── MODEL_TRAINING_LOGIC.md        # Comprehensive training documentation
├── SCALING_LOGIC_EXPLAINED.md     # Detailed scaling documentation
├── PROJECT_CONTEXT.md             # Complete project context
├── README.md                      # This file
│
└── ml/
    └── scaling_layer/
        ├── scaling_bridge.py              # Base scaling bridge
        ├── enhanced_scaling_bridge.py     # Enhanced version with inferred ranges
        ├── inferred_ranges.py            # Python ranges module
        ├── inferred_ranges.json          # JSON ranges file
        └── README.md                      # Scaling bridge documentation
```

## 🔧 Components

### 1. Model Training

**Primary Script: `train_model.py`**

Complete training pipeline that:
- Loads and merges datasets
- Handles missing values (median imputation)
- Performs stratified train-test split (80/20)
- Encodes disease labels
- Handles class imbalance (SMOTE or manual oversampling)
- Trains Gradient Boosting Classifier
- Evaluates model performance
- Saves model and encoder

**Note:** The currently saved model (`disease_prediction_model.pkl`) is an XGBClassifier trained using the notebooks in `ml/training&testing/`. Additional training notebooks are available for experimentation with different ensemble methods.

**Model Details:**
- Algorithm: XGBoost Classifier (currently saved model) / Gradient Boosting Classifier (train_model.py)
- Note: The saved model (`disease_prediction_model.pkl`) is an XGBClassifier trained in the notebooks. The `train_model.py` script uses GradientBoostingClassifier.
- Hyperparameters (XGBoost):
  - `n_estimators=300`
  - `learning_rate=0.05`
  - `max_depth=5`
  - `random_state=42`
- Hyperparameters (GradientBoosting - train_model.py):
  - `n_estimators=100`
  - `learning_rate=0.1`
  - `max_depth=3`
  - `random_state=42`

### 2. Scaling Bridge (`ml/scaling_layer/`)

Critical interface layer that converts raw clinical values to [0, 1] range.

**Components:**
- `scaling_bridge.py`: Base implementation with clinical reference ranges
- `enhanced_scaling_bridge.py`: Enhanced version with inferred ranges from training data
- `inferred_ranges.json`: Data-driven ranges (24 features)
- `inferred_ranges.py`: Python module version

**Features:**
- Min-Max normalization
- Inferred ranges from training data
- 10% range extension for safety margin
- Input validation
- Edge case handling

### 3. Prediction CLI (`predict.py`)

Production-ready command-line tool for making predictions.

**Features:**
- Multiple input methods (positional args, CSV string, file)
- Automatic scaling detection
- Model loading with compatibility handling
- Prediction with probabilities
- JSON output support
- Verbose mode for debugging

## 📊 Performance Metrics

### Overall Performance

- **Accuracy**: 95.50%
- **F1-Score (Weighted)**: 0.95
- **Macro F1**: 0.87

### Per-Class Performance

| Disease      | Precision | Recall | F1-Score |
|--------------|-----------|--------|----------|
| Anemia       | 0.95      | 0.95   | 0.95     |
| Diabetes     | 0.98      | 0.98   | 0.98     |
| Healthy      | 0.67      | 0.50   | 0.57     |
| Heart Di     | 0.89      | 1.00   | 0.94     |
| Thalasse     | 1.00      | 1.00   | 1.00     |
| Thromboc     | 0.75      | 0.75   | 0.75     |

**Key Observations:**
- High recall for critical diseases (Heart Di: 100%)
- Common diseases have excellent performance
- Model prioritizes recall (minimizing False Negatives)

## 📚 Documentation

Comprehensive documentation is available:

- **`MODEL_TRAINING_LOGIC.md`**: Detailed explanation of the training pipeline
- **`SCALING_LOGIC_EXPLAINED.md`**: Complete guide to the scaling bridge system
- **`PROJECT_CONTEXT.md`**: Full project context and architecture
- **`ml/scaling_layer/README.md`**: Scaling bridge usage guide

## 🔮 Future Work

### Pending Components

1. **Dashboard (Module C)**
   - Status: Not implemented
   - Tech Stack: React + Vite + shadcn/ui + Acernity UI frontend with FastAPI backend
   - Features: Input form, prediction display, risk indicators, explainability

2. **Blockchain Feature**
   - Status: Not implemented
   - Features: Immutable logging of predictions, audit trail

### Potential Enhancements

- Hyperparameter tuning (GridSearchCV)
- Feature engineering
- Ensemble methods
- SHAP values for explainability
- Data drift detection
- Batch prediction support

## 🐛 Troubleshooting

### Common Issues

#### 1. Model Loading Errors

**Error**: `ValueError: BitGenerator` or `MT19937` error

**Solution**: Numpy version incompatibility. Try:
```bash
pip install --upgrade numpy
# Or re-save the model
python train_model.py
```

#### 2. Missing Data Files

**Error**: `FileNotFoundError: cleaned.csv not found`

**Solution**: Ensure data files are in the project root directory.

#### 3. Class Imbalance Warning

**Warning**: `Using manual oversampling fallback`

**Solution**: Install imbalanced-learn:
```bash
pip install imbalanced-learn
```

#### 4. Scaling Bridge Import Error

**Error**: `Could not import EnhancedScalingBridge`

**Solution**: Ensure `ml/scaling_layer/` directory exists with all files.

## 📝 License

Part of the GGW Redact MediGuard project.

## 👥 Contributing

This is a research/development project. For questions or contributions, please refer to the project documentation.

---

**Last Updated**: Based on current implementation status  
**Project Status**: Core components complete (Module A & B), Dashboard pending (Module C)  
**Version**: 1.0 (Core Implementation)
