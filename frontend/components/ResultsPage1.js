import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const ResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const data = location.state || null; // directly get the passed object

  if (!data) {
    return (
      <div className="results-container p-4">
        <h2>No results to display. Please upload a report.</h2>
        <button
          onClick={() => navigate('/')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Go Back to Upload
        </button>
      </div>
    );
  }

  // Destructure all fields (including ct_values)
  const { disease, result, ct_value, ct_values, suggestion, raw_text } = data;

  return (
    <div className="results-container p-4 max-w-xl mx-auto bg-white rounded shadow mt-6">
      <h2 className="text-2xl font-bold mb-4">Report Analysis</h2>

      <div className="report-card mb-4">
        <h3 className="font-semibold mb-2">Diagnosis Summary</h3>
        <p><strong>Disease:</strong> {disease}</p>
        <p>
          <strong>Result:</strong>{" "}
          <span className={result === 'Positive' ? 'text-red-600 font-bold' : 'text-green-600 font-bold'}>
            {result}
          </span>
        </p>

        {/* Display Ct values */}
        <p><strong>Ct Values:</strong></p>
        <ul className="list-disc list-inside ml-4">
          {ct_values && Object.entries(ct_values).map(([gene, value]) => (
            <li key={gene}>{gene}: {value}</li>
          ))}
        </ul>
      </div>

      <div className="recommendations-card mb-4">
        <h3 className="font-semibold mb-2">Suggestions</h3>
        <p>{suggestion}</p>
      </div>

      <details className="bg-gray-100 p-2 rounded">
        <summary className="cursor-pointer font-semibold">View Raw OCR Text</summary>
        <pre className="mt-2 max-h-64 overflow-auto">{raw_text}</pre>
      </details>
    </div>
  );
};

export default ResultsPage;
