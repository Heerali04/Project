import React, { useEffect, useState } from "react";
import axios from "axios";

const ReportsPage = () => {
  const [reports, setReports] = useState([]);

  // Fetch reports
  const fetchReports = async () => {
    try {
      const res = await axios.get("http://localhost:5000/reports");
      setReports(res.data);
    } catch (err) {
      console.error("Error fetching reports:", err);
    }
  };

  // Clear all reports
  const clearReports = async () => {
    try {
      await axios.delete("http://localhost:5000/clear_reports");
      setReports([]); // empty the UI immediately
      alert("✅ All reports cleared!");
    } catch (err) {
      console.error("Error clearing reports:", err);
      alert("❌ Failed to clear reports");
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">📋 Reports Dashboard</h2>

      <button
        onClick={clearReports}
        className="mb-6 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        🗑️ Clear Reports
      </button>

      {reports.length === 0 ? (
        <p>No reports found.</p>
      ) : (
        <ul className="space-y-4">
          {reports.map((r) => (
            <li
              key={r._id}
              className="border p-4 rounded shadow-sm bg-gray-50"
            >
              {/* Check if it’s a symptom-based prediction */}
              {r.source === "ml-symptoms" ? (
                <>
                  <h3 className="text-lg font-semibold">🧾 Symptom Prediction</h3>
                  <p>
                    <strong>Disease:</strong> {r.prediction}
                  </p>
                  <p>
                    <strong>Symptoms:</strong> {r.symptoms}
                  </p>
                  {r.matched_symptoms?.length > 0 && (
                    <p>
                      <strong>Matched Symptoms:</strong>{" "}
                      {r.matched_symptoms.join(", ")}
                    </p>
                  )}
                  {r.suggestion && (
                    <p className="text-sm text-gray-700">
                      💡 Suggestion: {r.suggestion}
                    </p>
                  )}
                </>
              ) : (
                <>
                  <h3 className="text-lg font-semibold">🧾 Uploaded Report</h3>
                  <p>
                    <strong>Disease:</strong> {r.disease}
                  </p>
                  <p>
                    <strong>Result:</strong> {r.result}
                  </p>
                  {r.ct_value && r.ct_value !== "N/A" && (
                    <p>
                      <strong>Ct Value:</strong> {r.ct_value}
                    </p>
                  )}
                  {r.suggestion && (
                    <p className="text-sm text-gray-700">
                      💡 Suggestion: {r.suggestion}
                    </p>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ReportsPage;
