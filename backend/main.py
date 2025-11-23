"""
FastAPI main application for MediGuard AI backend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import sys
from typing import Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    FileUploadResponse,
    ErrorResponse,
    SavePredictionRequest,
    PredictionHistory,
    DashboardStats
)
from backend.services.prediction_service import PredictionService
from backend.services.explainability_service import ExplainabilityService
from backend.services.ocr_service import ocr_service
from backend.services.file_parser import file_parser_service
from backend.services.prediction_storage_service import PredictionStorageService

# Initialize FastAPI app
app = FastAPI(
    title="MediGuard AI API",
    description="Backend API for disease prediction from medical data",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services (initialized at startup)
prediction_service: PredictionService = None
explainability_service: ExplainabilityService = None
prediction_storage: PredictionStorageService = None


@app.on_event("startup")
async def startup_event():
    """Initialize services at startup."""
    global prediction_service, explainability_service, prediction_storage
    
    try:
        # Initialize prediction service
        model_path = PROJECT_ROOT / "disease_prediction_model.pkl"
        encoder_path = PROJECT_ROOT / "label_encoder.pkl"
        prediction_service = PredictionService(model_path, encoder_path)
        print("✓ Prediction service initialized")
        
        # Initialize explainability service
        explainability_service = ExplainabilityService()
        print("✓ Explainability service initialized")
        
        # Initialize prediction storage service
        prediction_storage = PredictionStorageService()
        print("✓ Prediction storage service initialized")
    except Exception as e:
        print(f"⚠️  Error initializing services: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MediGuard AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/predict",
            "upload_image": "/api/upload/image",
            "upload_pdf": "/api/upload/pdf",
            "upload_csv": "/api/upload/csv",
            "save_prediction": "/api/predictions/save",
            "get_predictions": "/api/predictions",
            "get_stats": "/api/predictions/stats"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "prediction_service": prediction_service is not None,
        "explainability_service": explainability_service is not None
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_disease(request: PredictionRequest):
    """
    Predict disease from manual feature entry.
    
    Args:
        request: PredictionRequest with 24 feature values
        
    Returns:
        PredictionResponse with prediction, probabilities, and explainability
    """
    if not prediction_service:
        raise HTTPException(status_code=503, detail="Prediction service not initialized")
    
    try:
        # Make prediction
        disease, probabilities, scaled_array = prediction_service.predict(request.features)
        
        # Get scaled features as dict
        from backend.services.prediction_service import FEATURE_NAMES
        scaled_features = {
            name: float(val) for name, val in zip(FEATURE_NAMES, scaled_array)
        }
        
        # Generate explainability
        explainability_json = {}
        explainability_html = ""
        if explainability_service:
            explainability_json, explainability_html = explainability_service.generate_explanation(
                request.features
            )
        
        return PredictionResponse(
            predicted_disease=disease,
            probabilities=probabilities,
            scaled_features=scaled_features,
            input_features=request.features,
            explainability_json=explainability_json,
            explainability_html=explainability_html
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/api/upload/image", response_model=FileUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload image file and extract features using OCR.
    
    Args:
        file: Image file (PNG, JPG, JPEG)
        
    Returns:
        FileUploadResponse with extracted features
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image (PNG, JPG, JPEG)")
    
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Extract features using OCR
        features = ocr_service.extract_features_from_image(file_bytes)
        
        # Check extraction success
        extracted_count = sum(1 for v in features.values() if v is not None)
        success = extracted_count > 0
        
        message = f"Extracted {extracted_count} out of 24 features" if success else "No features extracted"
        
        return FileUploadResponse(
            features=features,
            extraction_success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")


@app.post("/api/upload/pdf", response_model=FileUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload PDF file and extract features using OCR.
    
    Args:
        file: PDF file
        
    Returns:
        FileUploadResponse with extracted features
    """
    # Validate file type
    if not file.content_type or file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Extract features using OCR
        features = ocr_service.extract_features_from_pdf(file_bytes)
        
        # Check extraction success
        extracted_count = sum(1 for v in features.values() if v is not None)
        success = extracted_count > 0
        
        message = f"Extracted {extracted_count} out of 24 features" if success else "No features extracted"
        
        return FileUploadResponse(
            features=features,
            extraction_success=success,
            message=message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF OCR error: {str(e)}")


@app.post("/api/upload/csv", response_model=FileUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload CSV or Excel file and extract features.
    
    Args:
        file: CSV or Excel file
        
    Returns:
        FileUploadResponse with extracted features
    """
    try:
        # Read file bytes
        file_bytes = await file.read()
        
        # Determine file type
        filename = file.filename.lower() if file.filename else ""
        
        if filename.endswith('.csv'):
            # Parse CSV
            features = file_parser_service.parse_csv(file_bytes)
        elif filename.endswith(('.xlsx', '.xls')):
            # Parse Excel
            features = file_parser_service.parse_excel(file_bytes)
        else:
            raise HTTPException(
                status_code=400,
                detail="File must be CSV or Excel (.csv, .xlsx, .xls)"
            )
        
        # Check extraction success
        extracted_count = sum(1 for v in features.values() if v is not None)
        success = extracted_count > 0
        
        message = f"Extracted {extracted_count} out of 24 features" if success else "No features extracted"
        
        return FileUploadResponse(
            features=features,
            extraction_success=success,
            message=message
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File parsing error: {str(e)}")


@app.post("/api/predictions/save")
async def save_prediction(request: SavePredictionRequest):
    """
    Save a prediction to storage.
    
    Args:
        request: SavePredictionRequest with user_id, input_features, prediction_result, and source
        
    Returns:
        Dictionary with prediction_id
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        prediction_id = prediction_storage.save_prediction(
            user_id=request.user_id,
            input_features=request.input_features,
            prediction_result=request.prediction_result,
            source=request.source
        )
        return {"prediction_id": prediction_id, "message": "Prediction saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving prediction: {str(e)}")


@app.get("/api/predictions", response_model=List[PredictionHistory])
async def get_predictions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Get predictions, optionally filtered by user_id.
    
    Args:
        user_id: Optional user ID to filter by
        limit: Optional limit on number of results
        
    Returns:
        List of prediction history records
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        predictions = prediction_storage.get_predictions(user_id=user_id, limit=limit)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving predictions: {str(e)}")


@app.get("/api/predictions/user/{user_id}", response_model=List[PredictionHistory])
async def get_user_predictions(
    user_id: str,
    limit: Optional[int] = Query(None, description="Limit number of results")
):
    """
    Get predictions for a specific user.
    
    Args:
        user_id: User ID
        limit: Optional limit on number of results
        
    Returns:
        List of prediction history records for the user
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        predictions = prediction_storage.get_predictions(user_id=user_id, limit=limit)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user predictions: {str(e)}")


@app.get("/api/predictions/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get aggregated statistics for dashboard.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        DashboardStats with aggregated statistics
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        stats = prediction_storage.get_dashboard_stats(user_id=user_id)
        return DashboardStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

