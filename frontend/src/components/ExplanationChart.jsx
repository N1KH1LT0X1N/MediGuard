import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ExplanationChart = ({ featureImportance }) => {
  // Convert feature importance object to array for Recharts
  const data = Object.entries(featureImportance || {})
    .map(([name, value]) => ({
      name,
      importance: value,
      color: value >= 0 ? '#e74c3c' : '#7FFF00', // Red for positive, theme green for negative (protective)
    }))
    .sort((a, b) => Math.abs(b.importance) - Math.abs(a.importance)) // Sort by absolute importance
    .slice(0, 15); // Show top 15 features

  return (
    <div className="w-full bg-white rounded-lg shadow-lg border-2 border-black p-6">
      <h3 className="text-2xl font-bold text-gray-900 mb-4">Feature Importance Analysis</h3>
      <p className="text-sm text-gray-600 mb-4">
        Features contributing most to the prediction (positive = risk, negative = protective)
      </p>
      <ResponsiveContainer width="100%" height={500}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            type="number" 
            label={{ value: 'Contribution Score', position: 'insideBottom', offset: -5 }}
            tick={{ fill: '#523122' }}
          />
          <YAxis 
            type="category" 
            dataKey="name" 
            width={180}
            tick={{ fill: '#523122', fontSize: 12 }}
            angle={0}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #523122',
              borderRadius: '8px',
            }}
            formatter={(value) => [value.toFixed(4), 'Contribution']}
          />
          <Bar 
            dataKey="importance" 
            radius={[0, 8, 8, 0]}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ExplanationChart;

