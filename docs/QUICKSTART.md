# 🚀 MediGuard AI - Quick Start Guide

Welcome! This guide will help you get up and running with MediGuard AI in just a few minutes.

## 📖 What is MediGuard AI?

MediGuard AI is an **Intelligent Triage Assistant** that analyzes 24 blood test parameters to predict the likelihood of multiple diseases:
- Heart Disease
- Diabetes
- Anemia
- Thalassemia
- Thrombocytopenia
- Healthy status

The system uses machine learning (XGBoost/Gradient Boosting) with **95.5% accuracy** to help triage nurses make faster, safer decisions.

## ⚡ Quick Start (5 Minutes)

### Prerequisites

Before you begin, make sure you have:
- **Python 3.12+** (or 3.13+ recommended)
- **Node.js 18+** (Node.js 20+ recommended)
- **npm** (comes with Node.js)
- **Git** (to clone the repository)

### Step 1: Clone & Navigate

```bash
# If you haven't cloned yet
git clone <repository-url>
cd ggw_redact
```

### Step 2: Backend Setup

```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
# venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Go back to project root
cd ..
```

### Step 4: Database Setup (Optional but Recommended)

The project uses **Supabase (PostgreSQL)** for data storage. You can skip this for basic testing, but it's needed for full functionality.

**Quick Setup:**
1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Get your database connection string from Project Settings → Database
4. Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_KEY=[YOUR-ANON-KEY]
```

5. Run the database migration:
```bash
cd backend
python database/migrate.py
cd ..
```

> **Note:** If you skip database setup, the app will still work but won't save predictions or user data.

### Step 5: Start the Application

You have two options:

#### Option A: Use the Startup Script (Easiest)

```bash
# Make script executable (first time only)
chmod +x start.sh

# Run the script
./start.sh
```

This starts both backend and frontend automatically!

#### Option B: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR venv\Scripts\activate  # Windows

# Start backend server
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
# Start frontend server
cd frontend
npm run dev
```

### Step 6: Access the Application

