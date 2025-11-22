"""
Pydantic schemas for request/response models.
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List


class PredictionRequest(BaseModel):
    """Request model for manual prediction."""
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names to raw clinical values (24 features)"
    )


class ExplainabilityData(BaseModel):
    """Explainability data in JSON format."""
    feature_importance: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names to importance scores"
    )


class PredictionResponse(BaseModel):
    """Response model for prediction."""
    predicted_disease: str = Field(..., description="Predicted disease name")
    probabilities: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping disease names to probability scores"
    )
    scaled_features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names to scaled values (0-1 range)"
    )
    input_features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping feature names to input raw values"
    )
    explainability_json: Dict[str, float] = Field(
        ...,
        description="Feature importance scores for visualization"
    )
    explainability_html: str = Field(
        ...,
        description="Plotly HTML string for inline embedding"
    )


class FileUploadResponse(BaseModel):
    """Response model for file upload (extracted features)."""
    features: Dict[str, Optional[float]] = Field(
        ...,
        description="Dictionary mapping feature names to extracted values (None if not found)"
    )
    extraction_success: bool = Field(
        ...,
        description="Whether feature extraction was successful"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message about extraction process"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

