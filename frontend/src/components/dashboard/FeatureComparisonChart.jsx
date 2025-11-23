import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

const FeatureComparisonChart = ({ predictions, selectedFeatures = [], showPatientNames = false }) => {
  // Default features to show if none selected
  const defaultFeatures = [
    'Glucose',
    'Cholesterol',
    'Hemoglobin',
    'White Blood Cells',
    'BMI',
    'Systolic Blood Pressure'
  ];

  const featuresToShow = selectedFeatures.length > 0 ? selectedFeatures : defaultFeatures;

  // Process data: get average values for each feature across predictions
  const processData = () => {
    if (!predictions || predictions.length === 0) return [];

    const featureStats = {};

    featuresToShow.forEach(feature => {
      const values = predictions
        .map(p => p.input_features?.[feature])
        .filter(v => v !== null && v !== undefined && !isNaN(v))
        .map(v => parseFloat(v));

      if (values.length > 0) {
        const avg = values.reduce((a, b) => a + b, 0) / values.length;
        const min = Math.min(...values);
        const max = Math.max(...values);
        const latest = values[values.length - 1]; // Most recent value

        featureStats[feature] = {
          name: feature,
          average: parseFloat(avg.toFixed(2)),
          minimum: parseFloat(min.toFixed(2)),
          maximum: parseFloat(max.toFixed(2)),
          latest: parseFloat(latest.toFixed(2))
        };
      }
    });

    return Object.values(featureStats);
  };

  const data = processData();

  if (data.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Feature Comparison</h3>
        <p className="text-gray-500 text-center py-8">No feature data available</p>
      </div>
    );
  }

  // Color based on value (green for normal, red for high, blue for low)
  const getColor = (feature, value) => {
    // Simplified color logic - can be enhanced with normal ranges
    if (feature.includes('Glucose') || feature.includes('Cholesterol')) {
      return value > 200 ? '#e74c3c' : value > 150 ? '#f39c12' : '#7FFF00';
    }
    if (feature.includes('Hemoglobin')) {
      return value < 12 ? '#e74c3c' : value < 14 ? '#f39c12' : '#7FFF00';
    }
    if (feature.includes('BMI')) {
      return value > 30 ? '#e74c3c' : value > 25 ? '#f39c12' : '#7FFF00';
    }
    return '#3498db';
  };

  return (
    <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-2">Feature Comparison</h3>
      <p className="text-sm text-gray-600 mb-6">Average values of key clinical parameters across all analyses</p>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="name" 
            stroke="#222123"
            angle={-45}
            textAnchor="end"
            height={100}
            style={{ fontSize: '11px' }}
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
            formatter={(value, name) => {
              if (name === 'average') return [value, 'Average'];
              if (name === 'latest') return [value, 'Latest'];
              if (name === 'minimum') return [value, 'Minimum'];
              if (name === 'maximum') return [value, 'Maximum'];
              return [value, name];
            }}
            labelFormatter={(label, payload) => {
              if (showPatientNames && payload && payload[0] && payload[0].payload) {
                // For bar charts, we show patient info if available
                const patientInfo = payload[0].payload.patientInfo;
                if (patientInfo) {
                  return `${label} - ${patientInfo}`;
                }
              }
              return label;
            }}
          />
          <Legend />
          <Bar dataKey="average" name="Average Value" fill="#7FFF00" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.name, entry.average)} />
            ))}
          </Bar>
          <Bar dataKey="latest" name="Latest Value" fill="#3498db" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureComparisonChart;

