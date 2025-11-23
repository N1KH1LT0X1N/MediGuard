const RecentPredictionsList = ({ predictions, onPredictionClick, showPatientId = false }) => {
  if (!predictions || predictions.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Recent Predictions</h3>
        <p className="text-gray-500 text-center py-8">No predictions available</p>
      </div>
    );
  }

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

  const getSourceBadgeColor = (source) => {
    const colors = {
      manual: 'bg-blue-100 text-blue-800',
      pdf: 'bg-red-100 text-red-800',
      csv: 'bg-green-100 text-green-800',
      image: 'bg-purple-100 text-purple-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const getDiseaseColor = (disease) => {
    const colors = {
      'Anemia': 'text-red-600',
      'Diabetes': 'text-orange-600',
      'Heart Disease': 'text-red-700',
      'Thrombocytopenia': 'text-purple-600',
      'Thalassemia': 'text-blue-600',
      'Healthy': 'text-[#7FFF00]'
    };
    return colors[disease] || 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-4">Recent Predictions</h3>
      <p className="text-sm text-gray-600 mb-6">Your latest prediction analyses</p>
      
      <div className="space-y-3">
        {predictions.map((prediction) => {
          const disease = prediction.prediction_result?.predicted_disease || 'Unknown';
          const probabilities = prediction.prediction_result?.probabilities || {};
          const maxProb = Math.max(...Object.values(probabilities), 0);
          const source = prediction.source || 'manual';

          return (
            <div
              key={prediction.id}
              onClick={() => onPredictionClick && onPredictionClick(prediction)}
              className="p-4 rounded-lg border-2 border-gray-200 hover:border-[#7FFF00] transition-all cursor-pointer hover:shadow-md"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h4 className={`text-lg font-bold ${getDiseaseColor(disease)}`}>
                    {disease}
                  </h4>
                  {showPatientId && prediction.user_id && (
                    <p className="text-xs font-semibold text-gray-700 mt-1">
                      Patient: {prediction.user_id.length > 25 ? `${prediction.user_id.substring(0, 25)}...` : prediction.user_id}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">{formatDate(prediction.timestamp)}</p>
                </div>
                <div className="flex flex-col items-end space-y-1">
                  <span className={`text-xs font-semibold px-2 py-1 rounded ${getSourceBadgeColor(source)}`}>
                    {source.toUpperCase()}
                  </span>
                  <span className="text-sm font-semibold text-gray-600">
                    {(maxProb * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RecentPredictionsList;