- **Frontend**: Open [http://localhost:5173](http://localhost:5173) in your browser
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

## 🎯 What You Can Do Now

### 1. Make a Disease Prediction

1. Go to [http://localhost:5173](http://localhost:5173)
2. Click "Get Started" or navigate to `/home/patient/predict`
3. Enter 24 clinical parameters manually, OR
4. Upload a file (Image, PDF, or CSV/Excel)
5. Click "Predict Disease"
6. View the prediction with probabilities and explainability

### 2. Explore the API

Visit [http://localhost:8000/docs](http://localhost:8000/docs) to see all available endpoints:
- `POST /api/predict` - Make predictions
- `POST /api/upload/image` - Upload images for OCR
- `POST /api/upload/pdf` - Upload PDFs for OCR
- `POST /api/upload/csv` - Upload CSV/Excel files
- `GET /api/predictions` - View prediction history
- `GET /api/hash-chain/verify` - Verify data integrity

### 3. Test with CLI (Command Line)

You can also test predictions directly from the command line:

```bash
# Activate virtual environment
source venv/bin/activate

# Make a prediction
python predict.py 120 180 14.5 250000 7000 4.5 42 88 29 33 8 22.5 120 80 150 5.5 100 50 25 30 72 0.9 0.01 2.5

# Or use a CSV file
python predict.py --file test_data/test_data_diabetes.csv
```

## 📁 Project Structure

```
ggw_redact/
├── backend/              # FastAPI backend server
│   ├── main.py          # Main API application
│   ├── services/        # Business logic (prediction, OCR, etc.)
│   ├── models/          # Data models and schemas
│   ├── database/        # Database migrations and setup
│   └── config/          # Configuration files
│
├── frontend/            # React + Vite frontend
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── components/  # Reusable components
│   │   └── lib/         # Utilities and API client
│   └── package.json
│
├── ml/                  # Machine learning code
│   ├── scaling_layer/   # Scaling bridge (converts raw values to 0-1)
│   └── explainability.py # LIME-based explainability
│
├── models/              # Trained ML models (.pkl files)
├── test_data/           # Sample test files
├── venv/                # Python virtual environment
│
└── docs/            # Documentation folder
    ├── QUICKSTART.md    # This file!
    ├── PROJECT_CONTEXT.md # Full project documentation
    ├── DATABASE_SETUP.md # Database setup guide
    └── STORAGE_ARCHITECTURE.md # Data storage architecture
```

## 🔑 Key Features

### ✅ What's Working

- **Disease Prediction**: Full ML pipeline with 95.5% accuracy
- **Multiple Input Methods**: Manual entry, image OCR, PDF parsing, CSV upload
- **Explainability**: LIME-based feature importance analysis
- **Hash Chain**: Immutable audit trail for all predictions
- **Blockchain Integration**: Optional blockchain commits for verification
- **User Management**: User accounts with preferences
- **Dashboard**: Patient and doctor dashboards with statistics
- **API Documentation**: Auto-generated Swagger/ReDoc docs

### ⚠️ What's Optional

- **Database**: Works without it, but needed for data persistence
- **Blockchain**: Works in simulated mode by default (no real blockchain needed)

## 🧪 Testing the System

### Test Prediction (24 Features)

Here's a sample prediction with all 24 features:

```bash
python predict.py \
  120 180 14.5 250000 7000 4.5 42 88 29 33 \
  8 22.5 120 80 150 5.5 100 50 25 30 \
  72 0.9 0.01 2.5
```

**Feature Order:**
1. Glucose (mg/dL)
2. Cholesterol (mg/dL)
3. Hemoglobin (g/dL)
4. Platelets (per microliter)
5. White Blood Cells (per microliter)
6. Red Blood Cells (million per microliter)
7. Hematocrit (%)
8. Mean Corpuscular Volume (fL)
9. Mean Corpuscular Hemoglobin (pg)
10. Mean Corpuscular Hemoglobin Concentration (g/dL)
11. Insulin (μIU/mL)
12. BMI (kg/m²)
13. Systolic Blood Pressure (mmHg)
14. Diastolic Blood Pressure (mmHg)
15. Triglycerides (mg/dL)
16. HbA1c (%)
17. LDL Cholesterol (mg/dL)
18. HDL Cholesterol (mg/dL)
19. ALT (U/L)
20. AST (U/L)
21. Heart Rate (bpm)
22. Creatinine (mg/dL)
23. Troponin (ng/mL)
24. C-reactive Protein (mg/L)

### Test Files

Sample test files are available in `test_data/`:
- `test_data_diabetes.csv`
- `test_data_anemia.csv`
- `test_data_heart_disease.csv`

## 🐛 Troubleshooting

### Backend Won't Start

**Issue**: `ModuleNotFoundError` or import errors
```bash
# Solution: Reinstall dependencies
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Issue**: Port 8000 already in use
```bash
# Solution: Kill the process or use different port
lsof -ti:8000 | xargs kill -9
# OR
uvicorn backend.main:app --reload --port 8001
```

**Issue**: Model files not found
```bash
# Solution: Ensure model files exist
ls models/disease_prediction_model.pkl
ls models/label_encoder.pkl
```

### Frontend Won't Start

**Issue**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue**: Port 5173 already in use
```bash
# Solution: Kill process or use different port
lsof -ti:5173 | xargs kill -9
# OR
npm run dev -- --port 3000
```

### Database Connection Issues

**Issue**: `Connection refused` or database errors
```bash
# Solution: Check your .env file
cat .env  # Verify DATABASE_URL is correct

# Test connection
cd backend
python -c "from config.database import engine; print('Connected!')"
```

**Issue**: Tables don't exist
```bash
# Solution: Run migration
cd backend
python database/migrate.py
```

### Prediction Errors

**Issue**: `Expected 24 features, got X`
- Make sure you provide exactly 24 values
- Check feature order matches the list above

**Issue**: Model loading errors
```bash
# Solution: Check model files exist and are valid
python -c "import joblib; joblib.load('models/disease_prediction_model.pkl')"
```

## 📚 Next Steps

### Learn More

1. **Read Full Documentation**: Check out `docs/PROJECT_CONTEXT.md` for complete architecture
2. **Database Setup**: See `docs/DATABASE_SETUP.md` for detailed database configuration
3. **Storage Architecture**: Read `docs/STORAGE_ARCHITECTURE.md` to understand data flow
4. **Model Training**: See `docs/MODEL_TRAINING_LOGIC.md` for ML model details

### Development

1. **Backend Development**: 
   - Backend auto-reloads on file changes
   - Check logs in terminal for errors
   - API docs at `/docs` update automatically

2. **Frontend Development**:
   - Hot Module Replacement (HMR) enabled
   - Changes appear instantly in browser
   - Check browser console for errors

### Production Deployment

For production deployment:
1. Set up production database (Supabase or self-hosted PostgreSQL)
2. Configure environment variables
3. Build frontend: `cd frontend && npm run build`
4. Serve frontend with a web server (nginx, etc.)
5. Run backend with production ASGI server (gunicorn + uvicorn)

## 🎓 Understanding the System

### How It Works

1. **Input**: User provides 24 clinical parameters (manually or via file upload)
2. **Scaling**: Raw values are converted to 0-1 range using the scaling bridge
3. **Prediction**: ML model predicts disease with probabilities
4. **Explainability**: LIME analyzes which features contributed most
5. **Storage**: Prediction saved to database with hash chain for immutability
6. **Blockchain**: Optional blockchain commit for external verification

### Key Components

- **Prediction Service**: Loads model and makes predictions
- **Scaling Bridge**: Converts raw clinical values to model format
- **OCR Service**: Extracts text from images/PDFs
- **File Parser**: Parses CSV/Excel files
- **Hash Chain Service**: Creates immutable audit trail
- **Blockchain Service**: Commits to blockchain (optional)

## 💡 Tips

1. **Start Simple**: Test with manual entry first, then try file uploads
2. **Check API Docs**: Visit `/docs` to see all available endpoints
3. **Use Test Data**: Sample files in `test_data/` are great for testing
4. **Database Optional**: You can test predictions without database setup
5. **Blockchain Optional**: Works in simulated mode by default

## 🆘 Need Help?

- **Check Logs**: Backend logs show in terminal, frontend logs in browser console
- **API Docs**: Visit `http://localhost:8000/docs` for interactive API testing
- **Documentation**: Read the detailed docs in the project root
- **Health Check**: Visit `http://localhost:8000/api/health` to verify backend status

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend starts without errors (`http://localhost:8000/api/health`)
- [ ] Frontend loads (`http://localhost:5173`)
- [ ] Can make a prediction via web interface
- [ ] Can make a prediction via CLI (`python predict.py ...`)
- [ ] API docs accessible (`http://localhost:8000/docs`)
- [ ] Database connected (if configured)
- [ ] Hash chain working (check `/api/hash-chain/verify`)

---

**That's it! You're ready to use MediGuard AI! 🎉**

For more details, check out the other documentation files in the project root.

