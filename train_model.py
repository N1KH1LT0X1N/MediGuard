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

from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
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
        # Load data files
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
    if SMOTE_AVAILABLE:
        print("✓ Applying SMOTE to handle class imbalance...")
        smote = SMOTE(random_state=42)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train_encoded)
        # Convert back to DataFrame to preserve column names
        X_train_resampled = pd.DataFrame(X_train_resampled, columns=X_train.columns)
    else:
        print("⚠️  Using manual oversampling fallback...")
        # Manual fallback: Duplicate minority classes
        train_data = pd.concat([X_train.reset_index(drop=True), pd.Series(y_train_encoded, name='Disease')], axis=1)
        max_size = train_data['Disease'].value_counts().max()
        
        lst = [train_data]
        for class_index, group in train_data.groupby('Disease'):
            if len(group) < max_size:
                lst.append(group.sample(max_size-len(group), replace=True, random_state=42))
        
        train_data_resampled = pd.concat(lst, ignore_index=True)
        X_train_resampled = train_data_resampled.drop('Disease', axis=1)
        y_train_resampled = train_data_resampled['Disease'].values  # Convert to numpy array

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


def train_gradient_boosting(X_train, y_train, X_test, y_test, le):
    """Train a Gradient Boosting model with default parameters."""
    print("\n" + "="*80)
    print("STEP 3: Training Gradient Boosting Model")
    print("="*80)
    
    # Transform test labels to numbers
    y_test_encoded = le.transform(y_test)
    
    # Create Gradient Boosting model with default parameters
    print("Training Gradient Boosting Classifier...")
    print("  Parameters: n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42")
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=3,
        min_samples_split=2,
        min_samples_leaf=1,
        subsample=1.0,
        random_state=42
    )
    
    # Train the model
    model.fit(X_train, y_train)
    print("✓ Model trained successfully")
    
    # Make predictions
    y_pred_encoded = model.predict(X_test)
    y_test_labels = le.inverse_transform(y_test_encoded)
    y_pred_labels = le.inverse_transform(y_pred_encoded)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test_encoded, y_pred_encoded)
    f1 = f1_score(y_test_encoded, y_pred_encoded, average='weighted', zero_division=0)
    
    print(f"\n✓ Model Performance:")
    print(f"  - Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  - F1-Score: {f1:.4f}")
    
    # Classification report
    print(f"\n✓ Classification Report:")
    print(classification_report(y_test_labels, y_pred_labels))
    
    # Confusion matrix
    cm = confusion_matrix(y_test_labels, y_pred_labels, labels=le.classes_)
    print(f"\n✓ Confusion Matrix:")
    print(f"  Classes: {list(le.classes_)}")
    print(cm)
    
    return model


def save_model(model, label_encoder, output_dir='.'):
    """Save the trained model and label encoder."""
    print("\n" + "="*80)
    print("STEP 4: Saving Model")
    print("="*80)
    
    output_path = Path(output_dir)
    model_path = output_path / 'disease_prediction_model.pkl'
    encoder_path = output_path / 'label_encoder.pkl'
    
    try:
        # Save model using joblib
        joblib.dump(model, model_path)
        print(f"✓ Model saved to: {model_path}")
        
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
    print("GRADIENT BOOSTING MODEL TRAINING")
    print("="*80)
    
    # Step 1: Prepare data
    X_train, X_test, y_train, y_test = prepare_datasets()
    
    if X_train is None:
        print("❌ Failed to load data. Exiting.")
        return 1
    
    # Step 2: Preprocess and balance
    X_train_resampled, y_train_resampled, label_encoder = preprocess_and_balance(X_train, y_train)
    
    # Step 3: Train model
    model = train_gradient_boosting(X_train_resampled, y_train_resampled, X_test, y_test, label_encoder)
    
    # Step 4: Save model
    success = save_model(model, label_encoder, output_dir='.')
    
    if success:
        print("\n" + "="*80)
        print("✓✓✓ TRAINING COMPLETE! ✓✓✓")
        print("="*80)
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

