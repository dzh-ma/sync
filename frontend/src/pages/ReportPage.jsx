import React, { useState } from "react";
import axiosInstance from "../services/api";

const ReportPage = () => {
  const [formData, setFormData] = useState({
    start_date: "",
    end_date: "",
    format: "csv"
  });
  const [error, setError] = useState();
  const [downloading, setDownloading] = useState();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setDownloading(true);
    try {
      const response = await axiosInstance.post(
        `/reports/report?format=${formData.format}&start_date=${formData.start_date}&end_date=${formData.end_date}`,
        null,
        { responseType: "blob" }
      );

      // Create a download link for the generated report
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `energy_report.${formData.format}`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setError("");
    } catch (err) {
      setError("Error generating report");
      console.error(err);
    }
    setDownloading(false);
  };

  return (
    <div>
      <h2>Generate Energy Report</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Start Date:</label>
          <input
            type="date"
            name="start_date"
            value={formData.start_date}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>End Date:</label>
          <input
            type="date"
            name="end_date"
            value={formData.end_date}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Format:</label>
          <select name="format" value={formData.format} onChange={handleChange}>
            <option value="csv">CSV</option>
            <option value="pdf">PDF</option>
          </select>
        </div>
        <button type="submit" disabled={downloading}>
          {downloading ? "Generating..." : "Generate Report"}
        </button>
      </form>
    </div>
  )
}

export default ReportPage
