import React, { useState } from "react";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) { alert("Select a file"); return; }
    setLoading(true); setResponse(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="p-4">
      <h1>Medical Report Analyzer</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload & Analyze</button>

      {loading && <p>Processing...</p>}
      {response && !loading && (
        <div style={{ border: "1px solid gray", padding: "10px", marginTop: "10px" }}>
          <p><strong>Disease:</strong> {response.disease}</p>
          <p><strong>Result:</strong> {response.result}</p>
          <p><strong>Ct Value:</strong> {response.ct_value}</p>
          <p><strong>Suggestions:</strong> {response.suggestion}</p>
          <details>
            <summary>Raw OCR Text</summary>
            <pre>{response.raw_text}</pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default UploadPage;
