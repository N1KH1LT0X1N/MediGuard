"""
Prediction Storage Service for saving and retrieving prediction history.
Uses JSON file storage for persistence.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import uuid

PROJECT_ROOT = Path(__file__).parent.parent.parent
STORAGE_DIR = PROJECT_ROOT / "backend" / "data"
STORAGE_FILE = STORAGE_DIR / "predictions.json"


class PredictionStorageService:
    """Service for storing and retrieving prediction history."""
    
    def __init__(self, storage_file: Optional[Path] = None):
        """
        Initialize prediction storage service.
        
        Args:
            storage_file: Path to JSON storage file (default: backend/data/predictions.json)
        """
        self.storage_file = storage_file or STORAGE_FILE
        self._ensure_storage_dir()
        self._ensure_storage_file()
    
    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _ensure_storage_file(self):
        """Ensure storage file exists with empty list."""
        if not self.storage_file.exists():
            with open(self.storage_file, 'w') as f:
                json.dump([], f)
    
    def _load_predictions(self) -> List[Dict]:
        """Load all predictions from storage file."""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_predictions(self, predictions: List[Dict]):
        """Save predictions to storage file."""
        with open(self.storage_file, 'w') as f:
            json.dump(predictions, f, indent=2)
    
    def save_prediction(
        self,
        user_id: str,
        input_features: Dict[str, float],
        prediction_result: Dict,
        source: str = "manual"  # "manual", "pdf", "csv", "image"
    ) -> str:
        """
        Save a prediction to storage.
        
        Args:
            user_id: User identifier
            input_features: Raw input features dictionary
            prediction_result: Full prediction response dictionary
            source: Source of the prediction (manual, pdf, csv, image)
            
        Returns:
            Prediction ID (UUID)
        """
        prediction_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        prediction_record = {
            "id": prediction_id,
            "user_id": user_id,
            "timestamp": timestamp,
            "source": source,
            "input_features": input_features,
            "prediction_result": prediction_result
        }
        
        predictions = self._load_predictions()
        predictions.append(prediction_record)
        self._save_predictions(predictions)
        
        return prediction_id
    
    def get_predictions(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get predictions, optionally filtered by user_id.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Optional limit on number of results
            
        Returns:
            List of prediction records
        """
        predictions = self._load_predictions()
        
        if user_id:
            predictions = [p for p in predictions if p.get("user_id") == user_id]
        
        # Sort by timestamp (newest first)
        predictions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        if limit:
            predictions = predictions[:limit]
        
        return predictions
    
    def get_recent_predictions(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get recent predictions.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Number of recent predictions to return
            
        Returns:
            List of recent prediction records
        """
        return self.get_predictions(user_id=user_id, limit=limit)
    
    def get_dashboard_stats(self, user_id: Optional[str] = None) -> Dict:
        """
        Get aggregated statistics for dashboard.
        
        Args:
            user_id: Optional user ID to filter by
            
        Returns:
            Dictionary with aggregated statistics
        """
        predictions = self.get_predictions(user_id=user_id)
        
        if not predictions:
            return {
                "total_predictions": 0,
                "disease_distribution": {},
                "risk_levels": {
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "abnormal_features_summary": {}
            }
        
        # Disease distribution
        disease_counts = {}
        for pred in predictions:
            disease = pred.get("prediction_result", {}).get("predicted_disease", "Unknown")
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        # Risk levels (based on highest probability)
        risk_levels = {"high": 0, "medium": 0, "low": 0}
        abnormal_features_count = {}
        
        for pred in predictions:
            result = pred.get("prediction_result", {})
            probabilities = result.get("probabilities", {})
            
            if probabilities:
                max_prob = max(probabilities.values())
                if max_prob >= 0.7:
                    risk_levels["high"] += 1
                elif max_prob >= 0.5:
                    risk_levels["medium"] += 1
                else:
                    risk_levels["low"] += 1
            
            # Count abnormal features
            input_features = pred.get("input_features", {})
            explainability = result.get("explainability_json", {})
            
            # Get normal ranges (simplified - would need actual ranges from medical fields)
            # For now, count features with high absolute importance as potentially abnormal
            for feature_name, importance in explainability.items():
                if abs(importance) > 0.1:  # Significant contribution
                    abnormal_features_count[feature_name] = abnormal_features_count.get(feature_name, 0) + 1
        
        return {
            "total_predictions": len(predictions),
            "disease_distribution": disease_counts,
            "risk_levels": risk_levels,
            "abnormal_features_summary": abnormal_features_count
        }


# Global instance (will be initialized in main.py)
prediction_storage: Optional[PredictionStorageService] = None

