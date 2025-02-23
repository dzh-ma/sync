import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../services/api";

const RegisterPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState();
  const [password, setPassword] = useState();
  const [role, setRole] = useState();
  const [errors, setErrors] = useState();
  const [message, setMessage] = useState();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors([]);        // clear previous errors
    try {
      await axiosInstance.post("/users/register", { email, password, role });
      setMessage("Registration successful! Please log in.");
      navigate("/login");
    } catch (err) {
      if (err.response && err.response.data.detail) {
        const validationErrors = err.response.data.detail.map(
          (item) => item.msg
        );
        setErrors(validationErrors);
      } else {
        setErrors(["Registration failed, please try again."]);
      }
      console.errors(err);
    }
  }

  return (
    <div>
      <h2>Register</h2>
      {message && <p style={{ color: "green" }}>{message}</p>}
      {Array.isArray(errors) && errors.length > 0 ? (
        <ul style={{ color: 'red' }}>
          {errors.map((error, index) => (
            <li key={index}>{error}</li>
          ))}
        </ul>
      ) : (
          errors && <p style={{ color: 'red' }}>{errors}</p>
        )}
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
          <br />
          <small>
            Password must be at least 8 characters long, contain at least 1 number,
            1 letter (both uppercase & lowercase) & 1 special character
          </small>
        </div>
        <div>
          <label>Role:</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default RegisterPage;
