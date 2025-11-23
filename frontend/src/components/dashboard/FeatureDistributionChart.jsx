import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const FeatureDistributionChart = ({ predictions, featureName, showPatientNames = false }) => {
  // Process data: create histogram bins for the selected feature
  const processData = () => {
    if (!predictions || !featureName || predictions.length === 0) return [];

    // Extract all values for this feature
    const values = predictions
      .map(p => p.input_features?.[featureName])
      .filter(v => v !== null && v !== undefined && !isNaN(v))
      .map(v => parseFloat(v));

    if (values.length === 0) return [];

    // Create bins (20 bins for smoother distribution)
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Handle edge case where all values are the same
    if (min === max) {
      const formatValue = (val) => {
        if (val >= 1000) return val.toFixed(0);
        if (val >= 100) return val.toFixed(1);
        if (val >= 10) return val.toFixed(2);
        return val.toFixed(2);
      };
      return [{
        value: formatValue(min),
        valueNum: min,
        range: formatValue(min),
        min: min,
        max: max,
        count: values.length
      }];
    }
    
    // Use fewer bins for cleaner visualization (10-15 bins)
    const numBins = Math.min(15, Math.max(5, Math.floor(Math.sqrt(values.length))));
    const binSize = (max - min) / numBins;
    const bins = Array(numBins).fill(0).map((_, i) => {
      const binMin = min + i * binSize;
      const binMax = min + (i + 1) * binSize;
      const binCenter = (binMin + binMax) / 2;
      
      // Format value based on range
      const formatValue = (val) => {
        if (val >= 1000) return val.toFixed(0);
        if (val >= 100) return val.toFixed(1);
        if (val >= 10) return val.toFixed(2);
        return val.toFixed(2);
      };
      
      return {
        value: formatValue(binCenter),
        valueNum: binCenter,
        range: `${formatValue(binMin)} - ${formatValue(binMax)}`,
        min: binMin,
        max: binMax,
        count: 0
      };
    });

    // Count values in each bin and track patient names if needed
    if (showPatientNames) {
      // Map each prediction to its value for patient tracking
      predictions.forEach(pred => {
        const val = pred.input_features?.[featureName];
        if (val !== null && val !== undefined && !isNaN(val)) {
          const parsedVal = parseFloat(val);
          let binIndex = Math.floor((parsedVal - min) / binSize);
          if (parsedVal >= max) {
            binIndex = numBins - 1;
          } else if (binIndex >= numBins) {
            binIndex = numBins - 1;
          } else if (binIndex < 0) {
            binIndex = 0;
          }
          
          if (bins[binIndex]) {
            bins[binIndex].count++;
            if (!bins[binIndex].patientNames) {
              bins[binIndex].patientNames = [];
            }
            if (pred.user_id && !bins[binIndex].patientNames.includes(pred.user_id)) {
              bins[binIndex].patientNames.push(pred.user_id);
            }
          }
        }
      });
    } else {
      // Original counting logic (faster when not tracking patients)
      values.forEach(value => {
        let binIndex = Math.floor((value - min) / binSize);
        if (value >= max) {
          binIndex = numBins - 1;
        } else if (binIndex >= numBins) {
          binIndex = numBins - 1;
        } else if (binIndex < 0) {
          binIndex = 0;
        }
        
        if (bins[binIndex]) {
          bins[binIndex].count++;
        }
      });
    }

    return bins;
  };

  const data = processData();

  if (data.length === 0) {
    return (
      <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg">
        <h3 className="text-xl font-bold text-[#222123] mb-4">Feature Distribution</h3>
        <p className="text-gray-500 text-center py-8">
          {featureName ? `No data available for ${featureName}` : 'Select a feature to view distribution'}
        </p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
      <h3 className="text-xl font-bold text-[#222123] mb-2">Feature Distribution</h3>
      <p className="text-sm text-gray-600 mb-2">{featureName}</p>
      <p className="text-xs text-gray-500 mb-6">Distribution of values across all predictions</p>
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" opacity={0.5} />
          <XAxis 
            dataKey="value" 
            stroke="#222123"
            style={{ fontSize: '11px', fontWeight: '500' }}
            tick={{ fill: '#222123' }}
            label={{ 
              value: 'Value Range', 
              position: 'insideBottom', 
              offset: -10,
              style: { fill: '#222123', fontWeight: 'bold' }
            }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            stroke="#222123"
            style={{ fontSize: '12px', fontWeight: '500' }}
            tick={{ fill: '#222123' }}
            label={{ 
              value: 'Frequency', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#222123', fontWeight: 'bold' }
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '2px solid #222123',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            }}
            formatter={(value) => [`${value} occurrence${value !== 1 ? 's' : ''}`, 'Count']}
            labelFormatter={(label, payload) => {
              if (payload && payload[0] && payload[0].payload) {
                const range = payload[0].payload.range;
                if (showPatientNames && payload[0].payload.patientNames) {
                  const patientList = payload[0].payload.patientNames.slice(0, 3).join(', ');
                  const more = payload[0].payload.patientNames.length > 3 
                    ? ` (+${payload[0].payload.patientNames.length - 3} more)` 
                    : '';
                  return `Range: ${range}${patientList ? ` - Patients: ${patientList}${more}` : ''}`;
                }
                return `Range: ${range}`;
              }
              return `Value: ${label}`;
            }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#7FFF00"
            strokeWidth={3}
            dot={{ fill: '#7FFF00', r: 4, strokeWidth: 2, stroke: '#222123' }}
            activeDot={{ r: 6, fill: '#6ee000', stroke: '#222123', strokeWidth: 2 }}
            name="Frequency"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FeatureDistributionChart;

