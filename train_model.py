#!/usr/bin/env python3
"""
Simplified training script that trains only a Gradient Boosting model
and saves it properly for predictions.
"""

import pandas as pd
import numpy as np
import joblib
import warnings
from pathlib import Path
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

# Try to import SMOTE for balancing
try:
    from imblearn.over_sampling import SMOTE
    SMOTE_AVAILABLE = True
except ImportError:
    SMOTE_AVAILABLE = False
    print("Warning: 'imblearn' library not found. Using manual oversampling fallback.")


def prepare_datasets():
    """Load and prepare the datasets."""
    print("="*80)
    print("STEP 1: Loading and Preparing Data")
    print("="*80)
    
    try:
        # Load data files - try original files first, fallback to cleaned
        try:
            df_cleaned = pd.read_csv('Blood_samples_dataset_balanced_2(f).csv')
            df_test = pd.read_csv('blood_samples_dataset_test.csv')
            print("  ✓ Using original dataset files (matching notebook)")
        except FileNotFoundError:
            print("  ⚠️  Original files not found, using cleaned.csv files")
            df_cleaned = pd.read_csv('cleaned.csv')
            df_test = pd.read_csv('cleaned_test.csv')
        
        # Merge them
        df_combined = pd.concat([df_cleaned, df_test], ignore_index=True)
        
        # Separate Features and Target
        X = df_combined.drop(columns=['Disease'])
        y = df_combined['Disease']
        
        # Handle missing values
        print(f"  Checking for missing values...")
        missing_count = X.isnull().sum().sum()
        if missing_count > 0:
            print(f"  ⚠️  Found {missing_count} missing values. Imputing with median...")
            imputer = SimpleImputer(strategy='median')
            X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns, index=X.index)
            print(f"  ✓ Missing values handled")
        else:
            print(f"  ✓ No missing values found")
        
        # Stratified Split (80% Train, 20% Test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"✓ Data loaded and merged. Total rows: {len(df_combined)}")
        print(f"✓ Training set shape: {X_train.shape}")
        print(f"✓ Test set shape: {X_test.shape}")
        print(f"✓ Number of features: {X_train.shape[1]}")
        
        return X_train, X_test, y_train, y_test

    except FileNotFoundError as e:
        print(f"❌ Error: Data file not found: {e}")
        return None, None, None, None


def preprocess_and_balance(X_train, y_train):
    """Preprocess and balance the training data."""
    print("\n" + "="*80)
    print("STEP 2: Preprocessing & Balancing")
    print("="*80)
    
    # Encode Labels (Convert Strings to Numbers)
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    
    # Print mapping for reference
    label_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    print(f"✓ Disease Label Mapping: {label_mapping}")
    print(f"✓ Number of classes: {len(le.classes_)}")

    # Handle Class Imbalance
    # NOTE: Notebook doesn't use SMOTE, but keeping it as optional
    USE_SMOTE = False  # Set to True to use SMOTE, False to match notebook behavior
    
    if USE_SMOTE and SMOTE_AVAILABLE:
        print("✓ Applying SMOTE to handle class imbalance...")
        smote = SMOTE(random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train_encoded)
        # Convert back to DataFrame to preserve column names
        X_train_resampled = pd.DataFrame(X_train_resampled, columns=X_train.columns)
    elif USE_SMOTE and not SMOTE_AVAILABLE:
        print("⚠️  SMOTE requested but not available. Using manual oversampling...")
        # Manual fallback: Duplicate minority classes
        train_data = pd.concat([X_train.reset_index(drop=True), pd.Series(y_train_encoded, name='Disease')], axis=1)
        max_size = train_data['Disease'].value_counts().max()
        
        lst = [train_data]
        for class_index, group in train_data.groupby('Disease'):
            if len(group) < max_size:
                lst.append(group.sample(max_size-len(group), replace=True, random_state=42))
        
        train_data_resampled = pd.concat(lst, ignore_index=True)
        X_train_resampled = train_data_resampled.drop('Disease', axis=1)
        y_train_resampled = train_data_resampled['Disease'].values
    else:
        print("✓ Skipping SMOTE (matching notebook behavior - no resampling)")
        X_train_resampled = X_train
        y_train_resampled = y_train_encoded

    # Handle any NaN values that might have been introduced
    missing_count = X_train_resampled.isnull().sum().sum()
    if missing_count > 0:
        print(f"  ⚠️  Found {missing_count} missing values after resampling. Imputing...")
        imputer = SimpleImputer(strategy='median')
        X_train_resampled = pd.DataFrame(
            imputer.fit_transform(X_train_resampled), 
            columns=X_train_resampled.columns
        )
        print(f"  ✓ Missing values handled")
    
    # Ensure y_train_resampled is a numpy array without NaN
    if isinstance(y_train_resampled, pd.Series):
        y_train_resampled = y_train_resampled.values
    y_train_resampled = np.array(y_train_resampled)
    if np.isnan(y_train_resampled).any():
        print(f"  ⚠️  Found NaN in y_train_resampled. Removing...")
        mask = ~np.isnan(y_train_resampled)
        X_train_resampled = X_train_resampled.iloc[mask]
        y_train_resampled = y_train_resampled[mask]
        print(f"  ✓ NaN values removed")

    print(f"✓ Original training size: {len(X_train)}")
    print(f"✓ Resampled training size: {len(X_train_resampled)}")
    
    return X_train_resampled, y_train_resampled, le


