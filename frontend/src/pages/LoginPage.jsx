import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance from "../services/api";

const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("")

  // Check for verification token in URL query parameters
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const verifyToken = params.get("verifyToken");
    if (verifyToken) {
      axiosInstance.get(`/users/verify?token=${verifyToken}`)
        .then((res) => {
          setMessage("Email verified successfully. Please log in.");
        })
        .catch((err) => {
          setError("Email verification failed. Please try again.");
          console.error(err);
        });
    }
  }, [location])

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // FastAPI expects form data
      const response = await axiosInstance.post(
        "/users/token",
        new URLSearchParams({ username: email, password })
      );
      localStorage.setItem("token", response.data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError("Invalid credentials");
      console.error(err);
    }
  }

  return (
    <div>
      <h2>Login</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  )
};

export default LoginPage;
