import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import UploadPage from "./components/UploadPage";

import SymptomsPage from "./components/SymptomsPage";
import AuthPage from "./components/AuthPage";
import ReportsPage from "./components/ReportsPage";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogout = () => {
    setLoggedIn(false); // clear login state
  };

  return (
    <Router>
      <div>
        {/* Show navbar only when logged in */}
        {loggedIn && (
          <nav className="p-4 bg-gray-200 flex justify-between items-center shadow-md">
            <div className="flex space-x-4">
              <Link className="text-blue-700 hover:underline" to="/">Upload</Link>
              <Link className="text-blue-700 hover:underline" to="/symptoms">Symptoms</Link>
              
              <Link className="text-blue-700 hover:underline" to="/reports">Reports Dashboard</Link>
            </div>
            <button
              onClick={handleLogout}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
          </nav>
        )}

        <main className="p-6">
          <Routes>
            {/* Login/Signup Page */}
            <Route
              path="/login"
              element={<AuthPage setLoggedIn={setLoggedIn} />}
            />

            {/* Protected routes */}
            <Route
              path="/"
              element={loggedIn ? <UploadPage /> : <Navigate to="/login" />}
            />
            <Route
              path="/symptoms"
              element={loggedIn ? <SymptomsPage /> : <Navigate to="/login" />}
            />
            {/* <Route
              path="/dashboard"
              element={loggedIn ? <Dashboard /> : <Navigate to="/login" />}
            /> */}
            <Route
              path="/reports"
              element={loggedIn ? <ReportsPage /> : <Navigate to="/login" />}
            />

            {/* Fallback redirect */}
            <Route path="*" element={<Navigate to={loggedIn ? "/" : "/login"} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
