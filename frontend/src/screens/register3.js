import React, { useState, useEffect } from "react";
import PhoneInput from "react-phone-input-2";
import "react-phone-input-2/lib/style.css";
import Select from "react-select";
import axios from "axios";
import { getNames, getCode } from "country-list"; // Import country-list functions
import { useUser } from '../UserContext';
import { useNavigate } from "react-router-dom"; // Import useNavigate


export default function Register3() {
  const navigate = useNavigate(); // Move useNavigate here
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    phoneNumber: "",
    gender: "male",
    birthdate: { day: "", month: "", year: "" },
    country: "",
    city: "",
    address: "",
    email: ""
  });

  const [countries, setCountries] = useState([]); // Countries from country-list
  const [cities, setCities] = useState([]);
  const [loadingCities, setLoadingCities] = useState(false); // Add loading state

  const { user } = useUser();

  useEffect(() => {
    setFormData(prev => ({ ...prev, email: user.email }));
  }, [user.email]);

  // Fetch countries using country-list
  useEffect(() => {
    const countryNames = getNames(); // Get all country names
    const countryOptions = countryNames.map(name => ({
      value: getCode(name), // Get country code (e.g., "US" for United States)
      label: name, // Country name (e.g., "United States")
    }));
    setCountries(countryOptions.sort((a, b) => a.label.localeCompare(b.label))); // Sort alphabetically
  }, []);

  // Fetch cities when country changes using GeoNames API
  useEffect(() => {
    const fetchCities = async () => {
      if (formData.country) {
        setLoadingCities(true);
        try {
          const response = await axios.get(
            `http://api.geonames.org/searchJSON?country=${formData.country}&maxRows=1000&username=mu50n`
          );
          const cityOptions = response.data.geonames.map(city => ({
            value: city.name,
            label: city.name,
          }));
          setCities(cityOptions);
        } catch (error) {
          console.error("Error fetching cities:", error);
        }
        setLoadingCities(false);
      }
    };
    fetchCities();
  }, [formData.country]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handlePhoneChange = (value) => {
    setFormData({ ...formData, phoneNumber: value });
  };

  const handleCountryChange = (selectedOption) => {
    setFormData({ ...formData, country: selectedOption.value, city: "" });
  };

  const handleCityChange = (selectedOption) => {
    setFormData({ ...formData, city: selectedOption.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Submitting form data:", formData); // Log formData before submission
    try {
      const response = await axios.post("http://localhost:8000/register_personal", {
        ...formData,
        birthdate: {
          day: parseInt(formData.birthdate.day),
          month: parseInt(formData.birthdate.month),
          year: parseInt(formData.birthdate.year),
        },
      });
      console.log("Personal details saved:", response.data);
      alert("Details saved successfully!");
      navigate("/dashboard1"); // Redirect to the dashboard1 page
    } catch (error) {
      console.error("Error saving details:", error);
      alert("Error saving details. Please try again.");
    }
  };

  const dayOptions = Array.from({ length: 31 }, (_, i) => ({ value: i + 1, label: i + 1 }));
  const monthOptions = Array.from({ length: 12 }, (_, i) => ({ value: i + 1, label: i + 1 }));
  const yearOptions = Array.from({ length: 100 }, (_, i) => ({ value: 2023 - i, label: 2023 - i }));

  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      flexDirection: "column",
      textAlign: "center",
      background: "linear-gradient(135deg, #f0f4f8, #d9e2ec)",
      padding: "20px",
    }}>
      <form onSubmit={handleSubmit} style={{ width: "350px", backgroundColor: "#fff", padding: "20px", borderRadius: "10px", boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)", textAlign: "left" }}>
        <h2 style={{ color: "#333", marginBottom: "20px", fontWeight: "bold", textAlign: "center" }}>Personal Details</h2>
        <input
          type="text"
          name="firstName"
          placeholder="Enter your First Name"
          value={formData.firstName}
          onChange={handleChange}
          required
          style={{ width: "80%", padding: "10px", marginBottom: "10px", borderRadius: "5px", border: "1px solid #ccc", boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)", transition: "border-color 0.3s" }}
          onFocus={(e) => e.target.style.borderColor = "#007bff"}
          onBlur={(e) => e.target.style.borderColor = "#ccc"}
        />
        <input
          type="text"
          name="lastName"
          placeholder="Enter your Last Name"
          value={formData.lastName}
          onChange={handleChange}
          required
          style={{ width: "80%", padding: "10px", marginBottom: "10px", borderRadius: "5px", border: "1px solid #ccc", boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)", transition: "border-color 0.3s" }}
          onFocus={(e) => e.target.style.borderColor = "#007bff"}
          onBlur={(e) => e.target.style.borderColor = "#ccc"}
        />
        <input
          type="email"
          name="email"
          placeholder="Enter your Email"
          value={formData.email}
          onChange={handleChange}
          required
          readOnly
          style={{
            width: "80%",
            padding: "10px",
            marginBottom: "10px",
            borderRadius: "5px",
            border: "1px solid #ccc",
            boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)",
            transition: "border-color 0.3s",
            backgroundColor: "#f0f0f0"
          }}
          onFocus={(e) => e.target.style.borderColor = "#007bff"}
          onBlur={(e) => e.target.style.borderColor = "#ccc"}
        />
        <PhoneInput
          country={'us'}
          value={formData.phoneNumber}
          onChange={handlePhoneChange}
          inputProps={{
            name: 'phoneNumber',
            required: true,
          }}
          containerStyle={{ marginBottom: "10px" }}
          inputStyle={{ width: "100%", padding: "10px", borderRadius: "5px", border: "1px solid #ccc", boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)", transition: "border-color 0.3s" }}
          onFocus={(e) => e.target.style.borderColor = "#007bff"}
          onBlur={(e) => e.target.style.borderColor = "#ccc"}
        />
        <div style={{ marginBottom: "10px" }}>
          <label style={{ marginRight: "10px" }}>
            <input
              type="radio"
              name="gender"
              value="male"
              checked={formData.gender === "male"}
              onChange={handleChange}
            />
            Male
          </label>
          <label>
            <input
              type="radio"
              name="gender"
              value="female"
              checked={formData.gender === "female"}
              onChange={handleChange}
            />
            Female
          </label>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
          <Select
            name="day"
            options={dayOptions}
            placeholder="Day"
            onChange={(option) => setFormData({ ...formData, birthdate: { ...formData.birthdate, day: option.value } })}
            styles={{ container: (base) => ({ ...base, width: "30%" }) }}
          />
          <Select
            name="month"
            options={monthOptions}
            placeholder="Month"
            onChange={(option) => setFormData({ ...formData, birthdate: { ...formData.birthdate, month: option.value } })}
            styles={{ container: (base) => ({ ...base, width: "30%" }) }}
          />
          <Select
            name="year"
            options={yearOptions}
            placeholder="Year"
            onChange={(option) => setFormData({ ...formData, birthdate: { ...formData.birthdate, year: option.value } })}
            styles={{ container: (base) => ({ ...base, width: "30%" }) }}
          />
        </div>
        <Select
          name="country"
          options={countries}
          placeholder="Choose your country"
          onChange={handleCountryChange}
          isSearchable
          styles={{ container: (base) => ({ ...base, marginBottom: "10px" }) }}
        />
        <Select
          name="city"
          options={cities}
          placeholder={loadingCities ? "Loading cities..." : "Choose your city"}
          onChange={handleCityChange}
          isSearchable
          isDisabled={!formData.country || loadingCities}
          styles={{ container: (base) => ({ ...base, marginBottom: "10px" }) }}
        />
        <input
          type="text"
          name="address"
          placeholder="Enter your address"
          value={formData.address}
          onChange={handleChange}
          required
          style={{ width: "80%", padding: "10px", marginBottom: "20px", borderRadius: "5px", border: "1px solid #ccc", boxShadow: "inset 0 1px 3px rgba(0, 0, 0, 0.1)", transition: "border-color 0.3s" }}
          onFocus={(e) => e.target.style.borderColor = "#007bff"}
          onBlur={(e) => e.target.style.borderColor = "#ccc"}
        />
        <button type="submit" style={{ width: "100%", padding: "10px", backgroundColor: "#007bff", color: "#fff", border: "none", borderRadius: "5px", cursor: "pointer", transition: "background-color 0.3s" }}
          onMouseOver={(e) => e.target.style.backgroundColor = "#0056b3"}
          onMouseOut={(e) => e.target.style.backgroundColor = "#007bff"}
        >Next</button>
      </form>
    </div>
  );
}
