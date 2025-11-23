import { useState, useEffect } from 'react';
import { getDashboardStats, getPredictions } from '../../lib/api';
import DiseaseDistributionChart from '../../components/dashboard/DiseaseDistributionChart';
import RiskLevelCard from '../../components/dashboard/RiskLevelCard';
import AbnormalFeaturesCard from '../../components/dashboard/AbnormalFeaturesCard';
import RecentPredictionsList from '../../components/dashboard/RecentPredictionsList';
import FeatureTrendChart from '../../components/dashboard/FeatureTrendChart';
import FeatureComparisonChart from '../../components/dashboard/FeatureComparisonChart';
import RiskTrendChart from '../../components/dashboard/RiskTrendChart';
import FeatureDistributionChart from '../../components/dashboard/FeatureDistributionChart';

const DoctorDashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentPredictions, setRecentPredictions] = useState([]);
  const [allPredictions, setAllPredictions] = useState([]); // For graphs
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedUserId, setSelectedUserId] = useState(null); // null = all patients
  const [allUsers, setAllUsers] = useState([]);
  const [selectedFeature, setSelectedFeature] = useState('Glucose'); // For FeatureDistributionChart

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch all predictions to get unique user IDs
        const allPredictionsForUsers = await getPredictions(null, 1000);
        const uniqueUsers = [...new Set(allPredictionsForUsers.map(p => p.user_id))];
        setAllUsers(uniqueUsers);
        
        // Fetch dashboard stats (all patients or filtered)
        const statsData = await getDashboardStats(selectedUserId);
        setStats(statsData);
        
        // Fetch recent predictions (all patients or filtered)
        const predictionsData = await getPredictions(selectedUserId, 10);
        setRecentPredictions(predictionsData);
        
        // Fetch all predictions for graphs (limit to 100 for performance)
        const allPredictionsData = await getPredictions(selectedUserId, 100);
        setAllPredictions(allPredictionsData);
        
        setError(null);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [selectedUserId]);

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
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-[#222123] mb-2">Doctor Dashboard</h1>
              <p className="text-gray-600">Overview of all patient predictions and health insights</p>
            </div>
            
            {/* Patient Filter */}
            <div className="flex items-center space-x-3">
              <label className="text-sm font-medium text-gray-700">Filter by Patient:</label>
              <select
                value={selectedUserId || 'all'}
                onChange={(e) => setSelectedUserId(e.target.value === 'all' ? null : e.target.value)}
                className="px-4 py-2 border-2 border-[#222123] rounded-lg focus:outline-none focus:border-[#7FFF00] bg-white"
              >
                <option value="all">All Patients</option>
                {allUsers.map(userId => (
                  <option key={userId} value={userId}>
                    {userId.length > 20 ? `${userId.substring(0, 20)}...` : userId}
                  </option>
                ))}
              </select>
            </div>
          </div>
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
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

        {/* Clinician Graphs Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-[#222123] mb-6">Clinician Analysis</h2>
          
          {/* Feature Trends Over Time - Main Clinician Graph */}
          <div className="mb-6">
            <FeatureTrendChart predictions={allPredictions} />
          </div>

          {/* Two Column Grid for Additional Graphs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Feature Comparison */}
            <div>
              <FeatureComparisonChart predictions={allPredictions} />
            </div>

            {/* Risk Trend */}
            <div>
              <RiskTrendChart predictions={allPredictions} />
            </div>
          </div>

          {/* Feature Distribution with Selector */}
          <div className="mb-6">
            <div className="mb-4">
              <label className="text-sm font-medium text-gray-700 mr-3">Select Feature for Distribution:</label>
              <select
                value={selectedFeature}
                onChange={(e) => setSelectedFeature(e.target.value)}
                className="px-4 py-2 border-2 border-[#222123] rounded-lg focus:outline-none focus:border-[#7FFF00] bg-white"
              >
                <option value="Glucose">Glucose</option>
                <option value="Cholesterol">Cholesterol</option>
                <option value="Hemoglobin">Hemoglobin</option>
                <option value="White Blood Cells">White Blood Cells</option>
                <option value="Red Blood Cells">Red Blood Cells</option>
                <option value="Platelets">Platelets</option>
                <option value="BMI">BMI</option>
                <option value="Systolic Blood Pressure">Systolic Blood Pressure</option>
                <option value="Diastolic Blood Pressure">Diastolic Blood Pressure</option>
                <option value="Heart Rate">Heart Rate</option>
                <option value="Insulin">Insulin</option>
                <option value="Triglycerides">Triglycerides</option>
                <option value="HDL Cholesterol">HDL Cholesterol</option>
                <option value="LDL Cholesterol">LDL Cholesterol</option>
                <option value="Creatinine">Creatinine</option>
                <option value="ALT">ALT</option>
                <option value="AST">AST</option>
              </select>
            </div>
            <FeatureDistributionChart 
              predictions={allPredictions} 
              featureName={selectedFeature}
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

export default DoctorDashboard;
