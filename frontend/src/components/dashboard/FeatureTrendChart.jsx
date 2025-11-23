import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const FeatureTrendChart = ({ predictions, showPatientNames = false }) => {
  // Key features to track (clinically important)
  const keyFeatures = [
    'Glucose',
    'Cholesterol',
    'Hemoglobin',
    'White Blood Cells',
    'Red Blood Cells',
    'Platelets',
    'BMI',
    'Systolic Blood Pressure',
    'Diastolic Blood Pressure',
    'Heart Rate'
  ];

  // Process predictions to create time series data
  const processData = () => {
    if (!predictions || predictions.length === 0) return [];

    // Sort by timestamp
    const sorted = [...predictions].sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    );

    // Create data points for each prediction
    return sorted.map((pred, index) => {
      const dataPoint = {
        index: index + 1,
        date: new Date(pred.timestamp).toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        }),
        timestamp: pred.timestamp,
        patientName: showPatientNames && pred.user_id 
          ? (pred.user_id.length > 20 ? `${pred.user_id.substring(0, 20)}...` : pred.user_id)
          : null
      };

      // Add feature values
      if (pred.input_features) {
        keyFeatures.forEach(feature => {
          const value = pred.input_features[feature];
          if (value !== null && value !== undefined) {
            dataPoint[feature] = parseFloat(value);
          }
        });
      }

      return dataPoint;
    });
  };

  const data = processData();

  // Colors for each feature
  const colors = [
    '#7FFF00', // Lime green (theme)
    '#e74c3c', // Red
    '#3498db', // Blue
    '#f39c12', // Orange
    '#9b59b6', // Purple
    '#1abc9c', // Teal
    '#e67e22', // Dark orange
    '#34495e', // Dark gray
    '#16a085', // Green
    '#c0392b'  // Dark red
  ];

  if (data.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Feature Trends Over Time</h3>
        <p className="text-gray-500 text-center py-8">No prediction data available</p>
      </div>
    );
  }

  // Get features that have data
  const availableFeatures = keyFeatures.filter(feature => 
    data.some(d => d[feature] !== undefined)
  );

  if (availableFeatures.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Feature Trends Over Time</h3>
        <p className="text-gray-500 text-center py-8">No feature data available</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-2">Feature Trends Over Time</h3>
      <p className="text-sm text-gray-600 mb-6">Track how key clinical parameters change across your analyses</p>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="date" 
            stroke="#222123"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#222123"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #222123',
              borderRadius: '8px',
            }}
            formatter={(value, name) => [value?.toFixed(2) || 'N/A', name]}
            labelFormatter={(label, payload) => {
              if (payload && payload[0] && payload[0].payload) {
                const patientName = payload[0].payload.patientName;
                if (patientName) {
                  return `${label} - Patient: ${patientName}`;
                }
              }
              return label;
            }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          {availableFeatures.map((feature, index) => (
            <Line
              key={feature}
              type="monotone"
              dataKey={feature}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              dot={{ r: 4, fill: colors[index % colors.length] }}
              activeDot={{ r: 6 }}
              name={feature}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureTrendChart;

