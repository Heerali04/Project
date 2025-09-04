import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function LoginPage({ setLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!username || !password) return alert("Enter username & password");

    try {
      const res = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (data.success) {
        setLoggedIn(true);           // set login state
        navigate("/");               // redirect to upload page
      } else {
        alert(data.message);
      }
    } catch (err) {
      console.error(err);
      alert("Login error");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <h1 className="text-3xl font-bold mb-6">Login</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        className="mb-4 px-2 py-1 rounded border"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        className="mb-4 px-2 py-1 rounded border"
      />
      <button
        onClick={handleLogin}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Login
      </button>
    </div>
  );
}

export default LoginPage;
