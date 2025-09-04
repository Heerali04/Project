import React, { useEffect, useState } from "react";

function Dashboard() {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/reports")
      .then(res => res.json())
      .then(data => setReports(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Reports Dashboard</h1>
      {reports.length === 0 ? (
        <p>No reports uploaded yet.</p>
      ) : (
        <table className="table-auto border-collapse border border-gray-400">
          <thead>
            <tr>
              <th className="border border-gray-300 px-2 py-1">Disease</th>
              <th className="border border-gray-300 px-2 py-1">Result</th>
              <th className="border border-gray-300 px-2 py-1">Ct Value</th>
              <th className="border border-gray-300 px-2 py-1">Suggestions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r, i) => (
              <tr key={i}>
                <td className="border border-gray-300 px-2 py-1">{r.disease}</td>
                <td className="border border-gray-300 px-2 py-1">{r.result}</td>
                <td className="border border-gray-300 px-2 py-1">{r.ct_value}</td>
                <td className="border border-gray-300 px-2 py-1">{r.suggestion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Dashboard;
