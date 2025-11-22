/**
 * Component to embed Plotly HTML inline in the page
 */

const PlotlyEmbed = ({ htmlContent }) => {
  if (!htmlContent) {
    return (
      <div className="w-full bg-white rounded-lg shadow-lg border-2 border-black p-6">
        <p className="text-gray-600">Explanation visualization not available</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-lg shadow-lg border-2 border-black p-6 overflow-hidden">
      <h3 className="text-2xl font-bold text-gray-900 mb-4">Interactive Risk Indicator Analysis</h3>
      <p className="text-sm text-gray-600 mb-4">
        Interactive visualization showing how each feature contributes to the prediction
      </p>
      <div 
        className="w-full"
        style={{ minHeight: '600px' }}
        dangerouslySetInnerHTML={{ __html: htmlContent }}
      />
    </div>
  );
};

export default PlotlyEmbed;

