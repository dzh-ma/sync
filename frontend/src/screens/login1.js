import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

export default function Login1() {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleLogin = async () => {
    setError("");
    setSuccess("");

    try {
      const response = await axios.post("http://localhost:8000/login", formData);
      setSuccess(response.data.msg);

      // Navigate to dashboard1 upon successful login
      navigate("/dashboard1");
    } catch (err) {
      setError(err.response?.data?.detail || "An error occurred");
    }
  };

  return (
    <div
      style={{
        margin: "50px auto",
        padding: "30px",
        border: "1px solid #e0e0e0",
        borderRadius: "12px",
        width: "350px",
        boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
      }}
    >
      <h1 style={{ fontSize: "24px", marginBottom: "10px", textAlign: "center" }}>
        Login
      </h1>
      <p style={{ color: "#888", marginBottom: "20px", textAlign: "center" }}>
        Welcome Back, Admin
      </p>

      {/* Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleLogin();
        }}
      >
        {/* Email Field */}
        <div style={{ marginBottom: "15px", textAlign: "left" }}>
          <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            placeholder="Enter your email"
            style={{
              width: "93%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />
        </div>

        {/* Password Field */}
        <div style={{ marginBottom: "15px", textAlign: "left" }}>
          <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>
            Password
          </label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleInputChange}
            required
            placeholder="Enter your password"
            style={{
              width: "93%",
              padding: "10px",
              borderRadius: "5px",
              border: "1px solid #ccc",
            }}
          />
        </div>

        {/* Submit Button */}
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
          Login
        </button>
      </form>

      {/* Error and Success Messages */}
      {error && (
        <p style={{ color: "red", marginTop: "20px", textAlign: "center" }}>
          {error}
        </p>
      )}
      {success && (
        <p style={{ color: "green", marginTop: "20px", textAlign: "center" }}>
          {success}
        </p>
      )}

      {/* Links */}
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <p>
          Don’t have an account?{" "}
          <button
            onClick={() => navigate("/register1")}
            style={{
              color: "#007BFF",
              background: "none",
              border: "none",
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            Register Now
          </button>
        </p>
        <p>
          Part of a household?{" "}
          <button
            onClick={() => navigate("/login2")}
            style={{
              color: "#007BFF",
              background: "none",
              border: "none",
              cursor: "pointer",
              textDecoration: "underline",
            }}
          >
            Click Here
          </button>
        </p>
      </div>
    </div>
  );
}





