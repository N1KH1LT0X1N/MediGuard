import { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Preloader from './components/Preloader';
import WhatsAppFloatingButton from './components/WhatsAppFloatingButton';
import BotpressFloatingButton from './components/BotpressFloatingButton';
import HomePage from './pages/HomePage';
import DoctorHomePage from './pages/DoctorHomePage';
import PatientHomePage from './pages/PatientHomePage';
import WhatsAppPage from './pages/WhatsAppPage';

// Doctor Pages
import PredictDisease from './pages/PredictDisease';
import DoctorDashboard from './pages/doctor/DoctorDashboard';
import DoctorPatients from './pages/doctor/DoctorPatients';
import DoctorAppointments from './pages/doctor/DoctorAppointments';
import DoctorSettings from './pages/doctor/DoctorSettings';
import ScalingLayerVisualization from './pages/doctor/ScalingLayerVisualization';
import HashChain from './pages/HashChain';

// Patient Pages
import PatientDashboard from './pages/patient/PatientDashboard';
import PatientAppointments from './pages/patient/PatientAppointments';
import PatientReports from './pages/patient/PatientReports';
import FindDoctors from './pages/patient/FindDoctors';
import MedicalHistory from './pages/patient/MedicalHistory';
import PatientSettings from './pages/patient/PatientSettings';

const App = () => {
  const [showPreloader, setShowPreloader] = useState(true);

  const handlePreloaderComplete = () => {
    setShowPreloader(false);
  };

  return (
    <>
      {showPreloader && <Preloader onComplete={handlePreloaderComplete} />}
      {!showPreloader && (
        <>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/whatsapp" element={<WhatsAppPage />} />
            
            {/* Home route redirects to patient by default */}
            <Route path="/home" element={<Navigate to="/home/patient" replace />} />
            
            {/* Doctor Routes */}
            <Route path="/home/doctor" element={<DoctorHomePage />}>
              <Route index element={<Navigate to="/home/doctor/dashboard" replace />} />
              <Route path="dashboard" element={<DoctorDashboard />} />
              <Route path="patients" element={<DoctorPatients />} />
              <Route path="hash-chain" element={<HashChain />} />
              <Route path="settings" element={<DoctorSettings />} />
              <Route path="scaling-layer" element={<ScalingLayerVisualization />} />
            </Route>

            {/* Patient Routes */}
            <Route path="/home/patient" element={<PatientHomePage />}>
              <Route index element={<Navigate to="/home/patient/predict" replace />} />
              <Route path="dashboard" element={<PatientDashboard />} />
              <Route path="predict" element={<PredictDisease />} />
              <Route path="hash-chain" element={<HashChain />} />
              <Route path="reports" element={<PatientReports />} />
              <Route path="doctors" element={<FindDoctors />} />
              <Route path="settings" element={<PatientSettings />} />
            </Route>
          </Routes>
          <BotpressFloatingButton />
          <WhatsAppFloatingButton />
        </>
      )}
    </>
  );
};

export default App;
