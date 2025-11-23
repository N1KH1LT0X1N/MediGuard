const RiskLevelCard = ({ riskLevels }) => {
  const { high = 0, medium = 0, low = 0 } = riskLevels || {};
  const total = high + medium + low;

  if (total === 0) {
    return (
      <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Risk Levels</h3>
        <p className="text-gray-500 text-center py-4">No prediction data available</p>
      </div>
    );
  }

  const highPercent = total > 0 ? ((high / total) * 100).toFixed(1) : 0;
  const mediumPercent = total > 0 ? ((medium / total) * 100).toFixed(1) : 0;
  const lowPercent = total > 0 ? ((low / total) * 100).toFixed(1) : 0;

  return (
    <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-4">Risk Levels</h3>
      <p className="text-sm text-gray-600 mb-6">Distribution of prediction confidence levels</p>
      
      <div className="space-y-4">
        {/* High Risk */}
        <div className="flex items-center justify-between p-4 rounded-lg border-2 border-red-200 bg-red-50">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 rounded-full bg-red-600"></div>
            <span className="font-semibold text-gray-900">High Risk</span>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-red-600">{high}</p>
            <p className="text-xs text-gray-500">{highPercent}%</p>
          </div>
        </div>

        {/* Medium Risk */}
        <div className="flex items-center justify-between p-4 rounded-lg border-2 border-orange-200 bg-orange-50">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span className="font-semibold text-gray-900">Medium Risk</span>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-orange-600">{medium}</p>
            <p className="text-xs text-gray-500">{mediumPercent}%</p>
          </div>
        </div>

        {/* Low Risk */}
        <div className="flex items-center justify-between p-4 rounded-lg border-2 border-[#7FFF00] bg-green-50">
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 rounded-full bg-[#7FFF00]"></div>
            <span className="font-semibold text-gray-900">Low Risk</span>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-[#7FFF00]">{low}</p>
            <p className="text-xs text-gray-500">{lowPercent}%</p>
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t-2 border-gray-200">
        <p className="text-sm text-gray-600 text-center">
          Total Predictions: <span className="font-bold text-[#222123]">{total}</span>
        </p>
      </div>
    </div>
  );
};

export default RiskLevelCard;

