import { useState, useEffect } from 'react';

const ScalingLayerVisualization = () => {
  const [selectedFeature, setSelectedFeature] = useState('Glucose');
  const [rawValue, setRawValue] = useState(120);
  const [animationStep, setAnimationStep] = useState(0);
  const [showCalculation, setShowCalculation] = useState(false);
  const [sensitivityDelta, setSensitivityDelta] = useState(1);

  // Inferred ranges (from the scaling layer)
  const featureRanges = {
    'Glucose': { min: 39.09, max: 231.86, unit: 'mg/dL', clinical: { min: 70, max: 200 } },
    'Cholesterol': { min: 52.73, max: 344.59, unit: 'mg/dL', clinical: { min: 100, max: 300 } },
    'Hemoglobin': { min: 10.58, max: 19.45, unit: 'g/dL', clinical: { min: 12, max: 18 } },
    'Platelets': { min: 84000, max: 516000, unit: 'cells/μL', clinical: { min: 150000, max: 450000 } },
    'White Blood Cells': { min: 2350, max: 12651, unit: 'cells/μL', clinical: { min: 4000, max: 11000 } },
    'BMI': { min: 9.40, max: 46.04, unit: 'kg/m²', clinical: { min: 15, max: 40 } },
    'Systolic Blood Pressure': { min: 69.85, max: 201.77, unit: 'mmHg', clinical: { min: 90, max: 180 } },
    'Diastolic Blood Pressure': { min: 51.09, max: 109.41, unit: 'mmHg', clinical: { min: 60, max: 100 } },
  };

  const currentRange = featureRanges[selectedFeature];
  const scaledValue = currentRange 
    ? ((rawValue - currentRange.min) / (currentRange.max - currentRange.min))
    : 0;
  const clippedValue = Math.max(0, Math.min(1, scaledValue));

  // Sensitivity calculations
  const baseScaled = currentRange ? (rawValue - currentRange.min) / (currentRange.max - currentRange.min) : 0;
  const changedValue = rawValue + sensitivityDelta;
  const changedScaled = currentRange ? (changedValue - currentRange.min) / (currentRange.max - currentRange.min) : 0;
  const scaledDifference = changedScaled - baseScaled;
  const sensitivityRatio = currentRange ? scaledDifference / sensitivityDelta : 0;

  useEffect(() => {
    setAnimationStep(0);
    setShowCalculation(false);
  }, [selectedFeature, rawValue]);

  const startAnimation = () => {
    setAnimationStep(1);
    setTimeout(() => setAnimationStep(2), 1000);
    setTimeout(() => setAnimationStep(3), 2000);
    setTimeout(() => setAnimationStep(4), 3000);
    setTimeout(() => {
      setAnimationStep(5);
      setShowCalculation(true);
    }, 4000);
  };

  const formatValue = (val) => {
    if (val >= 1000) return val.toFixed(0);
    if (val >= 100) return val.toFixed(1);
    if (val >= 10) return val.toFixed(2);
    return val.toFixed(2);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 animate-fadeIn">
          <h1 className="text-4xl font-bold text-[#222123] mb-2">Scaling Layer Architecture</h1>
          <p className="text-gray-600 text-lg">Understanding how raw clinical values transform into model-ready inputs</p>
        </div>

        {/* Interactive Demo Section */}
        <div className="bg-white rounded-xl p-8 border-2 border-[#222123] shadow-lg mb-8 animate-fadeIn">
          <h2 className="text-2xl font-bold text-[#222123] mb-6">Interactive Scaling Demo</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Feature Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Feature:</label>
              <select
                value={selectedFeature}
                onChange={(e) => setSelectedFeature(e.target.value)}
                className="w-full px-4 py-2 border-2 border-[#222123] rounded-lg focus:outline-none focus:border-[#7FFF00] bg-white"
              >
                {Object.keys(featureRanges).map(feature => (
                  <option key={feature} value={feature}>{feature}</option>
                ))}
              </select>
            </div>

            {/* Raw Value Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Raw Value ({currentRange?.unit}):
              </label>
              <input
                type="number"
                value={rawValue}
                onChange={(e) => setRawValue(parseFloat(e.target.value) || 0)}
                min={currentRange?.min}
                max={currentRange?.max}
                step="0.1"
                className="w-full px-4 py-2 border-2 border-[#222123] rounded-lg focus:outline-none focus:border-[#7FFF00]"
              />
            </div>
          </div>

          <button
            onClick={startAnimation}
            className="px-6 py-3 bg-[#7FFF00] text-black rounded-lg hover:bg-[#6ee000] transition-colors font-bold border-2 border-[#222123] mb-6"
          >
            Animate Transformation
          </button>

          {/* Transformation Flow */}
          <div className="space-y-4">
            {/* Step 1: Raw Value */}
            <div className={`bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-6 border-2 ${animationStep >= 1 ? 'border-blue-500' : 'border-blue-200 opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-blue-900 mb-2">Step 1: Raw Clinical Value</h3>
                  <p className="text-blue-800">
                    <span className="text-2xl font-bold">{formatValue(rawValue)}</span> {currentRange?.unit}
                  </p>
                </div>
                <div className="text-4xl">📊</div>
              </div>
            </div>

            {/* Step 2: Range Lookup */}
            <div className={`bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-6 border-2 ${animationStep >= 2 ? 'border-purple-500' : 'border-purple-200 opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-purple-900 mb-2">Step 2: Range Lookup</h3>
                  <p className="text-purple-800">
                    Min: <span className="font-bold">{formatValue(currentRange?.min)}</span> | 
                    Max: <span className="font-bold">{formatValue(currentRange?.max)}</span> {currentRange?.unit}
                  </p>
                  <p className="text-sm text-purple-700 mt-1">
                    (Inferred from training data + 10% safety margin)
                  </p>
                </div>
                <div className="text-4xl">🔍</div>
              </div>
            </div>

            {/* Step 3: Min-Max Scaling */}
            <div className={`bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-6 border-2 ${animationStep >= 3 ? 'border-green-500' : 'border-green-200 opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-green-900 mb-2">Step 3: Min-Max Scaling</h3>
                  {showCalculation && (
                    <div className="text-green-800 font-mono text-sm">
                      <p className="mb-1">
                        scaled = (raw - min) / (max - min)
                      </p>
                      <p className="mb-1">
                        scaled = ({formatValue(rawValue)} - {formatValue(currentRange?.min)}) / ({formatValue(currentRange?.max)} - {formatValue(currentRange?.min)})
                      </p>
                      <p className="text-lg font-bold">
                        scaled = {scaledValue.toFixed(4)}
                      </p>
                    </div>
                  )}
                </div>
                <div className="text-4xl">⚙️</div>
              </div>
            </div>

            {/* Step 4: Clipping */}
            <div className={`bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg p-6 border-2 ${animationStep >= 4 ? 'border-yellow-500' : 'border-yellow-200 opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-yellow-900 mb-2">Step 4: Clipping to [0, 1]</h3>
                  <p className="text-yellow-800">
                    Final Scaled Value: <span className="text-2xl font-bold">{clippedValue.toFixed(4)}</span>
                  </p>
                </div>
                <div className="text-4xl">✂️</div>
              </div>
            </div>

            {/* Step 5: Model Ready */}
            <div className={`bg-gradient-to-r from-[#7FFF00] to-[#6ee000] rounded-lg p-6 border-2 border-[#222123] ${animationStep >= 5 ? 'opacity-100' : 'opacity-50'}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-[#222123] mb-2">Step 5: Model-Ready Input</h3>
                  <p className="text-[#222123]">
                    <span className="text-2xl font-bold">{clippedValue.toFixed(4)}</span> (in [0, 1] range)
                  </p>
                </div>
                <div className="text-4xl">✅</div>
              </div>
            </div>
          </div>
        </div>

        {/* Architecture Diagram */}
        <div className="bg-white rounded-xl p-8 border-2 border-[#222123] shadow-lg mb-8 animate-fadeIn">
          <h2 className="text-2xl font-bold text-[#222123] mb-6">Scaling Layer Architecture</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-500 text-white rounded-lg p-6 text-center border-2 border-[#222123] hover:scale-105 transition-transform">
              <div className="text-4xl mb-2">📥</div>
              <h3 className="font-bold mb-2">Raw Input</h3>
              <p className="text-sm">Clinical Values</p>
            </div>

            <div className="bg-purple-500 text-white rounded-lg p-6 text-center border-2 border-[#222123] hover:scale-105 transition-transform">
              <div className="text-4xl mb-2">🔍</div>
              <h3 className="font-bold mb-2">Range Lookup</h3>
              <p className="text-sm">Inferred Ranges</p>
            </div>

            <div className="bg-green-500 text-white rounded-lg p-6 text-center border-2 border-[#222123] hover:scale-105 transition-transform">
              <div className="text-4xl mb-2">⚙️</div>
              <h3 className="font-bold mb-2">Min-Max Scale</h3>
              <p className="text-sm">Normalization</p>
            </div>

            <div className="bg-[#7FFF00] text-[#222123] rounded-lg p-6 text-center border-2 border-[#222123] hover:scale-105 transition-transform">
              <div className="text-4xl mb-2">✅</div>
              <h3 className="font-bold mb-2">Scaled Array</h3>
              <p className="text-sm">[0, 1] Range</p>
            </div>
          </div>

          <div className="text-center">
            <div className="inline-block bg-[#222123] text-white rounded-lg p-6 border-2 border-[#7FFF00]">
              <div className="text-4xl mb-2">🤖</div>
              <h3 className="font-bold text-xl mb-2">ML Model Input</h3>
              <p className="text-sm">24 Features Array</p>
            </div>
          </div>
        </div>

        {/* Key Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-bold text-[#222123] mb-2">Data-Driven Ranges</h3>
            <p className="text-gray-600">
              Ranges inferred from actual training data distribution, not just clinical references
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-4xl mb-4">🛡️</div>
            <h3 className="text-xl font-bold text-[#222123] mb-2">10% Safety Margin</h3>
            <p className="text-gray-600">
              Extended ranges provide buffer for edge cases and outliers
            </p>
          </div>

          <div className="bg-white rounded-xl p-6 border-2 border-[#222123] shadow-lg animate-fadeIn">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-bold text-[#222123] mb-2">Real-Time Scaling</h3>
            <p className="text-gray-600">
              Instant transformation from raw clinical values to model-ready format
            </p>
          </div>
        </div>

        {/* Formula Card */}
        <div className="bg-gradient-to-br from-[#7FFF00] to-[#6ee000] rounded-xl p-8 border-2 border-[#222123] shadow-lg mb-8 animate-fadeIn">
          <h2 className="text-2xl font-bold text-[#222123] mb-4">The Scaling Formula</h2>
          <div className="bg-white rounded-lg p-6 border-2 border-[#222123]">
            <div className="text-center">
              <div className="text-4xl font-bold text-[#222123] mb-4 font-mono">
                scaled = (raw - min) / (max - min)
              </div>
              <div className="text-gray-600 space-y-2">
                <p><strong>raw:</strong> Raw clinical value (e.g., 120 mg/dL)</p>
                <p><strong>min:</strong> Minimum value from inferred range</p>
                <p><strong>max:</strong> Maximum value from inferred range</p>
                <p><strong>scaled:</strong> Result in [0, 1] range</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sensitivity Preservation Section */}
        <div className="bg-white rounded-xl p-8 border-2 border-[#222123] shadow-lg mb-8 animate-fadeIn">
          <h2 className="text-3xl font-bold text-[#222123] mb-6">🎯 Sensitivity Preservation</h2>
          <p className="text-gray-600 text-lg mb-6">
            How does the scaling layer account for small sensitivity changes? The linear transformation preserves relative differences, ensuring that even minute clinical variations are accurately represented.
          </p>

          {/* Key Principles */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-blue-50 rounded-lg p-6 border-2 border-blue-300">
              <div className="text-4xl mb-3">📏</div>
              <h3 className="text-xl font-bold text-blue-900 mb-2">Linear Preservation</h3>
              <p className="text-blue-800 text-sm">
                The min-max formula is a <strong>linear transformation</strong>, meaning small changes in raw values translate proportionally to scaled values. A 1 mg/dL change always produces the same scaled difference.
              </p>
            </div>

            <div className="bg-purple-50 rounded-lg p-6 border-2 border-purple-300">
              <div className="text-4xl mb-3">🔬</div>
              <h3 className="text-xl font-bold text-purple-900 mb-2">High Precision</h3>
              <p className="text-purple-800 text-sm">
                Uses <strong>floating-point arithmetic</strong> with 4-6 decimal precision. No quantization or rounding - every decimal place is preserved through the transformation.
              </p>
            </div>

            <div className="bg-green-50 rounded-lg p-6 border-2 border-green-300">
              <div className="text-4xl mb-3">⚖️</div>
              <h3 className="text-xl font-bold text-green-900 mb-2">Proportional Sensitivity</h3>
              <p className="text-green-800 text-sm">
                Sensitivity is <strong>range-dependent</strong>. Smaller ranges = higher sensitivity. A 1 unit change in a narrow range (e.g., Creatinine) has more impact than in a wide range (e.g., Platelets).
              </p>
            </div>
          </div>

          {/* Interactive Sensitivity Demo */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-6 border-2 border-[#222123] mb-6">
            <h3 className="text-xl font-bold text-[#222123] mb-4">Interactive Sensitivity Demonstration</h3>
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium text-gray-700">Change in Raw Value:</label>
                <input
                  type="number"
                  value={sensitivityDelta}
                  onChange={(e) => setSensitivityDelta(parseFloat(e.target.value) || 0)}
                  step="0.1"
                  className="px-3 py-1 border-2 border-[#222123] rounded"
                />
                <span className="text-sm text-gray-600">{currentRange?.unit}</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded p-4 border-2 border-blue-300">
                  <p className="text-sm font-bold text-blue-900 mb-2">Base Value</p>
                  <p className="text-lg">Raw: {rawValue.toFixed(2)} {currentRange?.unit}</p>
                  <p className="text-lg">Scaled: {baseScaled.toFixed(6)}</p>
                </div>

                <div className="bg-white rounded p-4 border-2 border-green-300">
                  <p className="text-sm font-bold text-green-900 mb-2">Changed Value</p>
                  <p className="text-lg">Raw: {changedValue.toFixed(2)} {currentRange?.unit}</p>
                  <p className="text-lg">Scaled: {changedScaled.toFixed(6)}</p>
                </div>
              </div>

              <div className="bg-[#7FFF00] rounded p-4 border-2 border-[#222123]">
                <p className="text-sm font-bold text-[#222123] mb-2">Sensitivity Analysis</p>
                <p className="text-sm text-[#222123]">
                  Raw Change: <strong>{sensitivityDelta > 0 ? '+' : ''}{sensitivityDelta.toFixed(2)}</strong> {currentRange?.unit}
                </p>
                <p className="text-sm text-[#222123]">
                  Scaled Change: <strong>{scaledDifference > 0 ? '+' : ''}{scaledDifference.toFixed(6)}</strong>
                </p>
                <p className="text-sm text-[#222123] mt-2">
                  Sensitivity Ratio: <strong>{(sensitivityRatio * 100).toFixed(4)}%</strong> (scaled change per unit raw change)
                </p>
                <p className="text-xs text-gray-700 mt-2">
                  This demonstrates that even small changes ({sensitivityDelta} {currentRange?.unit}) are preserved proportionally in the scaled space!
                </p>
              </div>
            </div>
          </div>

          {/* Mathematical Proof */}
          <div className="bg-yellow-50 rounded-lg p-6 border-2 border-yellow-300">
            <h3 className="text-xl font-bold text-yellow-900 mb-4">Mathematical Proof of Sensitivity Preservation</h3>
            <div className="space-y-4 text-yellow-800">
              <div className="bg-white rounded p-4 border border-yellow-200">
                <p className="font-mono text-sm mb-2">
                  <strong>Given:</strong> Two raw values v₁ and v₂ where v₂ = v₁ + Δ
                </p>
                <p className="font-mono text-sm mb-2">
                  <strong>Scaled values:</strong>
                </p>
                <p className="font-mono text-sm mb-2 ml-4">
                  s₁ = (v₁ - min) / (max - min)
                </p>
                <p className="font-mono text-sm mb-2 ml-4">
                  s₂ = (v₂ - min) / (max - min) = ((v₁ + Δ) - min) / (max - min)
                </p>
                <p className="font-mono text-sm mb-2">
                  <strong>Difference:</strong>
                </p>
                <p className="font-mono text-sm mb-2 ml-4">
                  s₂ - s₁ = Δ / (max - min)
                </p>
                <p className="font-mono text-sm">
                  <strong>Conclusion:</strong> The scaled difference is <strong>proportional</strong> to the raw difference, scaled by the range span. This means sensitivity is preserved!
                </p>
              </div>
            </div>
          </div>

          {/* Real-World Example */}
          <div className="mt-6 bg-indigo-50 rounded-lg p-6 border-2 border-indigo-300">
            <h3 className="text-xl font-bold text-indigo-900 mb-4">Real-World Example: Glucose Sensitivity</h3>
            <div className="space-y-3 text-indigo-800">
              <p className="text-sm">
                <strong>Scenario:</strong> Two patients with slightly different glucose levels
              </p>
              <div className="bg-white rounded p-4 border border-indigo-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="font-bold mb-2">Patient A:</p>
                    <p>Raw: 120.0 mg/dL</p>
                    <p>Scaled: {((120.0 - 39.09) / (231.86 - 39.09)).toFixed(6)}</p>
                  </div>
                  <div>
                    <p className="font-bold mb-2">Patient B:</p>
                    <p>Raw: 120.5 mg/dL (0.5 mg/dL difference)</p>
                    <p>Scaled: {((120.5 - 39.09) / (231.86 - 39.09)).toFixed(6)}</p>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-indigo-200">
                  <p className="font-bold">
                    Scaled Difference: {(((120.5 - 39.09) / (231.86 - 39.09)) - ((120.0 - 39.09) / (231.86 - 39.09))).toFixed(6)}
                  </p>
                  <p className="text-xs mt-1">
                    This 0.5 mg/dL difference is preserved as a {(((120.5 - 39.09) / (231.86 - 39.09)) - ((120.0 - 39.09) / (231.86 - 39.09))).toFixed(6)} difference in scaled space - 
                    the model can detect this subtle variation!
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScalingLayerVisualization;
