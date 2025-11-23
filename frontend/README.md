# MediGuard AI: Intelligent Triage Assistant - Frontend

An intelligent triage assistant that analyzes 24 pre-scaled blood test parameters to predict the likelihood of multiple diseases (Heart Disease, Diabetes, Anemia, Thalassemia, Thrombocytopenia, and Healthy status). The system serves as a crucial second opinion for triage nurses, routing patients efficiently and safely.

## 🎯 Project Overview

MediGuard AI is a machine learning system that predicts diseases from clinical blood test parameters. The system consists of three main modules:

- **Module A (Model)**: ✅ **Complete** - Robust Multi-Class Classification model trained with XGBoost (saved model) / Gradient Boosting (train_model.py)
- **Module B (Scaling Bridge)**: ✅ **Complete** - Complete interface layer converting raw clinical inputs to scaled format
- **Module C (Dashboard)**: ✅ **Frontend Complete** - React + Vite frontend with modern UI components (Backend API pending)

## ✨ Key Features

### Frontend Features
- **Modern React Application**: Built with React 19, Vite 6, and React Router 7
- **Responsive Design**: Mobile-first design with Tailwind CSS 4
- **Multiple User Interfaces**: Separate views for patients and doctors
- **Disease Prediction Interface**: Manual data entry form with validation for all 24 clinical parameters
- **File Upload Support**: UI for uploading images (PNG/JPG), PDFs, and CSV/Excel files
- **Smooth Animations**: GSAP and Framer Motion for enhanced user experience
- **Data Visualization**: Recharts integration for displaying medical data

### Backend Features (Pending)
- **RESTful API**: FastAPI backend for prediction endpoints (to be implemented)
- **Real-time Predictions**: API integration for live disease prediction
- **Explainability**: Integration with LIME-based explainability module

