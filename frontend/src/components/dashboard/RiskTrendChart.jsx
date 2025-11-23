import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';

const RiskTrendChart = ({ predictions, showPatientNames = false }) => {
  // Process predictions to show disease probability trends
  const processData = () => {
    if (!predictions || predictions.length === 0) return [];

    // Sort by timestamp
    const sorted = [...predictions].sort((a, b) => 
      new Date(a.timestamp) - new Date(b.timestamp)
    );

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

      // Extract probabilities from prediction_result
      if (pred.prediction_result?.probabilities) {
        const probs = pred.prediction_result.probabilities;
        Object.keys(probs).forEach(disease => {
          dataPoint[disease] = parseFloat((probs[disease] * 100).toFixed(2));
        });
      }

      // Add predicted disease probability
      if (pred.prediction_result?.predicted_disease) {
        const predicted = pred.prediction_result.predicted_disease;
        if (pred.prediction_result.probabilities?.[predicted]) {
          dataPoint['Predicted Disease'] = parseFloat(
            (pred.prediction_result.probabilities[predicted] * 100).toFixed(2)
          );
        }
      }

      return dataPoint;
    });
  };

  const data = processData();

  // Get all unique diseases from predictions
  const getAllDiseases = () => {
    const diseases = new Set();
    predictions?.forEach(pred => {
      if (pred.prediction_result?.probabilities) {
        Object.keys(pred.prediction_result.probabilities).forEach(d => diseases.add(d));
      }
    });
    return Array.from(diseases);
  };

  const diseases = getAllDiseases();
  const colors = ['#7FFF00', '#e74c3c', '#3498db', '#f39c12', '#9b59b6', '#1abc9c', '#e67e22'];

  if (data.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Risk Trend Analysis</h3>
        <p className="text-gray-500 text-center py-8">No prediction data available</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-2">Risk Trend Analysis</h3>
      <p className="text-sm text-gray-600 mb-6">Disease probability trends over time</p>
      <ResponsiveContainer width="100%" height={350}>
        <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <defs>
            {diseases.map((disease, index) => (
              <linearGradient key={disease} id={`color${index}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors[index % colors.length]} stopOpacity={0.8}/>
                <stop offset="95%" stopColor={colors[index % colors.length]} stopOpacity={0.1}/>
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
          <XAxis 
            dataKey="date" 
            stroke="#222123"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#222123"
            style={{ fontSize: '12px' }}
            label={{ value: 'Probability (%)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #222123',
              borderRadius: '8px',
            }}
            formatter={(value) => [`${value}%`, 'Probability']}
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
          <Legend />
          {diseases.map((disease, index) => (
            <Area
              key={disease}
              type="monotone"
              dataKey={disease}
              stroke={colors[index % colors.length]}
              strokeWidth={2}
              fill={`url(#color${index})`}
              name={disease}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskTrendChart;

