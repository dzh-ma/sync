/**
 * API Service
 *
 * This module creates and exports an Axios instance configured to communicate with
 * the FastAPI backend. It sets the base URL for API calls and automatically attaches
 * a JWT token (if available in localStorage) to each request for authentication.
 *
 * @module api
 * @example
 * import axiosInstance from './services/api';
 * 
 * // Making a GET request to fetch user data
 * axiosInstance.get('/users/me')
 *   .then(response => console.log(response.data))
 *   .catch(error => console.error(error));
 */

import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",   // Adjust if needed
});

// Interceptor to attach JWT token from localStorage to every request
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
