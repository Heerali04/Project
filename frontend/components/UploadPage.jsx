import React, { useState } from "react";
import axios from "axios";

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setReport(null);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const data = response.data;

      // ✅ If result is "Negative", hide suggestion
      if (data.result && data.result.toLowerCase() === "negative") {
        data.suggestion = null;
      }

      setReport(data);
    } catch (error) {
      console.error(error);
      alert("Error uploading file.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Upload Medical Report</h1>

      <input type="file" onChange={handleFileChange} className="mb-4" />

      <button
        onClick={handleUpload}
        disabled={loading}
        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
      >
        {loading ? "Uploading..." : "Upload"}
      </button>

      {report && (
        <div className="mt-6 p-4 border rounded bg-gray-100 shadow">
          <h2 className="text-xl font-semibold mb-2">Report Result</h2>
          <p>
            <strong>Disease:</strong> {report.disease}
          </p>
          <p>
            <strong>Result:</strong> {report.result}
          </p>
          {report.ct_value && (
            <p>
              <strong>Ct Value:</strong> {report.ct_value}
            </p>
          )}

          {/* ✅ Show suggestion only if available */}
          {report.suggestion && (
            <p className="mt-2 text-sm text-gray-700">
              <strong>Suggestion:</strong> {report.suggestion}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadPage;
