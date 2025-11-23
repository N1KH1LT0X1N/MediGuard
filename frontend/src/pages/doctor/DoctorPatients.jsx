import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPredictions, getDashboardStats, getUsersList } from '../../lib/api';

const DoctorPatients = () => {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const loadPatients = async () => {
      try {
        setLoading(true);
        
        // OPTIMIZED: Get unique users using dedicated endpoint (fast DISTINCT query)
        // Instead of loading 1000 predictions just to get user IDs
        const usersResponse = await getUsersList(100);
        const uniqueUserIds = usersResponse.users || [];
        
        if (uniqueUserIds.length === 0) {
          setPatients([]);
          setError(null);
          setLoading(false);
          return;
        }
        
        // OPTIMIZED: Fetch stats and recent predictions for all users in parallel (batch requests)
        const statsPromises = uniqueUserIds.map(userId => 
          getDashboardStats(userId).catch(err => {
            console.error(`Error fetching stats for ${userId}:`, err);
            return null;
          })
        );
        
        const recentPredictionsPromises = uniqueUserIds.map(userId =>
          getPredictions(userId, 5).catch(err => {
            console.error(`Error fetching predictions for ${userId}:`, err);
            return [];
          })
        );
        
        // Execute all requests in parallel
        const [statsResults, recentPredictionsResults] = await Promise.all([
          Promise.all(statsPromises),
          Promise.all(recentPredictionsPromises)
        ]);
        
        // Build patient list from stats and recent predictions
        const patientList = uniqueUserIds.map((userId, index) => {
          const stats = statsResults[index];
          const recentPreds = recentPredictionsResults[index] || [];
          const latestPrediction = recentPreds.length > 0 ? recentPreds[0] : null;
          
          // Extract diseases from stats
          const diseases = stats ? Object.keys(stats.disease_distribution || {}) : [];
          
          // Extract sources from recent predictions
          const sources = [...new Set(recentPreds.map(p => p.source).filter(Boolean))];
          
          return {
            userId: userId,
            predictions: recentPreds,
            totalPredictions: stats?.total_predictions || 0,
            diseases: diseases,
            latestPrediction: latestPrediction,
            sources: sources
          };
        });
        
        // Sort by latest prediction date (most recent first)
        patientList.sort((a, b) => {
          if (!a.latestPrediction) return 1;
          if (!b.latestPrediction) return -1;
          return new Date(b.latestPrediction.timestamp) - new Date(a.latestPrediction.timestamp);
        });
        
        setPatients(patientList);
        setError(null);
      } catch (err) {
        console.error('Error loading patients:', err);
        setError(err.message || 'Failed to load patients');
      } finally {
        setLoading(false);
      }
    };

    loadPatients();
  }, []);

  const formatDate = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (e) {
      return timestamp;
    }
  };

  const getDiseaseColor = (disease) => {
    const colors = {
      'Anemia': 'bg-red-100 text-red-800 border-red-300',
      'Diabetes': 'bg-orange-100 text-orange-800 border-orange-300',
      'Heart Disease': 'bg-red-200 text-red-900 border-red-400',
      'Thrombocytopenia': 'bg-purple-100 text-purple-800 border-purple-300',
      'Thalassemia': 'bg-blue-100 text-blue-800 border-blue-300',
      'Healthy': 'bg-[#7FFF00] bg-opacity-20 text-[#222123] border-[#7FFF00]'
    };
    return colors[disease] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getSourceBadgeColor = (source) => {
    const colors = {
      manual: 'bg-blue-100 text-blue-800',
      pdf: 'bg-red-100 text-red-800',
      csv: 'bg-green-100 text-green-800',
      image: 'bg-purple-100 text-purple-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const handlePatientClick = (userId) => {
    navigate(`/home/doctor/dashboard?patient=${userId}`);
  };

  const filteredPatients = patients.filter(patient => {
    const searchLower = searchTerm.toLowerCase();
    return (
      patient.userId.toLowerCase().includes(searchLower) ||
      patient.diseases.some(d => d.toLowerCase().includes(searchLower)) ||
      patient.sources.some(s => s.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#7FFF00] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading patients...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-xl p-6 border-2 border-red-200 shadow-lg max-w-md">
          <h3 className="text-xl font-bold text-red-600 mb-2">Error</h3>
          <p className="text-gray-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-fadeIn">
          <h1 className="text-3xl font-bold text-[#222123] mb-2">Patients</h1>
          <p className="text-gray-600">View and manage your patient list</p>
        </div>

        {/* Search Bar */}
        <div className="mb-6 animate-fadeIn">
          <div className="bg-white rounded-xl p-4 border-2 border-[#222123] shadow-lg">
            <input
              type="text"
              placeholder="Search by patient ID, disease, or source..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-[#7FFF00]"
            />
          </div>
        </div>

        {/* Stats Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">{patients.length}</p>
              <p className="text-sm text-gray-600 mt-1">Total Patients</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">
                {patients.reduce((sum, p) => sum + p.totalPredictions, 0)}
              </p>
              <p className="text-sm text-gray-600 mt-1">Total Predictions</p>
            </div>
          </div>
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-center">
              <p className="text-3xl font-bold text-[#222123]">
                {new Set(patients.flatMap(p => p.diseases)).size}
              </p>
              <p className="text-sm text-gray-600 mt-1">Unique Diseases</p>
            </div>
          </div>
        </div>

        {/* Patient List */}
        {filteredPatients.length === 0 ? (
          <div className="bg-white rounded-xl p-8 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <p className="text-gray-500 text-center py-8">
              {searchTerm ? 'No patients found matching your search' : 'No patients available'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPatients.map((patient) => {
              const latestDisease = patient.latestPrediction?.prediction_result?.predicted_disease || 'Unknown';
              const latestProb = patient.latestPrediction?.prediction_result?.probabilities?.[latestDisease] || 0;

              return (
                <div
                  key={patient.userId}
                  onClick={() => handlePatientClick(patient.userId)}
                  className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg hover:border-[#7FFF00] transition-all cursor-pointer hover:shadow-xl animate-fadeIn"
                >
                  {/* Patient Header */}
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-lg font-bold text-[#222123] truncate">
                        {patient.userId.length > 20 ? `${patient.userId.substring(0, 20)}...` : patient.userId}
                      </h3>
                      <span className="text-xs text-gray-500">
                        {patient.totalPredictions} {patient.totalPredictions === 1 ? 'prediction' : 'predictions'}
                      </span>
                    </div>
                    {patient.latestPrediction && (
                      <p className="text-xs text-gray-500">
                        Last: {formatDate(patient.latestPrediction.timestamp)}
                      </p>
                    )}
                  </div>

                  {/* Latest Prediction */}
                  {patient.latestPrediction && (
                    <div className="mb-4 p-3 rounded-lg border-2 border-gray-200 bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <span className={`text-sm font-bold px-2 py-1 rounded border ${getDiseaseColor(latestDisease)}`}>
                          {latestDisease}
                        </span>
                        <span className="text-sm font-semibold text-gray-600">
                          {(latestProb * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {patient.sources.map(source => (
                          <span
                            key={source}
                            className={`text-xs font-semibold px-2 py-1 rounded ${getSourceBadgeColor(source)}`}
                          >
                            {source.toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Diseases Detected */}
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Diseases Detected:</p>
                    <div className="flex flex-wrap gap-1">
                      {patient.diseases.length > 0 ? (
                        patient.diseases.slice(0, 3).map(disease => (
                          <span
                            key={disease}
                            className={`text-xs px-2 py-1 rounded border ${getDiseaseColor(disease)}`}
                          >
                            {disease}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-gray-500">None</span>
                      )}
                      {patient.diseases.length > 3 && (
                        <span className="text-xs text-gray-500 px-2 py-1">
                          +{patient.diseases.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>

                  {/* View Details Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePatientClick(patient.userId);
                    }}
                    className="w-full px-4 py-2 bg-[#7FFF00] text-black rounded-lg hover:bg-[#6ee000] transition-colors font-bold border-2 border-[#222123]"
                  >
                    View Details
                  </button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default DoctorPatients;