### ML Features
- **Multi-Disease Classification**: Predicts 6 different disease classes from 24 clinical features
- **Scaling Bridge**: Converts raw clinical values (various units and scales) to normalized [0, 1] range
- **High Accuracy**: 95.5% accuracy on test set with high recall for critical diseases
- **Production-Ready**: Complete CLI prediction tool with multiple input methods
- **Comprehensive Documentation**: Detailed documentation for all components

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Project Structure](#project-structure)
5. [Components](#components)
6. [Performance Metrics](#performance-metrics)
7. [Documentation](#documentation)
8. [Future Work](#future-work)

## 📋 24 Clinical Features

The disease prediction model requires 24 clinical parameters in the following order:

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

### Feature Validation Ranges

The manual entry form validates each feature against expected ranges:
- **Glucose**: 39.09 - 231.86 mg/dL
- **Cholesterol**: 52.73 - 344.59 mg/dL
- **Hemoglobin**: 10.58 - 19.45 g/dL
- **Platelets**: 84,000 - 516,000 cells/μL
- And more... (see `PredictDisease.jsx` for complete list)

## 📁 Frontend Project Structure

```
frontend/
│
├── package.json                   # Node.js dependencies and scripts
├── vite.config.js                 # Vite configuration with Tailwind CSS
├── eslint.config.js               # ESLint configuration
├── index.html                     # HTML entry point
│
├── public/
│   ├── images/                    # Static images (logos, backgrounds, etc.)
│   ├── videos/                    # Video assets
│   └── fonts/                     # Custom fonts (ProximaNova)
│
└── src/
    ├── main.jsx                   # React application entry point
    ├── App.jsx                    # Main routing component
    ├── index.css                  # Global styles with Tailwind CSS
    │
    ├── pages/                     # Page components
    │   ├── HomePage.jsx           # Landing page
    │   ├── PredictDisease.jsx     # Disease prediction interface
    │   ├── PatientHomePage.jsx    # Patient dashboard layout
    │   ├── DoctorHomePage.jsx     # Doctor dashboard layout
    │   ├── patient/               # Patient-specific pages
    │   │   ├── PatientAppointments.jsx
    │   │   ├── PatientReports.jsx
    │   │   ├── FindDoctors.jsx
    │   │   ├── MedicalHistory.jsx
    │   │   └── PatientSettings.jsx
    │   └── doctor/                # Doctor-specific pages
    │       ├── DoctorDashboard.jsx
    │       ├── DoctorPatients.jsx
    │       ├── DoctorAppointments.jsx
    │       └── DoctorSettings.jsx
    │
    ├── components/                 # Reusable components
    │   ├── NavBar.jsx             # Main navigation bar
    │   ├── PatientNavBar.jsx      # Patient navigation
    │   ├── DoctorNavBar.jsx       # Doctor navigation
    │   ├── DashboardNavBar.jsx    # Dashboard navigation
    │   ├── ui/                    # UI components
    │   │   ├── CategoryList.jsx   # Category listing component
    │   │   └── chart.jsx          # Chart component
    │   ├── blocks/                # Block components
    │   │   └── features-9.jsx    # Features block
    │   ├── ClipPathTitle.jsx      # Title component with clip path
    │   └── VideoPinSection.jsx    # Video pin section
    │
    ├── sections/                  # Page sections
    │   ├── HeroSection.jsx        # Hero section with animations
    │   ├── MessageSection.jsx     # Message section
    │   ├── BenefitSection.jsx     # Benefits section
    │   └── FooterSection.jsx      # Footer section
    │
    ├── constants/                 # Constants and configuration
    │   └── index.js              # Shared constants
    │
    └── lib/                       # Utility functions
        └── utils.js              # Helper utilities
```

## 🚀 Frontend Quick Start

### Prerequisites

- Node.js 18+ (recommended: Node.js 20+)
- npm or yarn package manager

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Development

```bash
# Start development server (runs on http://localhost:5173)
npm run dev
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Linting

```bash
# Run ESLint
npm run lint
```

## 🛠️ Technology Stack

### Core Framework
- **React 19.1.0**: Modern React with latest features
- **Vite 6.3.5**: Fast build tool and dev server
- **React Router DOM 7.9.6**: Client-side routing

### Styling
- **Tailwind CSS 4.1.8**: Utility-first CSS framework
- **@tailwindcss/vite 4.1.8**: Vite plugin for Tailwind CSS
- **Custom CSS**: Additional styling in `index.css`

### Animations & Interactions
- **GSAP 3.13.0**: Professional animation library
- **@gsap/react 2.1.2**: React hooks for GSAP
- **Framer Motion 12.23.24**: Animation library for React

### Data Visualization
- **Recharts 3.4.1**: Composable charting library

### Utilities
- **clsx 2.1.1**: Conditional class names
- **tailwind-merge 3.4.0**: Merge Tailwind classes
- **lucide-react 0.554.0**: Icon library
- **react-responsive 10.0.1**: Media queries for React
- **dotted-map 2.2.3**: Map visualization
- **three 0.181.2**: 3D graphics library

## 📱 Pages & Routes

### Public Routes
- `/` - Landing page with hero section and feature overview

### Patient Routes
- `/home/patient` - Patient dashboard (redirects to predict)
- `/home/patient/predict` - Disease prediction interface
- `/home/patient/appointments` - Patient appointments
- `/home/patient/reports` - Patient medical reports
- `/home/patient/doctors` - Find doctors
- `/home/patient/settings` - Patient settings

### Doctor Routes
- `/home/doctor` - Doctor dashboard (redirects to dashboard)
- `/home/doctor/dashboard` - Doctor dashboard overview
- `/home/doctor/patients` - Patient management
- `/home/doctor/appointments` - Appointment management
- `/home/doctor/settings` - Doctor settings

## 🎨 Key Components

### PredictDisease Component
The main disease prediction interface with:
- **Multiple Input Methods**: 
  - Image upload (PNG/JPG) for OCR analysis
  - PDF upload for document analysis
  - CSV/Excel upload for batch processing
  - Manual data entry form with all 24 clinical parameters
- **Form Validation**: Real-time validation with range checking
- **Upload Progress**: Visual progress indicators
- **Analysis Animation**: Step-by-step analysis visualization

### Navigation Components
- **NavBar**: Main navigation for landing page
- **PatientNavBar**: Patient-specific navigation
- **DoctorNavBar**: Doctor-specific navigation
- **DashboardNavBar**: Dashboard navigation

### Section Components
- **HeroSection**: Animated hero section with GSAP
- **MessageSection**: Feature messaging
- **BenefitSection**: Benefits showcase
- **FooterSection**: Footer with links

## 🔌 Backend Integration (Pending)

The frontend is currently UI-only. Backend API integration is pending:

### Required Backend Endpoints

1. **POST /api/predict**
   - Accepts: 24 clinical feature values
   - Returns: Predicted disease, probabilities, scaled features

2. **POST /api/upload/image**
   - Accepts: Image file (PNG/JPG)
   - Returns: Extracted feature values

3. **POST /api/upload/pdf**
   - Accepts: PDF file
   - Returns: Extracted feature values

4. **POST /api/upload/csv**
   - Accepts: CSV/Excel file
   - Returns: Extracted feature values

### Integration Steps (When Backend is Ready)

1. Create API client in `src/lib/api.js` or `src/api/client.js`
2. Update `PredictDisease.jsx` to call API endpoints
3. Add error handling and loading states
4. Display prediction results with visualizations

## 📊 Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Landing Page | ✅ Complete | Hero, sections, navigation |
| Patient Dashboard | ✅ Complete | Layout and navigation |
| Doctor Dashboard | ✅ Complete | Layout and navigation |
| Disease Prediction UI | ✅ Complete | Manual entry form with validation |
| File Upload UI | ✅ Complete | Image, PDF, CSV upload interfaces |
| Backend API Integration | ⚠️ Pending | No API calls implemented yet |
| Real-time Predictions | ⚠️ Pending | Requires backend |
| Explainability Visualization | ⚠️ Pending | Requires backend integration |
| Patient Reports | ⚠️ UI Only | No data integration |
| Appointments | ⚠️ UI Only | No data integration |

## 🐛 Known Issues

1. **No Backend Integration**: Frontend is currently UI-only. All prediction functionality requires backend API implementation.
2. **File Upload**: Upload UI exists but doesn't process files (requires OCR/parsing backend).
3. **Data Persistence**: No data persistence layer (localStorage/backend) implemented.

## 🔮 Future Enhancements

1. **Backend API Integration**: Connect to FastAPI backend for predictions
2. **Real-time Updates**: WebSocket integration for live updates
3. **State Management**: Add Redux or Zustand for global state
4. **Error Boundaries**: Implement React error boundaries
5. **Testing**: Add unit and integration tests
6. **Accessibility**: Improve ARIA labels and keyboard navigation
7. **Internationalization**: Add i18n support
8. **PWA Support**: Make it a Progressive Web App

## 📝 Notes

- The frontend uses JavaScript (JSX), not TypeScript
- Tailwind CSS 4 is used via the Vite plugin
- All animations use GSAP or Framer Motion
- The project structure follows React Router nested routes pattern

## 🔧 Frontend Architecture

### Component Structure

The frontend follows a modular component architecture:

1. **Pages**: Top-level route components (`pages/`)
2. **Components**: Reusable UI components (`components/`)
3. **Sections**: Page sections like hero, footer (`sections/`)
4. **Utilities**: Helper functions and constants (`lib/`, `constants/`)

### State Management

Currently using React's built-in state management:
- `useState` for local component state
- `useNavigate` from React Router for navigation
- No global state management (Redux/Zustand) yet

### Styling Approach

- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS**: Additional styles in `index.css`
- **Responsive Design**: Mobile-first approach with breakpoints
- **Custom Theme**: Custom color palette and fonts defined in `index.css`

### Animation Strategy

- **GSAP**: Complex animations (hero section, scroll effects)
- **Framer Motion**: Component-level animations
- **CSS Transitions**: Simple hover and state transitions

## 📊 Development Notes

### Current Implementation Status

- ✅ **UI Components**: All major UI components implemented
- ✅ **Routing**: Complete routing structure with React Router
- ✅ **Forms**: Manual data entry form with validation
- ✅ **File Upload UI**: Upload interfaces for all file types
- ⚠️ **API Integration**: Pending backend implementation
- ⚠️ **Data Processing**: File processing requires backend
- ⚠️ **State Persistence**: No data persistence layer

### Build Performance

- **Vite Dev Server**: Fast HMR (Hot Module Replacement)
- **Production Build**: Optimized with Vite's build pipeline
- **Bundle Size**: Optimized with tree-shaking

## 📚 Related Documentation

For complete project documentation, see:

- **`../docs/PROJECT_CONTEXT.md`**: Full project context and architecture
- **`../docs/MODEL_TRAINING_LOGIC.md`**: ML model training documentation
- **`../docs/SCALING_LOGIC_EXPLAINED.md`**: Scaling bridge documentation
- **`../ml/scaling_layer/README.md`**: Scaling bridge usage guide

## 🔮 Next Steps

### Immediate Priorities

1. **Backend API Development**
   - Implement FastAPI backend with prediction endpoints
   - Add file upload processing (OCR for images/PDFs, CSV parsing)
   - Integrate with existing `predict.py` functionality

2. **Frontend-Backend Integration**
   - Create API client utilities
   - Connect `PredictDisease` component to backend
   - Add error handling and loading states
   - Display prediction results with visualizations

3. **Data Visualization**
   - Integrate Recharts for probability visualization
   - Add feature importance charts
   - Display explainability results from LIME

### Future Enhancements

- **State Management**: Add Redux or Zustand for global state
- **Authentication**: User authentication and authorization
- **Real-time Updates**: WebSocket integration for live updates
- **Testing**: Unit and integration tests
- **Accessibility**: Improve ARIA labels and keyboard navigation
- **PWA**: Progressive Web App support
- **Internationalization**: Multi-language support

## 🐛 Troubleshooting

### Common Issues

#### 1. Module Not Found Errors

**Error**: `Cannot find module 'xyz'`

**Solution**: Install missing dependencies:
```bash
npm install
```

#### 2. Vite Dev Server Issues

**Error**: Port already in use

**Solution**: Kill the process using the port or use a different port:
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

#### 3. Build Errors

**Error**: Build fails with module resolution errors

**Solution**: Clear cache and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

#### 4. Tailwind CSS Not Working

**Error**: Styles not applying

**Solution**: Ensure Tailwind is properly configured in `vite.config.js` and `index.css` imports Tailwind.

#### 5. React Router Navigation Issues

**Error**: Routes not working

**Solution**: Ensure `BrowserRouter` wraps the app in `main.jsx` and routes are properly configured in `App.jsx`.

## 📝 License

Part of the GGW Redact MediGuard project.

## 👥 Contributing

This is a research/development project. For questions or contributions, please refer to the project documentation.

---

**Last Updated**: Based on current frontend implementation  
**Frontend Status**: UI Complete, Backend Integration Pending  
**Version**: 1.0 (Frontend Implementation)
