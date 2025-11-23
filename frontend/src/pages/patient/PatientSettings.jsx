import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { createUser } from '../../lib/api';

const PatientSettings = () => {
  const [currentUserId, setCurrentUserId] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Load current user ID from sessionStorage
    const userId = sessionStorage.getItem('mediguard_user_id') || 'Not set';
    setCurrentUserId(userId);
  }, []);

  const createNewPatient = async () => {
    try {
      setLoading(true);
      // Create new user via API
      const userData = await createUser();
      const newUserId = userData.user_id;
      
      // Store in sessionStorage
      sessionStorage.setItem('mediguard_user_id', newUserId);
      setCurrentUserId(newUserId);
      
      // Show confirmation
      alert(`New patient created!\nUser ID: ${newUserId}\n\nMake predictions to add data for this patient.`);
      
      // Optionally navigate to predict page
      navigate('/home/patient/predict');
    } catch (error) {
      console.error('Error creating new patient:', error);
      alert('Failed to create new patient. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearCurrentPatient = () => {
    if (window.confirm('Are you sure you want to clear your current patient ID? This will create a new patient on your next prediction.')) {
      sessionStorage.removeItem('mediguard_user_id');
      setCurrentUserId('Not set');
      alert('Patient ID cleared. A new patient ID will be created when you make your next prediction.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
          <h1 className="text-3xl font-bold text-[#222123] mb-2">Patient Settings</h1>
          <p className="text-gray-600 mb-8">Manage your account settings and patient identity.</p>

          {/* Current Patient ID */}
          <div className="mb-8 p-4 bg-gray-50 rounded-lg border-2 border-[#222123]">
            <h2 className="text-xl font-bold text-[#222123] mb-2">Current Patient ID</h2>
            <p className="text-sm text-gray-600 mb-2">This ID identifies you as a patient. All your predictions are linked to this ID.</p>
            <div className="flex items-center space-x-4">
              <code className="flex-1 px-4 py-2 bg-white border-2 border-[#222123] rounded-lg text-sm font-mono break-all">
                {currentUserId}
              </code>
              <button
                onClick={clearCurrentPatient}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-bold"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Create New Patient */}
          <div className="mb-8 p-4 bg-[#7FFF00] bg-opacity-10 rounded-lg border-2 border-[#7FFF00]">
            <h2 className="text-xl font-bold text-[#222123] mb-2">Create New Patient</h2>
            <p className="text-sm text-gray-600 mb-4">
              Click the button below to create a new patient ID. This is useful for testing with multiple patients.
              After creating a new patient, make predictions to add data for that patient.
            </p>
            <button
              onClick={createNewPatient}
              disabled={loading}
              className="px-6 py-3 bg-[#7FFF00] text-black rounded-lg hover:bg-[#6ee000] transition-colors font-bold border-2 border-[#222123] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Creating...' : 'Create New Patient'}
            </button>
          </div>

          {/* Instructions */}
          <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
            <h3 className="text-lg font-bold text-blue-900 mb-2">How to Add Multiple Patients:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
              <li>Click "Create New Patient" above to generate a new patient ID</li>
              <li>Go to "Predict Disease" and make a prediction (upload CSV/PDF or enter manually)</li>
              <li>The prediction will be saved under the new patient ID</li>
              <li>In the Doctor Dashboard, you'll see multiple patients in the filter dropdown</li>
              <li>Repeat steps 1-3 to add more patients</li>
            </ol>
          </div>

          {/* Quick Test Helper */}
          <div className="mt-8 p-4 bg-yellow-50 rounded-lg border-2 border-yellow-200">
            <h3 className="text-lg font-bold text-yellow-900 mb-2">Quick Test Tip:</h3>
            <p className="text-sm text-yellow-800 mb-2">
              For quick testing, you can also open the browser console and run:
            </p>
            <code className="block px-4 py-2 bg-white border border-yellow-300 rounded text-xs font-mono mb-2">
              sessionStorage.removeItem('mediguard_user_id')
            </code>
            <p className="text-sm text-yellow-800">
              Then refresh the page and make a prediction - a new patient ID will be automatically created via API.
            </p>
          </div>

          {/* Scaling Layer Visualization Link */}
          <div className="mt-8 p-6 bg-gradient-to-r from-[#7FFF00] to-[#6ee000] rounded-lg border-2 border-[#222123] shadow-lg">
            <h3 className="text-xl font-bold text-[#222123] mb-2">🔬 Scaling Layer Visualization</h3>
            <p className="text-sm text-[#222123] mb-4">
              Want to understand how raw clinical values are transformed into model-ready inputs? 
              Explore our interactive scaling layer visualization to see the transformation process in action!
            </p>
            <button
              onClick={() => navigate('/home/doctor/scaling-layer')}
              className="px-6 py-3 bg-[#222123] text-white rounded-lg hover:bg-gray-800 transition-colors font-bold border-2 border-white"
            >
              View Scaling Layer Architecture →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientSettings;
