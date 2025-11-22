#!/usr/bin/env python3
"""
CLI script for disease prediction using raw clinical feature values.

This script:
1. Takes 24 raw clinical feature values as input
2. Scales them using the scaling bridge
3. Makes predictions using the trained model
4. Outputs the predicted disease

Usage:
    python predict.py <value1> <value2> ... <value24>
    python predict.py --csv "value1,value2,...,value24"
    python predict.py --file input.csv
"""

import sys
import argparse
import pickle
import numpy as np
from pathlib import Path
import json

try:
    import joblib
except ImportError:
    print("Error: joblib is required. Install it with: pip install joblib")
    sys.exit(1)

# Add the scaling_layer directory to the path
sys.path.insert(0, str(Path(__file__).parent / "ml" / "scaling_layer"))

try:
    from enhanced_scaling_bridge import EnhancedScalingBridge, create_bridge_from_inferred_ranges
except ImportError:
    print("Error: Could not import EnhancedScalingBridge. Make sure ml/scaling_layer exists.")
    sys.exit(1)

# Add explainability import
sys.path.insert(0, str(Path(__file__).parent / "ml"))
try:
    from explainability import MediGuardExplainer
    HAS_EXPLAINABILITY = True
except ImportError:
    HAS_EXPLAINABILITY = False


# Wrapper classes for ensemble models
class WeightedEnsemble:
    """Wrapper for weighted average ensemble models."""
    def __init__(self, models, weights):
        self.models = models
        self.weights = weights
    
    def predict(self, X):
        predictions = np.array([model.predict(X) for model in self.models])
        # Weighted voting
        weighted_votes = np.zeros((X.shape[0], len(self.weights)))
        for i, (model, weight) in enumerate(zip(self.models, self.weights)):
            pred = model.predict(X)
            for j, p in enumerate(pred):
                weighted_votes[j, p] += weight
        return np.argmax(weighted_votes, axis=1)
    
    def predict_proba(self, X):
        probas = np.array([model.predict_proba(X) for model in self.models])
        # Weighted average of probabilities
        weighted_proba = np.average(probas, axis=0, weights=self.weights)
        return weighted_proba


class BlendingEnsemble:
    """Wrapper for blending ensemble models."""
    def __init__(self, base_learners, meta_learner):
        self.base_learners = base_learners
        self.meta_learner = meta_learner
    
    def predict(self, X):
        # Get base learner predictions
        base_predictions = np.column_stack([model.predict(X) for model in self.base_learners.values()])
        # Meta learner makes final prediction
        return self.meta_learner.predict(base_predictions)
    
    def predict_proba(self, X):
        # Get base learner probabilities
        base_probas = np.hstack([model.predict_proba(X) for model in self.base_learners.values()])
        # Meta learner makes final prediction
        return self.meta_learner.predict_proba(base_probas)


# Feature names in order (24 features, excluding Disease)
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


