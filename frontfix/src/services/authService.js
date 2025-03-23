// src/services/authService.js
import api from './api';

export const login = async (username, password) => {
  try {
    // Store credentials for basic auth
    const credentials = `${username}:${password}`;
    localStorage.setItem('credentials', credentials);
    
    // Test the credentials with a simple request
    const response = await api.get('/users/');
    // Check if response contains users
    return response.data && response.data.length > 0 ? response.data[0] : null;
  } catch (error) {
    // Remove credentials if login fails
    localStorage.removeItem('credentials');
    console.error('Login error:', error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('credentials');
};
