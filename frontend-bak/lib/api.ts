// lib/api.ts
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create an axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the auth token to requests
api.interceptors.request.use(
  (config) => {
    // Get the token from localStorage
    const token = localStorage.getItem('access_token');
    const tokenType = localStorage.getItem('token_type') || 'bearer';
    
    // If token exists, add it to the headers
    if (token) {
      config.headers['Authorization'] = `${tokenType} ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors (expired token, etc.)
    if (error.response && error.response.status === 401) {
      // Clear stored tokens and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('token_type');
      localStorage.removeItem('currentUser');
      
      // In a client component, you'd use router.push
      // Since this is a service file, we'll use window.location
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await api.post('/users/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('token_type', response.data.token_type);
    
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('currentUser');
    window.location.href = '/login';
  },
  
  register: async (userData: any) => {
    const response = await api.post('/users/register', userData);
    return response.data;
  },
  
  verifyEmail: async (token: string) => {
    const response = await api.get(`/users/verify/${token}`);
    return response.data;
  },
};

// Device API
export const deviceApi = {
  getDevices: async () => {
    const response = await api.get('/devices/');
    return response.data;
  },
  
  getDevice: async (deviceId: string) => {
    const response = await api.get(`/devices/${deviceId}`);
    return response.data;
  },
  
  createDevice: async (device: any) => {
    const response = await api.post('/devices/', device);
    return response.data;
  },
  
  updateDevice: async (deviceId: string, updates: any) => {
    const response = await api.put(`/devices/${deviceId}`, updates);
    return response.data;
  },
  
  toggleDevice: async (deviceId: string) => {
    const response = await api.post(`/devices/${deviceId}/toggle`);
    return response.data;
  },
  
  controlDevice: async (deviceId: string, parameters: any) => {
    const response = await api.post(`/devices/${deviceId}/control`, parameters);
    return response.data;
  },
  
  deleteDevice: async (deviceId: string) => {
    const response = await api.delete(`/devices/${deviceId}`);
    return response.data;
  }
};

// Room API
export const roomApi = {
  getRooms: async () => {
    const response = await api.get('/rooms/');
    return response.data;
  },
  
  getRoom: async (roomId: string) => {
    const response = await api.get(`/rooms/${roomId}`);
    return response.data;
  },
  
  createRoom: async (room: any) => {
    const response = await api.post('/rooms/', room);
    return response.data;
  },
  
  updateRoom: async (roomId: string, updates: any) => {
    const response = await api.put(`/rooms/${roomId}`, updates);
    return response.data;
  },
  
  deleteRoom: async (roomId: string) => {
    const response = await api.delete(`/rooms/${roomId}`);
    return response.data;
  }
};

// Energy data API
export const energyApi = {
  getEnergyData: async (params: any = {}) => {
    const response = await api.get('/energy/user/energy-data', { params });
    return response.data;
  },
  
  getAggregatedData: async (params: any = {}) => {
    const response = await api.get('/energy/aggregate', { params });
    return response.data;
  },
  
  generateReport: async (format: 'csv' | 'pdf', params: any = {}) => {
    const response = await api.post(`/reports/report?format=${format}`, null, { 
      params,
      responseType: 'blob' 
    });
    return response.data;
  }
};

export default api;
