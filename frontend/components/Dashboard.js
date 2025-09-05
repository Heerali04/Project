import React, { useEffect, useState } from "react";

function Dashboard() {
  const [labReports, setLabReports] = useState([]);
  const [symptomReports, setSymptomReports] = useState([]);
  const [filter, setFilter] = useState("all"); // all | lab | symptoms

  useEffect(() => {
    fetch("http://localhost:5000/reports")
      .then((res) => res.json())
      .then((data) => {
        const labs = data.filter((r) => r.disease); // lab uploads
        const symptoms = data.filter((r) => r.possible_diseases); // manual entry
        setLabReports(labs.reverse());
        setSymptomReports(symptoms.reverse());
      })
      .catch((err) => console.error("Error fetching reports:", err));
  }, []);

  const renderResult = (result) => {
    if (result.toLowerCase() === "positive") {
      return <span className="text-red-600 font-semibold">{result}</span>;
    } else if (result.toLowerCase() === "negative") {
      return <span className="text-green-600 font-semibold">{result}</span>;
    }
    return <span className="text-gray-600">{result}</span>;
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h2 className="text-3xl font-bold mb-4 text-center">📊 Reports Dashboard</h2>

      {/* Summary counts */}
      <div className="text-center mb-8 text-lg">
        <span className="mr-6">🧪 Lab Reports: <strong>{labReports.length}</strong></span>
        <span>🤒 Symptom Analyses: <strong>{symptomReports.length}</strong></span>
      </div>

      {/* Filter buttons */}
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setFilter("all")}
          className={`px-4 py-2 rounded-lg ${
            filter === "all" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          All Reports
        </button>
        <button
          onClick={() => setFilter("lab")}
          className={`px-4 py-2 rounded-lg ${
            filter === "lab" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          Lab Reports
        </button>
        <button
          onClick={() => setFilter("symptoms")}
          className={`px-4 py-2 rounded-lg ${
            filter === "symptoms" ? "bg-blue-600 text-white" : "bg-gray-200"
          }`}
        >
          Symptom Analysis
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* ---------------- Lab Reports Section ---------------- */}
        {(filter === "all" || filter === "lab") && (
          <div>
            <h3 className="text-2xl font-semibold text-blue-700 mb-4">🧪 Lab Reports</h3>
            {labReports.length === 0 ? (
              <p className="text-gray-600">No lab reports available.</p>
            ) : (
              <div className="space-y-4">
                {labReports.map((report, idx) => (
                  <div
                    key={idx}
                    className="border rounded-xl shadow bg-white p-4 hover:shadow-md transition"
                  >
                    <p><strong>Disease:</strong> {report.disease}</p>
                    <p><strong>Result:</strong> {renderResult(report.result)}</p>
                    <p><strong>CT Value:</strong> {report.ct_value}</p>
                    <p><strong>Suggestion:</strong> {report.suggestion}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ---------------- Symptom Analysis Section ---------------- */}
        {(filter === "all" || filter === "symptoms") && (
          <div>
            <h3 className="text-2xl font-semibold text-green-700 mb-4">🤒 Symptom Analysis</h3>
            {symptomReports.length === 0 ? (
              <p className="text-gray-600">No symptom analyses available.</p>
            ) : (
              <div className="space-y-4">
                {symptomReports.map((report, idx) => (
                  <div
                    key={idx}
                    className="border rounded-xl shadow bg-white p-4 hover:shadow-md transition"
                  >
                    <p><strong>Symptoms Entered:</strong> {report.symptoms}</p>
                    <div className="mt-3 space-y-3">
                      {report.possible_diseases.map((disease, i) => (
                        <div
                          key={i}
                          className="border rounded-lg p-3 bg-gray-50 shadow-sm"
                        >
                          <p><strong>Disease:</strong> {disease.disease}</p>
                          <p><strong>Result:</strong> {renderResult(disease.result)}</p>
                          <p><strong>Matched Symptoms:</strong> {disease.matched_symptoms.join(", ") || "None"}</p>
                          <p><strong>Suggestion:</strong> {disease.suggestion}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
