import React, { useState } from "react";
import { useNavigate } from "react-router-dom";   // ✅ import navigate hook

function AuthPage({ setLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();   // ✅ setup navigate

  const handleSubmit = async (e) => {
    e.preventDefault();

    const endpoint = isLogin
      ? "http://localhost:5000/login"
      : "http://localhost:5000/register";

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      setMessage(data.message || "Something went wrong");

      if (data.success && isLogin) {
        setLoggedIn(true);
        navigate("/");   // ✅ redirect to Upload page
      }
    } catch (err) {
      setMessage("Error connecting to server");
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "50px auto", padding: "20px", border: "1px solid #ddd", borderRadius: "8px" }}>
      <h2>{isLogin ? "Login" : "Signup"}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            style={{ width: "100%", marginBottom: "10px", padding: "8px" }}
          />
        </div>
        <div>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: "100%", marginBottom: "10px", padding: "8px" }}
          />
        </div>
        <button
          type="submit"
          style={{
            width: "100%",
            padding: "10px",
            background: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
          }}
        >
          {isLogin ? "Login" : "Signup"}
        </button>
      </form>
      <p
        style={{ marginTop: "10px", cursor: "pointer", color: "#007bff" }}
        onClick={() => setIsLogin(!isLogin)}
      >
        {isLogin ? "Need an account? Signup" : "Already have an account? Login"}
      </p>
      {message && (
        <p style={{ marginTop: "15px", fontWeight: "bold" }}>{message}</p>
      )}
    </div>
  );
}

export default AuthPage;
