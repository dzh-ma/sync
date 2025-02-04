import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useUser } from '../UserContext';

function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const { setUser } = useUser();

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    setUser(prev => ({ ...prev, email: e.target.value }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setMessage("Passwords do not match!");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/register", {
        email,
        password,
      });
      setMessage(response.data.msg);
      alert("Account created successfully!");
      navigate("/register2", { state: { email } });
    } catch (error) {
      setMessage(error.response?.data?.detail || "Registration failed!");
    }
  };

  return (
    <div style={{ margin: "50px auto", padding: "30px", border: "1px solid #e0e0e0", borderRadius: "12px", width: "350px", boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)" }}>
      <h1 style={{ fontSize: "24px", marginBottom: "10px", textAlign: "center" }}>Register</h1>
      <p style={{ color: "#888", marginBottom: "20px", textAlign: "center" }}>Join us</p>
      <form onSubmit={handleRegister}>
        <div style={{ marginBottom: "15px", textAlign: "left" }}>
          <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>Enter your Email</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={handleEmailChange}
            required
            placeholder="Enter your Email"
            style={{ width: "93%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
          />
        </div>
        <div style={{ marginBottom: "15px", textAlign: "left" }}>
          <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>Password</label>
          <input
            type={showPassword ? "text" : "password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            placeholder="Enter your password"
            style={{ width: "93%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
          />
        </div>
        <div style={{ marginBottom: "15px", textAlign: "left" }}>
          <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>Confirm Password</label>
          <input
            type={showPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            placeholder="Enter your password"
            style={{ width: "93%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc" }}
          />
        </div>
        <div style={{ marginBottom: "20px", textAlign: "left" }}>
          <input
            type="checkbox"
            checked={showPassword}
            onChange={() => setShowPassword(!showPassword)}
          />
          <label style={{ marginLeft: "5px", color: "#888" }}>Show Password</label>
        </div>
        <button
          type="submit"
          style={{
            backgroundColor: "#007BFF",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            width: "100%",
          }}
        >
          Next
        </button>
      </form>
      {message && (
        <p
          style={{
            marginTop: "20px",
            color: message === "Passwords do not match!" ? "red" : "green",
          }}
        >
          {message}
        </p>
      )}
    </div>
  );
}

export default Register;
