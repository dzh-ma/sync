'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

// API base URL with fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create auth context
const AuthContext = createContext({
  user: null,
  loading: true,
  logout: () => {},
  isAuthenticated: false
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Load user from localStorage
    const loadUser = () => {
      try {
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
          const parsedUser = JSON.parse(storedUser);
          setUser(parsedUser);
        }
      } catch (error) {
        console.error('Error loading user from storage:', error);
        logout(); // Clear invalid data
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // Set up axios interceptor to add auth token to requests
  useEffect(() => {
    const interceptor = axios.interceptors.request.use(
      (config) => {
        // Don't add token to auth endpoints
        if (config.url?.includes('/token') || config.url?.includes('/register')) {
          return config;
        }
        
        const token = localStorage.getItem('access_token');
        const tokenType = localStorage.getItem('token_type') || 'Bearer';
        
        if (token) {
          config.headers.Authorization = `${tokenType} ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    return () => {
      // Remove interceptor when component unmounts
      axios.interceptors.request.eject(interceptor);
    };
  }, []);

  const logout = () => {
    // Clear all auth data
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('currentUser');
    setUser(null);
    
    // Redirect to login
    router.push('/auth/login');
  };

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        loading, 
        logout,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => useContext(AuthContext);

// Higher-order component to protect routes
export function withAuth(Component) {
  return function ProtectedRoute(props) {
    const { user, loading, isAuthenticated } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!loading && !isAuthenticated) {
        router.push('/auth/login');
      }
    }, [loading, isAuthenticated, router]);

    if (loading) {
      return <div className="flex h-screen items-center justify-center">Loading...</div>;
    }

    return isAuthenticated ? <Component {...props} /> : null;
  };
}
