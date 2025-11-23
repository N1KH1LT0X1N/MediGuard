"""
FastAPI main application for MediGuard AI backend.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import sys
import uuid
from datetime import datetime
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
    DashboardStats,
    UserPreferences,
    UpdateUserPreferencesRequest
)
from backend.services.prediction_service import PredictionService
from backend.services.explainability_service import ExplainabilityService
from backend.services.ocr_service import ocr_service
from backend.services.file_parser import file_parser_service
from backend.services.prediction_storage_service import PredictionStorageService
from backend.services.blockchain_service import BlockchainService
from backend.services.blockchain_committer import BlockchainCommitter
from backend.config.database import close_db_connections

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
blockchain_service: Optional[BlockchainService] = None
blockchain_committer: Optional[BlockchainCommitter] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services at startup."""
    global prediction_service, explainability_service, prediction_storage
    global blockchain_service, blockchain_committer
    
    try:
        # Initialize prediction service
        model_path = PROJECT_ROOT / "models" / "disease_prediction_model.pkl"
        encoder_path = PROJECT_ROOT / "models" / "label_encoder.pkl"
        prediction_service = PredictionService(model_path, encoder_path)
        print("✓ Prediction service initialized")
        
        # Initialize explainability service
        explainability_service = ExplainabilityService()
        print("✓ Explainability service initialized")
        
        # Initialize prediction storage service (PostgreSQL)
        prediction_storage = PredictionStorageService()
        # Create tables if they don't exist
        await prediction_storage._create_tables()
        print("✓ Prediction storage service initialized (PostgreSQL)")
        
        # Initialize blockchain service (optional - uses simulated mode by default)
        try:
            blockchain_service = BlockchainService()
            blockchain_committer = BlockchainCommitter(blockchain_service, commit_interval_hours=24)
            blockchain_committer.start()
            # Message already printed by BlockchainService.__init__
        except Exception as e:
            print(f"⚠️  Blockchain service not initialized: {e}")
            print("   Continuing without blockchain (hash chain still works)")
            blockchain_service = None
            blockchain_committer = None
            
    except Exception as e:
        print(f"⚠️  Error initializing services: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global blockchain_committer
    
    if blockchain_committer:
        blockchain_committer.stop()
    
    await close_db_connections()
    print("✓ Services shut down")


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
            "get_stats": "/api/predictions/stats",
            "create_user": "/api/users/create",
            "get_user": "/api/users/{user_id}",
            "update_preferences": "/api/users/{user_id}/preferences",
            "hash_chain_verify": "/api/hash-chain/verify",
            "blockchain_verify": "/api/blockchain/verify"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    db_status = False
    blockchain_status = False
    
    if prediction_storage:
        try:
            # Quick database check
            await prediction_storage.get_predictions(limit=1)
            db_status = True
        except:
            pass
    
    if blockchain_service:
        blockchain_status = blockchain_service.is_connected()
    
    return {
        "status": "healthy",
        "prediction_service": prediction_service is not None,
        "explainability_service": explainability_service is not None,
        "database": db_status,
        "blockchain": blockchain_status
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
            try:
                explainability_json, explainability_html = explainability_service.generate_explanation(
                request.features
            )
                if not explainability_json:
                    print("⚠️  Warning: explainability_json is empty after generation")
            except Exception as e:
                print(f"⚠️  Error generating explainability: {e}")
                import traceback
                traceback.print_exc()
        
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
    Save a prediction to storage with hash chain.
    
    Args:
        request: SavePredictionRequest with user_id, input_features, prediction_result, and source
        
    Returns:
        Dictionary with prediction_id
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        prediction_id = await prediction_storage.save_prediction(
            user_id=request.user_id,
            input_features=request.input_features,
            prediction_result=request.prediction_result,
            source=request.source
        )
        return {"prediction_id": prediction_id, "message": "Prediction saved successfully with hash chain"}
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
        predictions = await prediction_storage.get_predictions(user_id=user_id, limit=limit)
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
        predictions = await prediction_storage.get_predictions(user_id=user_id, limit=limit)
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user predictions: {str(e)}")


@app.get("/api/predictions/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    user_id: Optional[str] = Query(None, description="Filter by user ID")
):
    """
    Get aggregated statistics for dashboard.
    Optimized for performance.
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        DashboardStats with aggregated statistics
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        stats = await prediction_storage.get_dashboard_stats(user_id=user_id)
        return DashboardStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard stats: {str(e)}")


@app.get("/api/users/list")
async def get_users_list(
    limit: Optional[int] = Query(100, description="Limit number of users")
):
    """
    Get list of unique user IDs who have predictions.
    Optimized: Uses DISTINCT query instead of loading all predictions.
    
    Args:
        limit: Optional limit on number of users
        
    Returns:
        List of user IDs
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        user_ids = await prediction_storage.get_unique_users(limit=limit)
        return {"users": user_ids, "count": len(user_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving users list: {str(e)}")


@app.post("/api/users/create")
async def create_user():
    """
    Create a new user and return user_id.
    User is stored in Supabase database.
    
    Returns:
        Dictionary with user_id
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{uuid.uuid4().hex[:9]}"
        
        # Create user in database
        async with prediction_storage.async_session_maker() as session:
            from backend.models.database_models import User
            user = User(
                id=user_id,
                preferences={},
                metadata={}
            )
            session.add(user)
            await session.commit()
        
        return {
            "user_id": user_id,
            "message": "User created successfully and stored in database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    """
    Get user information and statistics.
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with user info, stats, and preferences
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        # Get user from database
        async with prediction_storage.async_session_maker() as session:
            from backend.models.database_models import User
            from sqlalchemy import select
            
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_dict = user.to_dict()
        
        # Get stats
        stats = await prediction_storage.get_dashboard_stats(user_id=user_id)
        
        return {
            "user_id": user_id,
            "exists": True,
            "created_at": user_dict["created_at"],
            "updated_at": user_dict["updated_at"],
            "preferences": user_dict["preferences"],
            "metadata": user_dict["metadata"],
            "total_predictions": stats["total_predictions"],
            "diseases_detected": list(stats["disease_distribution"].keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user info: {str(e)}")


@app.put("/api/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, request: UpdateUserPreferencesRequest):
    """
    Update user preferences.
    
    Args:
        user_id: User ID
        request: UpdateUserPreferencesRequest with preferences
        
    Returns:
        Dictionary with updated preferences
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        async with prediction_storage.async_session_maker() as session:
            from backend.models.database_models import User
            from sqlalchemy import select, update
            
            # Check if user exists
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update preferences
            preferences_dict = request.preferences.dict(exclude_none=True)
            current_preferences = user.preferences or {}
            current_preferences.update(preferences_dict)
            
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    preferences=current_preferences,
                    updated_at=datetime.utcnow()
                )
            )
            await session.commit()
            
            return {
                "user_id": user_id,
                "preferences": current_preferences,
                "message": "Preferences updated successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@app.get("/api/hash-chain")
async def get_hash_chain(
    limit: Optional[int] = Query(100, description="Limit number of results")
):
    """
    Get hash chain entries with blockchain data.
    
    Args:
        limit: Optional limit on number of results
        
    Returns:
        List of hash chain entries with prediction and blockchain info
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        from backend.models.database_models import HashChain, Prediction
        from backend.config.database import get_async_session_maker
        from sqlalchemy import select, desc
        
        async_session_maker = get_async_session_maker()
        async with async_session_maker() as session:
            # Get hash chain entries with prediction data
            query = (
                select(HashChain, Prediction)
                .join(Prediction, HashChain.prediction_id == Prediction.id)
                .order_by(desc(HashChain.id))
                .limit(limit)
            )
            
            result = await session.execute(query)
            rows = result.all()
            
            entries = []
            for hash_chain, prediction in rows:
                entries.append({
                    "id": hash_chain.id,
                    "prediction_id": hash_chain.prediction_id,
                    "previous_hash": hash_chain.previous_hash,
                    "current_hash": hash_chain.current_hash,
                    "block_timestamp": hash_chain.block_timestamp.isoformat() if hash_chain.block_timestamp else None,
                    "blockchain_tx_hash": hash_chain.blockchain_tx_hash,
                    "blockchain_block_number": hash_chain.blockchain_block_number,
                    "created_at": hash_chain.created_at.isoformat() if hash_chain.created_at else None,
                    "prediction": {
                        "user_id": prediction.user_id,
                        "timestamp": prediction.timestamp.isoformat() if prediction.timestamp else None,
                        "source": prediction.source,
                        "predicted_disease": prediction.prediction_result.get("predicted_disease") if prediction.prediction_result else None
                    }
                })
            
            return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hash chain: {str(e)}")


@app.get("/api/hash-chain/verify")
async def verify_hash_chain():
    """
    Verify the integrity of the hash chain.
    
    Returns:
        Dictionary with verification results
    """
    if not prediction_storage:
        raise HTTPException(status_code=503, detail="Prediction storage service not initialized")
    
    try:
        result = await prediction_storage.verify_hash_chain()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying hash chain: {str(e)}")


@app.get("/api/blockchain/verify/{tx_hash}")
async def verify_blockchain(tx_hash: str):
    """
    Verify a transaction on the blockchain.
    
    Args:
        tx_hash: Transaction hash to verify
        
    Returns:
        Dictionary with verification results
    """
    if not blockchain_service:
        raise HTTPException(status_code=503, detail="Blockchain service not initialized")
    
    try:
        result = blockchain_service.verify_on_blockchain(tx_hash)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying blockchain transaction: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

