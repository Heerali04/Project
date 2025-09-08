import { useState } from "react";

function SymptomPredictor() {
  const [symptoms, setSymptoms] = useState("");
  const [result, setResult] = useState(null);

  const handlePredict = async () => {
    try {
      const res = await fetch("http://127.0.0.1:5000/predict_symptoms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Error:", err);
    }
  };

  return (
    <div className="p-4">
      <textarea
        value={symptoms}
        onChange={(e) => setSymptoms(e.target.value)}
        placeholder="Enter patient symptoms..."
        className="w-full border p-2"
      />
      <button
        onClick={handlePredict}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Predict
      </button>

      {result && (
        <div className="mt-4 p-2 border rounded bg-gray-100">
          <h3>Prediction: {result.prediction}</h3>
          <p>Matched Symptoms: {result.matched_symptoms?.join(", ")}</p>
          <p>Suggestion: {result.suggestion}</p>
        </div>
      )}
    </div>
  );
}

export default SymptomPredictor;
