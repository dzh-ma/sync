import React, { useState } from "react";
import axiosInstance from "../services/api";

const AddEnergyDataPage = () => {
  const [formData, setFormData] = useState({
    device_id: "",
    energy_consumed: "",
    timestamp: "",
    location: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) =>  {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("/data/add", {
        ...formData,
        energy_consumed: parseFloat(formData.energy_consumed),
        timestamp: new Date(formData.timestamp)
      });
      setMessage("Energy data added successfully!");
      setError("");
      setFormData({ device_id: "", energy_consumed: "", timestamp: "", location: "" });
    } catch (err) {
      setError("Error adding energy data");
      console.error(err);
    }
  };

  return (
    <div>
      <h2>Add Energy Data</h2>
      {message && <p style={{ color: "green" }}>{message}</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Device ID:</label>
          <input
            type="text"
            name="device_id"
            value={formData.device_id}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Energy Consumed (kWh):</label>
          <input
            type="number"
            step="0.01"
            name="energy_consumed"
            value={formData.energy_consumed}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Location:</label>
          <input
            type="text"
            name="location"
            value={formData.location}
            onChange={handleChange}
          />
        </div>
        <button type="submit">Add Data</button>
      </form>
    </div>
  );
};

export default AddEnergyDataPage;
