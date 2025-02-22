import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://127.0.0.1:800/api/v1",   // Adjust if needed
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
