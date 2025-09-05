import React, { useState } from "react";

function SymptomsPage() {
  const [symptoms, setSymptoms] = useState("");
  const [results, setResults] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResults(null);

    try {
      const response = await fetch("http://localhost:5000/symptoms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms }),
      });

      const data = await response.json();
      setResults(data);
    } catch (err) {
      console.error("Error submitting symptoms:", err);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Enter Symptoms</h2>
      <form onSubmit={handleSubmit} className="mb-6">
        <textarea
          className="w-full p-3 border rounded-md mb-4"
          rows="4"
          value={symptoms}
          onChange={(e) => setSymptoms(e.target.value)}
          placeholder="e.g. fever, headache, vomiting, rash, cold"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Analyze
        </button>
      </form>

      {results && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold mb-2">Analysis Result</h3>

          {/* Show all possible diseases */}
          {results.possible_diseases.map((disease, idx) => (
            <div
              key={idx}
              className="border p-4 rounded mb-3 shadow-sm bg-gray-50"
            >
              <h4 className="text-lg font-bold">{disease.disease}</h4>
              <p>
                <strong>Result:</strong> {disease.result}
              </p>
              <p>
                <strong>Matched Symptoms:</strong>{" "}
                {disease.matched_symptoms.join(", ") || "None"}
              </p>
              <p className="text-sm text-gray-700">
                <strong>Suggestion:</strong> {disease.suggestion}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SymptomsPage;
