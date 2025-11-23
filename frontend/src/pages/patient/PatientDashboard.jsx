import { useState, useEffect } from 'react';
import { getDashboardStats, getUserPredictions } from '../../lib/api';
import DiseaseDistributionChart from '../../components/dashboard/DiseaseDistributionChart';
import RiskLevelCard from '../../components/dashboard/RiskLevelCard';
import AbnormalFeaturesCard from '../../components/dashboard/AbnormalFeaturesCard';
import RecentPredictionsList from '../../components/dashboard/RecentPredictionsList';

const PatientDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get user ID from sessionStorage
  const getUserId = () => {
    return sessionStorage.getItem('mediguard_user_id') || null;
  };

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        const userId = getUserId();
        
        if (!userId) {
          setError('No user ID found. Please make a prediction first.');
          setLoading(false);
          return;
        }
        
        // Fetch dashboard stats and recent predictions in parallel
        const [statsData, predictionsData] = await Promise.all([
          getDashboardStats(userId),
          getUserPredictions(userId, 10)
        ]);
        
        setStats(statsData);
        setRecentPredictions(predictionsData);
        setError(null);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const handlePredictionClick = (prediction) => {
    // Navigate to prediction details or show modal
    console.log('Prediction clicked:', prediction);
    // TODO: Implement navigation or modal
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#7FFF00] mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#222123] mb-2">Dashboard</h1>
          <p className="text-gray-600">Overview of your prediction history and health insights</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Disease Distribution */}
          <div className="lg:col-span-2">
            <DiseaseDistributionChart diseaseDistribution={stats?.disease_distribution || {}} />
          </div>

          {/* Risk Levels */}
          <div>
            <RiskLevelCard riskLevels={stats?.risk_levels || {}} />
          </div>
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Abnormal Features */}
          <div>
            <AbnormalFeaturesCard abnormalFeatures={stats?.abnormal_features_summary || {}} />
          </div>

          {/* Recent Predictions */}
          <div>
            <RecentPredictionsList
              predictions={recentPredictions}
              onPredictionClick={handlePredictionClick}
            />
          </div>
        </div>

        {/* Summary Card */}
        {stats && (
          <div className="mt-8 bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
            <h3 className="text-xl font-bold text-[#222123] mb-4">Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-3xl font-bold text-[#222123]">{stats.total_predictions}</p>
                <p className="text-sm text-gray-600 mt-1">Total Predictions</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-3xl font-bold text-[#222123]">
                  {Object.keys(stats.disease_distribution || {}).length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Diseases Detected</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <p className="text-3xl font-bold text-[#222123]">
                  {Object.keys(stats.abnormal_features_summary || {}).length}
                </p>
                <p className="text-sm text-gray-600 mt-1">Abnormal Features</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientDashboard;

