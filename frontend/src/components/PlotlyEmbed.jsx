/**
 * Component to embed Plotly HTML inline in the page using iframe for CSP compliance
 */

const PlotlyEmbed = ({ htmlContent }) => {
  if (!htmlContent) {
    return (
      <div className="w-full bg-white rounded-lg shadow-lg border-2 border-black p-6">
        <p className="text-gray-600">Explanation visualization not available</p>
      </div>
    );
  }

  // Create a blob URL from the HTML content for iframe src
  const blobUrl = URL.createObjectURL(
    new Blob([htmlContent], { type: 'text/html' })
  );

  return (
    <div className="w-full bg-white rounded-lg shadow-lg border-2 border-black p-6 overflow-hidden">
      <h3 className="text-2xl font-bold text-gray-900 mb-4">Interactive Risk Indicator Analysis</h3>
      <p className="text-sm text-gray-600 mb-4">
        Interactive visualization showing how each feature contributes to the prediction
      </p>
      <iframe
        src={blobUrl}
        className="w-full border-0"
        style={{ minHeight: '600px' }}
        title="Plotly Explanation Visualization"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
};

export default PlotlyEmbed;

