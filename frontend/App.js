import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import UploadPage from "./components/UploadPage";
import Dashboard from "./components/Dashboard";
import AuthPage from "./components/AuthPage";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogout = () => {
    setLoggedIn(false); // clear login state
  };

  return (
    <Router>
      <div>
        {loggedIn && (
          <nav className="p-4 bg-gray-200 flex justify-between items-center">
            <div>
              <Link className="mr-4 text-blue-700" to="/">Upload</Link>
              <Link className="text-blue-700" to="/dashboard">Dashboard</Link>
            </div>
            <button
              onClick={handleLogout}
              className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
          </nav>
        )}

        <main>
          <Routes>
            {/* Auth Page (Signup + Login in one component) */}
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
              path="/dashboard"
              element={loggedIn ? <Dashboard /> : <Navigate to="/login" />}
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
