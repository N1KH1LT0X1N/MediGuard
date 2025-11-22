# 🚀 How to Start the MediGuard AI Project

This guide will help you start both the backend (FastAPI) and frontend (React/Vite) services.

## 📋 Prerequisites

- **Python 3.13+** (or Python 3.12+)
- **Node.js 18+** (recommended: Node.js 20+)
- **npm** or **yarn** package manager

## 🔧 Initial Setup (One-time)

### 1. Backend Setup

```bash
# Navigate to project root
cd /Users/Hetansh/Github/ggw-redact-mediguard/ggw_redact

# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies (if not already installed)
npm install
```

## 🚀 Starting the Project

You need to run **both** the backend and frontend servers. You can do this in two ways:

### Option 1: Manual Start (Recommended for Development)

#### Terminal 1 - Backend Server

```bash
# Navigate to project root
cd /Users/Hetansh/Github/ggw-redact-mediguard/ggw_redact

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate  # On Windows

# Start the FastAPI server
cd backend
python main.py

# OR using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

#### Terminal 2 - Frontend Server

```bash
# Navigate to frontend directory
cd /Users/Hetansh/Github/ggw-redact-mediguard/ggw_redact/frontend

# Start the Vite development server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

### Option 2: Using the Startup Script

A convenience script is available to start both services:

```bash
# Make the script executable (first time only)
chmod +x start.sh

# Run the startup script
./start.sh
```

This will start both servers in separate terminal windows/tabs.

## ✅ Verification

### Backend Health Check

Once the backend is running, verify it's working:

```bash
# Check health endpoint
curl http://localhost:8000/api/health

# Or visit in browser
open http://localhost:8000/api/health
```

### Backend API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Frontend

Open your browser and navigate to: **http://localhost:5173**

## 📁 Project Structure

```
ggw_redact/
├── backend/              # FastAPI backend
│   ├── main.py          # Main FastAPI application
│   ├── requirements.txt # Python dependencies
│   ├── models/          # Pydantic schemas
│   └── services/        # Business logic services
├── frontend/            # React/Vite frontend
│   ├── src/            # React source code
│   ├── package.json    # Node.js dependencies
│   └── vite.config.js  # Vite configuration
├── ml/                  # Machine learning code
├── venv/                # Python virtual environment
└── *.pkl                # Trained model files
```

## 🔌 API Endpoints

### Backend Endpoints

- `GET /` - Root endpoint with API info
- `GET /api/health` - Health check
- `POST /api/predict` - Predict disease from features
- `POST /api/upload/image` - Upload image for OCR
- `POST /api/upload/pdf` - Upload PDF for OCR
- `POST /api/upload/csv` - Upload CSV/Excel for parsing

### Frontend Routes

- `/` - Landing page
- `/home/patient/predict` - Disease prediction interface
- `/home/patient/*` - Patient dashboard routes
- `/home/doctor/*` - Doctor dashboard routes

## 🛠️ Development Tips

### Backend Development

- The backend uses **hot reload** with `--reload` flag
- Changes to Python files will automatically restart the server
- Check logs in the terminal for errors

### Frontend Development

- Vite provides **Hot Module Replacement (HMR)**
- Changes to React components will update instantly in the browser
- Check browser console for errors

### Common Issues

#### Port Already in Use

**Backend (port 8000):**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port
uvicorn backend.main:app --reload --port 8001
```

**Frontend (port 5173):**
```bash
# Find and kill process
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

#### Virtual Environment Not Activated

Make sure you activate the virtual environment before running the backend:
```bash
source venv/bin/activate  # macOS/Linux
```

#### Frontend Dependencies Missing

If you see module errors in the frontend:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🎯 Next Steps

1. **Backend**: Verify the API is running at http://localhost:8000/docs
2. **Frontend**: Open http://localhost:5173 in your browser
3. **Test**: Try the disease prediction feature at `/home/patient/predict`

## 📚 Additional Documentation

- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **Project Context**: `PROJECT_CONTEXT.md`
- **Model Training**: `MODEL_TRAINING_LOGIC.md`
- **Scaling Logic**: `SCALING_LOGIC_EXPLAINED.md`

---

**Happy Coding! 🎉**

