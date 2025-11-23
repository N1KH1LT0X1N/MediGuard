import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#7FFF00', '#e74c3c', '#3498db', '#f39c12', '#9b59b6', '#1abc9c'];

const DiseaseDistributionChart = ({ diseaseDistribution }) => {
  // Convert object to array for chart
  const data = Object.entries(diseaseDistribution || {})
    .map(([name, value]) => ({
      name,
      value
    }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Disease Distribution</h3>
        <p className="text-gray-500 text-center py-8">No prediction data available</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-4">Disease Distribution</h3>
      <p className="text-sm text-gray-600 mb-6">Distribution of predicted diseases across all analyses</p>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #222123',
              borderRadius: '8px',
            }}
            formatter={(value) => [value, 'Predictions']}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DiseaseDistributionChart;