def load_model(model_path: Path, encoder_path: Path, verbose=False):
    """Load the trained model and label encoder."""
    try:
        # Try joblib first (models were saved with joblib)
        # Handle numpy version compatibility issues
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                # Try with joblib
                model = joblib.load(model_path)
                label_encoder = joblib.load(encoder_path)
            except (ValueError, TypeError, AttributeError) as joblib_error:
                error_str = str(joblib_error)
                # If it's a numpy compatibility issue
                if 'BitGenerator' in error_str or 'MT19937' in error_str:
                    print("\n" + "="*80)
                    print("⚠️  NUMPY VERSION COMPATIBILITY ISSUE DETECTED")
                    print("="*80)
                    print("The model was saved with a different numpy version.")
                    print("\nTo fix this, try one of the following:")
                    print("  1. Update numpy: pip install --upgrade numpy")
                    print("  2. Or re-save the model with the current numpy version")
                    print("\nAttempting to work around the issue...")
                    print("="*80 + "\n")
                    
                    # Try to work around by using pickle with different encodings
                    try:
                        # Try different pickle loading methods
                        with open(model_path, 'rb') as f:
                            try:
                                model = pickle.load(f)
                            except:
                                f.seek(0)
                                model = pickle.load(f, encoding='latin1')
                        with open(encoder_path, 'rb') as f:
                            try:
                                label_encoder = pickle.load(f)
                            except:
                                f.seek(0)
                                label_encoder = pickle.load(f, encoding='latin1')
                        print("✓ Successfully loaded model using pickle workaround\n")
                    except Exception as pickle_error:
                        raise Exception(
                            f"\n❌ Could not load model due to numpy version incompatibility.\n\n"
                            f"Error details: {error_str}\n\n"
                            f"SOLUTION OPTIONS:\n"
                            f"  1. Downgrade numpy to match training version:\n"
                            f"     pip install numpy==1.24.0  # or the version used during training\n"
                            f"  2. Re-save the model with current numpy version\n"
                            f"  3. Use a virtual environment with the correct numpy version\n\n"
                            f"Current numpy version: {np.__version__}\n"
                        )
                else:
                    # Other joblib error, try pickle as fallback
                    try:
                        with open(model_path, 'rb') as f:
                            model = pickle.load(f)
                        with open(encoder_path, 'rb') as f:
                            label_encoder = pickle.load(f)
                    except Exception as pickle_error:
                        raise Exception(f"Failed to load with joblib: {joblib_error}\nFailed to load with pickle: {pickle_error}")
        
        # Validate and wrap model if needed
        if not hasattr(model, 'predict'):
            # Check if model is a dict (ensemble models)
            if isinstance(model, dict):
                if 'models' in model and 'weights' in model:
                    # Weighted average ensemble
                    model = WeightedEnsemble(model['models'], model['weights'])
                elif 'base_learners' in model and 'meta_learner' in model:
                    # Blending ensemble
                    model = BlendingEnsemble(model['base_learners'], model['meta_learner'])
                else:
                    raise ValueError(f"Unknown model dict structure. Keys: {list(model.keys())}")
            else:
                # Check if it's actually feature names (common mistake)
                if isinstance(model, np.ndarray) and len(model) == 24:
                    raise ValueError(
                        f"\n❌ The model file appears to contain feature names, not a model.\n"
                        f"   This usually means the model was saved incorrectly.\n"
                        f"   Please check if there's a proper model file in ml/training&testing/\n"
                    )
                raise ValueError(
                    f"Loaded object is not a model (type: {type(model)}).\n"
                    f"Expected a model with 'predict' method or a dict with ensemble structure."
                )
        
        return model, label_encoder
    except FileNotFoundError as e:
        print(f"Error: Model file not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading model: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def parse_values_from_args(args):
    """Parse feature values from command line arguments."""
    if args.csv:
        # Parse from CSV string
        values = [float(x.strip()) for x in args.csv.split(',')]
    elif args.file:
        # Parse from file (first line, CSV format)
        with open(args.file, 'r') as f:
            line = f.readline().strip()
            values = [float(x.strip()) for x in line.split(',')]
    else:
        # Parse from positional arguments
        values = [float(x) for x in args.values]
    
    if len(values) != 24:
        print(f"Error: Expected 24 feature values, got {len(values)}")
        print("\nRequired features (in order):")
        for i, name in enumerate(FEATURE_NAMES, 1):
            print(f"  {i:2d}. {name}")
        sys.exit(1)
    
    return values


def create_feature_dict(values):
    """Create a dictionary mapping feature names to values."""
    if len(values) != len(FEATURE_NAMES):
        raise ValueError(f"Expected {len(FEATURE_NAMES)} values, got {len(values)}")
    
    return dict(zip(FEATURE_NAMES, values))


def predict(model, label_encoder, bridge, feature_dict, already_scaled=False, verbose=False):
    """Make a prediction using the model."""
    if already_scaled:
        # Inputs are already scaled (0-1 range), use directly
        if verbose:
            print("\n" + "="*80)
            print("Using Pre-scaled Features (0-1 range)")
            print("="*80)
        
        # Convert feature dict to array in correct order
        scaled_array = np.array([feature_dict[name] for name in FEATURE_NAMES])
        
        if verbose:
            print("\nPre-scaled values (using directly):")
            for i, name in enumerate(FEATURE_NAMES):
                print(f"  {name:40s} {scaled_array[i]:.6f}")
    else:
        # Scale features from raw clinical values
        if verbose:
            print("\n" + "="*80)
            print("Scaling Features (Raw → 0-1)")
            print("="*80)
        
        scaled_array = bridge.scale_to_array(feature_dict, feature_order=FEATURE_NAMES)
        
        if verbose:
            print("\nScaled values:")
            for i, (name, raw_val) in enumerate(feature_dict.items()):
                print(f"  {name:40s} {raw_val:10.4f} → {scaled_array[i]:.6f}")
    
    # Reshape for model input (1 sample, 24 features)
    scaled_array = scaled_array.reshape(1, -1)
    
    # Make prediction
    prediction = model.predict(scaled_array)
    prediction_proba = model.predict_proba(scaled_array)[0] if hasattr(model, 'predict_proba') else None
    
    # Decode prediction
    disease = label_encoder.inverse_transform(prediction)[0]
    
    return disease, prediction_proba, scaled_array


def main():
    parser = argparse.ArgumentParser(
        description='Predict disease from 24 raw clinical feature values',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Using raw clinical values (positional arguments):
  python predict.py 120 180 14.5 250000 7000 4.5 42 88 29 33 8 22.5 120 80 150 5.5 100 50 25 30 72 0.9 0.01 2.5

  # Using raw clinical values (CSV string):
  python predict.py --csv "120,180,14.5,250000,7000,4.5,42,88,29,33,8,22.5,120,80,150,5.5,100,50,25,30,72,0.9,0.01,2.5"

  # Using already-scaled values (0-1 range) from test CSV:
  # Note: Auto-detection will skip scaling if all values are 0-1
  python predict.py --file cleaned_test.csv
  # Or explicitly:
  python predict.py --file cleaned_test.csv --already-scaled

Required features (in order):
{chr(10).join(f"  {i:2d}. {name}" for i, name in enumerate(FEATURE_NAMES, 1))}
        """
    )
    
    # Input methods
    parser.add_argument(
        'values',
        nargs='*',
        type=float,
        help='24 feature values as positional arguments (use --csv or --file for other input methods)'
    )
    parser.add_argument(
        '--csv',
        type=str,
        help='Comma-separated values string (24 values). Mutually exclusive with positional args and --file'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Path to CSV file (first line should contain 24 comma-separated values). Mutually exclusive with positional args and --csv'
    )
    
    # Optional arguments
    parser.add_argument(
        '--model',
        type=str,
        default='disease_prediction_model.pkl',
        help='Path to model file (default: disease_prediction_model.pkl)'
    )
    parser.add_argument(
        '--encoder',
        type=str,
        default='label_encoder.pkl',
        help='Path to label encoder file (default: label_encoder.pkl)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including scaled values'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output result as JSON'
    )
    parser.add_argument(
        '--scaling-layer',
        type=str,
        default='ml/scaling_layer',
        help='Path to scaling layer directory (default: ml/scaling_layer)'
    )
    parser.add_argument(
        '--already-scaled',
        action='store_true',
        help='Input values are already scaled (0-1 range). Skip scaling step.'
    )
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = Path(__file__).parent
    
    # Resolve paths
    model_path = script_dir / args.model
    encoder_path = script_dir / args.encoder
    
    # Load model and encoder
    if not args.json:
        print("Loading model and label encoder...")
    model, label_encoder = load_model(model_path, encoder_path, verbose=args.verbose)
    
    # Create scaling bridge (only needed if not using pre-scaled inputs)
    bridge = None
    if not args.already_scaled:
        scaling_layer_path = script_dir / args.scaling_layer
        inferred_json = scaling_layer_path / 'inferred_ranges.json'
        if inferred_json.exists():
            bridge = create_bridge_from_inferred_ranges(str(inferred_json))
        else:
            # Fall back to using inferred_ranges.py if available
            bridge = create_bridge_from_inferred_ranges()
    
    if not args.json:
        if args.already_scaled:
            print("✓ Model loaded successfully (using pre-scaled inputs)\n")
        else:
            print("✓ Model and scaling bridge loaded successfully\n")
    
    # Initialize explainability module
    explainer = None
    if HAS_EXPLAINABILITY:
        try:
            training_data_path = script_dir / "cleaned_test.csv"
            explainer = MediGuardExplainer(
                model_path=model_path,
                encoder_path=encoder_path,
                training_data_path=training_data_path,
                scaling_bridge=bridge if bridge else None
            )
            if args.verbose and not args.json:
                print("✓ Explainability module initialized\n")
        except Exception as e:
            if args.verbose and not args.json:
                print(f"Warning: Could not initialize explainability: {e}\n")
            explainer = None
    
    # Validate that exactly one input method is provided
    input_methods = [bool(args.values), bool(args.csv), bool(args.file)]
    if sum(input_methods) != 1:
        parser.error("Exactly one input method must be specified: positional arguments, --csv, or --file")
    
    # Parse input values
    try:
        values = parse_values_from_args(args)
    except ValueError as e:
        print(f"Error parsing values: {e}")
        sys.exit(1)
    
    # Auto-detect if values are already scaled (all between 0-1)
    # If all values are in 0-1 range, they're almost certainly already scaled
    # since raw clinical values have very different scales (e.g., Glucose ~70-200, Platelets ~150k-450k)
    if not args.already_scaled:
        all_in_range = all(0.0 <= v <= 1.0 for v in values)
        if all_in_range and len(values) == 24:
            # Auto-detect: if all values are 0-1, they're almost certainly pre-scaled
            # Raw clinical values would have much larger ranges
            print("⚠️  Auto-detected: All input values are between 0-1.")
            print("   These appear to be pre-scaled values. Automatically skipping scaling step.\n")
            args.already_scaled = True
    
    # Create feature dictionary
    try:
        feature_dict = create_feature_dict(values)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Validate inputs (optional but helpful) - only for raw inputs
    if args.verbose and not args.already_scaled and bridge:
        validation = bridge.validate_input(feature_dict)
        if validation['warnings']:
            print("\n⚠️  Input Validation Warnings:")
            for warning in validation['warnings']:
                print(f"  - {warning}")
    
    # Make prediction
    try:
        disease, prediction_proba, scaled_array = predict(
            model, label_encoder, bridge, feature_dict, 
            already_scaled=args.already_scaled, 
            verbose=args.verbose
        )
    except Exception as e:
        print(f"Error during prediction: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Output results
    if args.json:
        result = {
            'predicted_disease': disease,
            'input_features': feature_dict,
            'scaled_features': {name: float(val) for name, val in zip(FEATURE_NAMES, scaled_array[0])}
        }
        if prediction_proba is not None:
            classes = label_encoder.classes_
            result['probabilities'] = {
                cls: float(prob) for cls, prob in zip(classes, prediction_proba)
            }
        print(json.dumps(result, indent=2))
        
        # Generate explanation graph (even in JSON mode per user preference)
        if explainer is not None and not args.already_scaled:
            try:
                html_path = explainer.generate_interactive_plot(
                    patient_data=feature_dict,
                    output_dir=str(script_dir)
                )
                # In JSON mode, print to stderr or add to result
                import sys
                print(f"\n✨ Explanation graph saved to {html_path}", file=sys.stderr)
                print("   Opening in browser...", file=sys.stderr)
                
                # Open in default browser
                import webbrowser
                webbrowser.open(f"file://{html_path}")
            except Exception as e:
                # Silent fail in JSON mode unless verbose
                if args.verbose:
                    import sys
                    print(f"Warning: Could not generate explanation: {e}", file=sys.stderr)
    else:
        print("\n" + "="*80)
        print("PREDICTION RESULT")
        print("="*80)
        print(f"\nPredicted Disease: {disease}\n")
        
        if prediction_proba is not None:
            print("Prediction Probabilities:")
            classes = label_encoder.classes_
            sorted_probs = sorted(zip(classes, prediction_proba), key=lambda x: x[1], reverse=True)
            for cls, prob in sorted_probs:
                print(f"  {cls:30s} {prob*100:6.2f}%")
            print()
        
        # Generate explanation graph
        if explainer is not None and not args.already_scaled:
            try:
                html_path = explainer.generate_interactive_plot(
                    patient_data=feature_dict,
                    output_dir=str(script_dir)
                )
                print(f"\n✨ Explanation graph saved to {html_path}")
                print("   Opening in browser...\n")
                
                # Open in default browser
                import webbrowser
                webbrowser.open(f"file://{html_path}")
            except Exception as e:
                if args.verbose:
                    print(f"Warning: Could not generate explanation: {e}\n")
                else:
                    print("(Explanation generation skipped)\n")
        elif explainer is not None and args.already_scaled:
            if args.verbose:
                print("(Explanation skipped: requires raw clinical values)\n")
        
        print("="*80)


if __name__ == '__main__':
    main()

