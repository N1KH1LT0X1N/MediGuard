const AbnormalFeaturesCard = ({ abnormalFeatures }) => {
  // Convert object to sorted array
  const features = Object.entries(abnormalFeatures || {})
    .map(([name, count]) => ({
      name,
      count
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10); // Top 10

  if (features.length === 0) {
    return (
      <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Abnormal Features</h3>
        <p className="text-gray-500 text-center py-4">No abnormal features detected</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-4">Abnormal Features</h3>
      <p className="text-sm text-gray-600 mb-6">Most frequently abnormal features across predictions</p>
      
      <div className="space-y-3">
        {features.map((feature, index) => (
          <div
            key={feature.name}
            className="flex items-center justify-between p-3 rounded-lg border-2 border-gray-200 hover:border-[#7FFF00] transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-[#222123] text-white flex items-center justify-center font-bold text-sm">
                {index + 1}
              </div>
              <span className="font-medium text-gray-900">{feature.name}</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">{feature.count}</span>
              <span className="text-xs text-gray-400">occurrences</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AbnormalFeaturesCard;

