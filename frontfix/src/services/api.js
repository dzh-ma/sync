import axios from 'axios';

// Base API instance
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1', // Your FastAPI server URL
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication interceptor
api.interceptors.request.use(
  (config) => {
    // Get stored credentials - this is just basic auth, adjust as needed
    const credentials = localStorage.getItem('credentials');
    if (credentials) {
      config.headers.Authorization = `Basic ${btoa(credentials)}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