def train_and_compare_models(X_train, y_train, X_test, y_test, le):
    """Train multiple XGBoost and Gradient Boosting configurations, compare accuracies, and return the best model."""
    print("\n" + "="*80)
    print("STEP 3: Testing Multiple Model Configurations")
    print("="*80)
    
    # Transform test labels to numbers
    y_test_encoded = le.transform(y_test)
    
    models_to_test = {}
    
    # XGBoost parameter combinations to test
    xgb_configs = [
        {
            'name': 'XGBoost (Notebook Config)',
            'params': {
                'eval_metric': 'mlogloss',
                'max_depth': 5,
                'learning_rate': 0.3,
                'n_estimators': 121,
                'subsample': 0.88,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
        },
        {
            'name': 'XGBoost (Deep Trees)',
            'params': {
                'eval_metric': 'mlogloss',
                'max_depth': 7,
                'learning_rate': 0.2,
                'n_estimators': 150,
                'subsample': 0.85,
                'colsample_bytree': 0.85,
                'min_child_weight': 3,
                'random_state': 42
            }
        },
        {
            'name': 'XGBoost (Fast Learning)',
            'params': {
                'eval_metric': 'mlogloss',
                'max_depth': 6,
                'learning_rate': 0.4,
                'n_estimators': 100,
                'subsample': 0.9,
                'colsample_bytree': 0.9,
                'random_state': 42
            }
        },
        {
            'name': 'XGBoost (Conservative)',
            'params': {
                'eval_metric': 'mlogloss',
                'max_depth': 4,
                'learning_rate': 0.15,
                'n_estimators': 200,
                'subsample': 0.8,
                'colsample_bytree': 0.75,
                'min_child_weight': 5,
                'random_state': 42
            }
        },
        {
            'name': 'XGBoost (Balanced)',
            'params': {
                'eval_metric': 'mlogloss',
                'max_depth': 6,
                'learning_rate': 0.25,
                'n_estimators': 130,
                'subsample': 0.85,
                'colsample_bytree': 0.85,
                'min_child_weight': 2,
                'random_state': 42
            }
        }
    ]
    
    # Gradient Boosting parameter combinations to test
    gb_configs = [
        {
            'name': 'Gradient Boosting (Default)',
            'params': {
                'n_estimators': 200,
                'learning_rate': 0.1,
                'max_depth': 10,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'subsample': 0.8,
                'random_state': 42
            }
        },
        {
            'name': 'Gradient Boosting (Deep)',
            'params': {
                'n_estimators': 250,
                'learning_rate': 0.08,
                'max_depth': 12,
                'min_samples_split': 3,
                'min_samples_leaf': 1,
                'subsample': 0.85,
                'random_state': 42
            }
        },
        {
            'name': 'Gradient Boosting (Fast)',
            'params': {
                'n_estimators': 150,
                'learning_rate': 0.15,
                'max_depth': 8,
                'min_samples_split': 4,
                'min_samples_leaf': 2,
                'subsample': 0.9,
                'random_state': 42
            }
        },
        {
            'name': 'Gradient Boosting (Conservative)',
            'params': {
                'n_estimators': 300,
                'learning_rate': 0.05,
                'max_depth': 9,
                'min_samples_split': 6,
                'min_samples_leaf': 3,
                'subsample': 0.75,
                'random_state': 42
            }
        },
        {
            'name': 'Gradient Boosting (Balanced)',
            'params': {
                'n_estimators': 180,
                'learning_rate': 0.12,
                'max_depth': 11,
                'min_samples_split': 4,
                'min_samples_leaf': 2,
                'subsample': 0.82,
                'random_state': 42
            }
        }
    ]
    
    # Test XGBoost configurations
    print("\n" + "="*80)
    print("Testing XGBoost Configurations")
    print("="*80)
    
    for i, config in enumerate(xgb_configs, 1):
        print(f"\n[{i}/{len(xgb_configs)}] {config['name']}")
        print(f"  Params: max_depth={config['params'].get('max_depth', 'N/A')}, "
              f"lr={config['params'].get('learning_rate', 'N/A')}, "
              f"n_est={config['params'].get('n_estimators', 'N/A')}")
        
        try:
            model = XGBClassifier(**config['params'])
            model.fit(X_train, y_train)
            
            # Test predictions
            pred_test = model.predict(X_test)
            acc_test = accuracy_score(y_test_encoded, pred_test)
            f1_test = f1_score(y_test_encoded, pred_test, average='weighted', zero_division=0)
            
            # Training predictions (for overfitting check)
            pred_train = model.predict(X_train)
            acc_train = accuracy_score(y_train, pred_train)
            f1_train = f1_score(y_train, pred_train, average='weighted', zero_division=0)
            
            # Calculate overfitting gap
            overfit_gap = acc_train - acc_test
            
            print(f"  ✓ Test Accuracy: {acc_test:.4f} ({acc_test*100:.2f}%) | F1: {f1_test:.4f}")
            print(f"    Train Accuracy: {acc_train:.4f} ({acc_train*100:.2f}%) | Gap: {overfit_gap:.4f}")
            
            models_to_test[config['name']] = {
                'model': model,
                'accuracy': acc_test,
                'f1': f1_test,
                'train_accuracy': acc_train,
                'train_f1': f1_train,
                'overfit_gap': overfit_gap,
                'predictions': pred_test,
                'params': config['params']
            }
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test Gradient Boosting configurations
    print("\n" + "="*80)
    print("Testing Gradient Boosting Configurations")
    print("="*80)
    
    for i, config in enumerate(gb_configs, 1):
        print(f"\n[{i}/{len(gb_configs)}] {config['name']}")
        print(f"  Params: max_depth={config['params'].get('max_depth', 'N/A')}, "
              f"lr={config['params'].get('learning_rate', 'N/A')}, "
              f"n_est={config['params'].get('n_estimators', 'N/A')}")
        
        try:
            model = GradientBoostingClassifier(**config['params'])
            model.fit(X_train, y_train)
            
            # Test predictions
            pred_test = model.predict(X_test)
            acc_test = accuracy_score(y_test_encoded, pred_test)
            f1_test = f1_score(y_test_encoded, pred_test, average='weighted', zero_division=0)
            
            # Training predictions (for overfitting check)
            pred_train = model.predict(X_train)
            acc_train = accuracy_score(y_train, pred_train)
            f1_train = f1_score(y_train, pred_train, average='weighted', zero_division=0)
            
            # Calculate overfitting gap
            overfit_gap = acc_train - acc_test
            
            print(f"  ✓ Test Accuracy: {acc_test:.4f} ({acc_test*100:.2f}%) | F1: {f1_test:.4f}")
            print(f"    Train Accuracy: {acc_train:.4f} ({acc_train*100:.2f}%) | Gap: {overfit_gap:.4f}")
            
            models_to_test[config['name']] = {
                'model': model,
                'accuracy': acc_test,
                'f1': f1_test,
                'train_accuracy': acc_train,
                'train_f1': f1_train,
                'overfit_gap': overfit_gap,
                'predictions': pred_test,
                'params': config['params']
            }
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Compare and select best model
    print("\n" + "="*80)
    print("ALL MODELS COMPARISON RESULTS")
    print("="*80)
    
    if not models_to_test:
        print("❌ No models were successfully trained!")
        return None, None
    
    # Sort by accuracy
    sorted_models = sorted(models_to_test.items(), key=lambda x: x[1]['accuracy'], reverse=True)
    best_model_name, best_model = sorted_models[0]
    
    print(f"\n{'Rank':<6} {'Model':<35} {'Test Acc':<12} {'Train Acc':<12} {'Gap':<8} {'F1':<8}")
    print("-" * 85)
    for rank, (name, results) in enumerate(sorted_models, 1):
        marker = " ⭐ BEST" if rank == 1 else ""
        gap_str = f"{results['overfit_gap']:.4f}"
        gap_indicator = " ⚠️" if results['overfit_gap'] > 0.1 else " ✓"
        print(f"{rank:<6} {name:<35} {results['accuracy']:.4f} ({results['accuracy']*100:.1f}%){marker:<8} "
              f"{results['train_accuracy']:.4f} ({results['train_accuracy']*100:.1f}%)  {gap_str}{gap_indicator:<3} {results['f1']:.4f}")
    
    print(f"\n{'='*80}")
    print(f"✓✓✓ BEST MODEL SELECTED: {best_model_name} ✓✓✓")
    print(f"{'='*80}")
    print(f"  - Test Accuracy: {best_model['accuracy']:.4f} ({best_model['accuracy']*100:.2f}%)")
    print(f"  - Train Accuracy: {best_model['train_accuracy']:.4f} ({best_model['train_accuracy']*100:.2f}%)")
    print(f"  - Overfitting Gap: {best_model['overfit_gap']:.4f}")
    print(f"  - F1-Score: {best_model['f1']:.4f}")
    print(f"  - Parameters: {best_model['params']}")
    
    # Overfitting Analysis
    print(f"\n{'='*80}")
    print("OVERFITTING ANALYSIS")
    print(f"{'='*80}")
    
    gap = best_model['overfit_gap']
    if gap < 0.01:
        print("✅ EXCELLENT: Train and test accuracies are very close (< 1% gap)")
        print("   → Model generalizes well, no overfitting detected")
    elif gap < 0.05:
        print("✅ GOOD: Small gap between train and test (< 5% gap)")
        print("   → Model generalizes well, minimal overfitting")
    elif gap < 0.10:
        print("⚠️  MODERATE: Noticeable gap between train and test (5-10% gap)")
        print("   → Some overfitting detected, but acceptable")
        print("   → Consider: reducing model complexity, adding regularization")
    elif gap < 0.20:
        print("⚠️⚠️  HIGH: Significant gap between train and test (10-20% gap)")
        print("   → Overfitting detected!")
        print("   → Recommendations:")
        print("     - Reduce max_depth")
        print("     - Increase learning_rate (faster convergence)")
        print("     - Reduce n_estimators")
        print("     - Increase min_samples_split/min_samples_leaf")
        print("     - Reduce subsample/colsample_bytree")
    else:
        print("❌❌❌ SEVERE: Very large gap between train and test (> 20% gap)")
        print("   → Severe overfitting detected!")
        print("   → Model is memorizing training data, not learning patterns")
        print("   → Strongly recommend:")
        print("     - Significantly reduce model complexity")
        print("     - Add more regularization")
        print("     - Consider simpler model or ensemble")
    
    print(f"\n  Train Accuracy: {best_model['train_accuracy']:.4f} ({best_model['train_accuracy']*100:.2f}%)")
    print(f"  Test Accuracy:  {best_model['accuracy']:.4f} ({best_model['accuracy']*100:.2f}%)")
    print(f"  Gap:            {gap:.4f} ({gap*100:.2f} percentage points)")
    
    # Cross-validation for more robust estimate
    print(f"\n{'='*80}")
    print("CROSS-VALIDATION ANALYSIS (5-fold)")
    print(f"{'='*80}")
    print("Running cross-validation on best model for more robust performance estimate...")
    
    # Combine train and test for CV (more data = better CV estimate)
    X_all = pd.concat([X_train, X_test], ignore_index=True)
    y_all_encoded = np.concatenate([y_train, y_test_encoded])
    
    # Create a fresh model instance with same parameters
    if 'XGBoost' in best_model_name:
        cv_model = XGBClassifier(**best_model['params'])
    else:
        cv_model = GradientBoostingClassifier(**best_model['params'])
    
    # 5-fold stratified cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(cv_model, X_all, y_all_encoded, cv=skf, scoring='accuracy', n_jobs=-1)
    
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    print(f"\n  CV Accuracy: {cv_mean:.4f} ± {cv_std:.4f} ({cv_mean*100:.2f}% ± {cv_std*100:.2f}%)")
    print(f"  CV Scores per fold: {[f'{s:.4f}' for s in cv_scores]}")
    
    # Compare CV with test accuracy
    cv_test_diff = abs(cv_mean - best_model['accuracy'])
    print(f"\n  CV vs Test Difference: {cv_test_diff:.4f} ({cv_test_diff*100:.2f} percentage points)")
    
    if cv_test_diff < 0.02:
        print("  ✅ CV and Test accuracies are very close - model is stable and reliable")
    elif cv_test_diff < 0.05:
        print("  ✅ CV and Test accuracies are close - model is reasonably stable")
    else:
        print("  ⚠️  CV and Test accuracies differ - may indicate variance in model performance")
    
    # Detailed report for best model
    y_test_labels = le.inverse_transform(y_test_encoded)
    y_pred_labels = le.inverse_transform(best_model['predictions'])
    
    print(f"\n✓ Classification Report for {best_model_name}:")
    print(classification_report(y_test_labels, y_pred_labels))
    
    # Confusion matrix
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    print(f"\n✓ Confusion Matrix for {best_model_name}:")
    print(f"  Classes: {list(le.classes_)}")
    print(cm)
    
    return best_model['model'], best_model_name


def save_model(model, label_encoder, model_name, output_dir='.'):
    """Save the trained model and label encoder."""
    print("\n" + "="*80)
    print(f"STEP 4: Saving Best Model ({model_name})")
    print("="*80)
    
    output_path = Path(output_dir)
    model_path = output_path / 'disease_prediction_model.pkl'
    encoder_path = output_path / 'label_encoder.pkl'
    
    try:
        # Save model using joblib
        joblib.dump(model, model_path)
        print(f"✓ Model ({model_name}) saved to: {model_path}")
        
        # Save label encoder using joblib
        joblib.dump(label_encoder, encoder_path)
        print(f"✓ Label encoder saved to: {encoder_path}")
        
        # Verify the saved model
        print(f"\n✓ Verifying saved model...")
        loaded_model = joblib.load(model_path)
        loaded_encoder = joblib.load(encoder_path)
        
        # Check if model has predict method
        if hasattr(loaded_model, 'predict'):
            print(f"✓ Model verification successful - has 'predict' method")
            print(f"  Model type: {type(loaded_model).__name__}")
        else:
            print(f"❌ WARNING: Saved model does not have 'predict' method!")
            return False
        
        # Check encoder
        if hasattr(loaded_encoder, 'classes_'):
            print(f"✓ Encoder verification successful - has 'classes_' attribute")
            print(f"  Number of classes: {len(loaded_encoder.classes_)}")
            print(f"  Classes: {list(loaded_encoder.classes_)}")
        else:
            print(f"⚠️  WARNING: Encoder may not be in expected format")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving model: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main training pipeline."""
    print("="*80)
    print("MODEL TRAINING - Testing XGBoost & Gradient Boosting")
    print("="*80)
    
    # Step 1: Prepare data
    X_train, X_test, y_train, y_test = prepare_datasets()
    
    if X_train is None:
        print("❌ Failed to load data. Exiting.")
        return 1
    
    # Step 2: Preprocess and balance
    X_train_resampled, y_train_resampled, label_encoder = preprocess_and_balance(X_train, y_train)
    
    # Step 3: Train and compare models, select best one
    model, model_name = train_and_compare_models(X_train_resampled, y_train_resampled, X_test, y_test, label_encoder)
    
    if model is None or model_name is None:
        print("❌ Failed to train any models. Exiting.")
        return 1
    
    # Step 4: Save model
    success = save_model(model, label_encoder, model_name, output_dir='.')
    
    if success:
        print("\n" + "="*80)
        print("✓✓✓ TRAINING COMPLETE! ✓✓✓")
        print("="*80)
        print(f"\nBest Model Selected: {model_name}")
        print("\nFiles saved:")
        print("  - disease_prediction_model.pkl")
        print("  - label_encoder.pkl")
        print("\nYou can now use these files for predictions with predict.py")
        print("="*80)
        return 0
    else:
        print("\n" + "="*80)
        print("❌ TRAINING FAILED - Model not saved correctly")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit(main())

