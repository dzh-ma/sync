import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";

export default function Register2() {
  const [otp, setOtp] = useState(["", "", "", "", ""]);
  const [message, setMessage] = useState("");
  const [showPopup, setShowPopup] = useState(false); // State for popup visibility
  const location = useLocation();
  const navigate = useNavigate();
  const email = location.state?.email; // Get email from location state

  useEffect(() => {
    // Send OTP when the page loads
    const sendOtpOnLoad = async () => {
      try {
        await axios.post("http://localhost:8000/request-otp", { email });
        alert("OTP has been sent to your email!");
      } catch (error) {
        console.error("Failed to send OTP:", error.response?.data?.detail || error.message);
      }
    };

    sendOtpOnLoad(); // Call the function
  }, [email]); // Dependency ensures it runs only when 'email' changes

  const handleChange = (element, index) => {
    const value = element.value;
    if (/^\d*$/.test(value)) {
      const newOtp = [...otp];
      newOtp[index] = value;
      setOtp(newOtp);

      if (value && index < 4) {
        document.getElementById(`otp-input-${index + 1}`).focus();
      }
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/verify-otp", {
        email,
        otp: otp.join(""),
      });
      setMessage(response.data.msg);
      if (response.data.success) {
        setShowPopup(true); // Show popup on success
        setTimeout(() => {
          setShowPopup(false); // Hide popup after 3 seconds
          navigate("/register3"); // Navigate after the popup
        }, 3000);
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || "Verification failed!");
    }
  };

  const handleResendCode = async () => {
    try {
      await axios.post("http://localhost:8000/request-otp", { email });
      alert("OTP has been resent!");
    } catch (error) {
      alert("Failed to resend OTP!");
    }
  };

  return (
    <div style={{ margin: "50px auto", textAlign: "center", padding: "20px", border: "1px solid #ccc", borderRadius: "8px", width: "300px" }}>
      <h1>Verify Your Email</h1>
      <form onSubmit={handleVerifyOtp}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: "20px" }}>
          {otp.map((value, index) => (
            <input
              key={index}
              id={`otp-input-${index}`}
              type="text"
              value={value}
              onChange={(e) => handleChange(e.target, index)}
              maxLength="1"
              style={{ width: "40px", height: "40px", textAlign: "center", margin: "0 5px", fontSize: "18px" }}
            />
          ))}
        </div>
        <button
          type="submit"
          style={{
            backgroundColor: "#007BFF",
            color: "white",
            padding: "10px 20px",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Verify
        </button>
      </form>
      <p style={{ marginTop: "20px" }}>
        I did not receive the code,{" "}
        <span onClick={handleResendCode} style={{ color: "#007BFF", cursor: "pointer" }}>
          Resend the code
        </span>
      </p>
      {message && <p style={{ color: message.includes("failed") ? "red" : "green" }}>{message}</p>}

      {showPopup && (
        <div
          style={{
            position: "fixed",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "white",
            padding: "20px",
            boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
            borderRadius: "8px",
            zIndex: 1000,
            textAlign: "center",
          }}
        >
          <p style={{ fontSize: "18px", fontWeight: "bold", marginBottom: "10px" }}>OTP Verified Successfully!</p>
        </div>
      )}
    </div>
  );
}
