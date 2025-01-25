import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login2() {
  const [email, setEmail] = useState("");
  const [pin, setPin] = useState(["", "", "", ""]);
  const navigate = useNavigate();

  const handlePinChange = (e, index) => {
    const value = e.target.value.replace(/[^0-9]/g, ""); // Allow only numbers
    if (value.length <= 1) {
      const newPin = [...pin];
      newPin[index] = value;
      setPin(newPin);

      // Automatically focus the next input
      if (value && index < 3) {
        document.getElementById(`pin-${index + 1}`).focus();
      }
    }
  };

  const handleRegister = () => {
    navigate("/register1");
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
        Welcome,
      </h1>
      <p style={{ color: "#888", marginBottom: "20px", textAlign: "center" }}>
        Household Member
      </p>

      {/* Email Field */}
      <div style={{ marginBottom: "15px", textAlign: "left" }}>
        <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>
          Enter your Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          style={{
            width: "93%",
            padding: "10px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />
      </div>

      {/* PIN Input */}
      <div style={{ marginBottom: "15px", textAlign: "left" }}>
        <label style={{ display: "block", marginBottom: "5px", color: "#888" }}>
          Pin
        </label>
        <div style={{ display: "flex", gap: "5px" }}>
          {pin.map((digit, index) => (
            <input
              key={index}
              id={`pin-${index}`}
              type="text"
              value={digit}
              onChange={(e) => handlePinChange(e, index)}
              maxLength="1"
              style={{
                width: "20%",
                padding: "10px",
                textAlign: "center",
                borderRadius: "5px",
                border: "1px solid #ccc",
                fontSize: "16px",
              }}
            />
          ))}
        </div>
      </div>

      {/* Login Button */}
      <button
        style={{
          width: "100%",
          padding: "10px",
          backgroundColor: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
          fontSize: "16px",
        }}
      >
        Login
      </button>

      {/* Register Link */}
      <div style={{ marginTop: "20px", textAlign: "center" }}>
        <p style={{ color: "#888" }}>Don’t have an account?</p>
        <button
          onClick={handleRegister}
          style={{
            background: "none",
            border: "none",
            color: "#007BFF",
            textDecoration: "underline",
            cursor: "pointer",
            fontSize: "16px",
          }}
        >
          Register Now
        </button>
      </div>
    </div>
  );
}
