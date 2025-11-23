# MediGuard AI Backend

FastAPI backend for disease prediction with OCR, file parsing, and explainability.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# From project root
cd backend
python main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /api/health` - Check service status

### Prediction
- `POST /api/predict` - Predict disease from manual feature entry
  - Body: `{ "features": { "Glucose": 120, "Cholesterol": 180, ... } }`
  - Returns: Prediction with probabilities and explainability

### File Upload
- `POST /api/upload/image` - Upload image (PNG/JPG) for OCR extraction
- `POST /api/upload/pdf` - Upload PDF for OCR extraction
- `POST /api/upload/csv` - Upload CSV/Excel for feature extraction

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Notes

- Ensure model files (`disease_prediction_model.pkl`, `label_encoder.pkl`) are in project root
- Ensure training data (`cleaned_test.csv`) is in project root for explainability
- CORS is configured for `http://localhost:5173` (Vite default port)

