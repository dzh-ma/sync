import React, { useState, useEffect } from "react";
import axiosInstance from "../services/api";

const DashboardPage = () => {
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({ start_date: "", end_date: "" });
  const [error, setError] = useState("");

  const fetchData = async () => {
    try {
      const response = await axiosInstance.get("/data/aggregate", {
        params: {
          start_date: filters.start_date,
          end_date: filters.end_date,
          interval: "day"
        }
      });
      setData(response.data.aggregated_data);
    } catch (err) {
      setError("Error fetching data");
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  }

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div>
      <h2>Dashboard</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleFilterSubmit}>
        <div>
          <label>Start date:</label>
          <input
            type="date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />
        </div>
        <div>
          <label>End Date:</label>
          <input
            type="date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </div>
        <button type="submit">Apply Filters</button>
      </form>
      <table border="1" style={{ marginTop: "20px" }}>
        <thead>
          <tr>
            <th>Device ID</th>
            <th>Date</th>
            <th>Total Energy (kWh)</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, index) => (
            <tr key={index}>
              <td>{item._id.device_id || "N/A"}</td>
              <td>{`${item.id.year}-${item._id.month}-${item._id.day}`}</td>
              <td>{item.total_energy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DashboardPage;
