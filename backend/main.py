"""
FastAPI main application for MediGuard AI backend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import sys
from typing import Dict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.schemas import (
    PredictionRequest,
    PredictionResponse,
    FileUploadResponse,
    ErrorResponse
)
from backend.services.prediction_service import PredictionService
from backend.services.explainability_service import ExplainabilityService
from backend.services.ocr_service import ocr_service
from backend.services.file_parser import file_parser_service

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


@app.on_event("startup")
async def startup_event():
    """Initialize services at startup."""
    global prediction_service, explainability_service
    
    try:
        # Initialize prediction service
        model_path = PROJECT_ROOT / "disease_prediction_model.pkl"
        encoder_path = PROJECT_ROOT / "label_encoder.pkl"
        prediction_service = PredictionService(model_path, encoder_path)
        print("✓ Prediction service initialized")
        
        # Initialize explainability service
        explainability_service = ExplainabilityService()
        print("✓ Explainability service initialized")
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
            "upload_csv": "/api/upload/csv"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

