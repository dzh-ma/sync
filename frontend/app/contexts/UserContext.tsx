// contexts/UserContext.tsx
"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

// User type definition that matches the backend model
interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  password?: string; // Store password for HTTP Basic Auth
  active: boolean;
}

interface UserContextType {
  user: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  error: string | null;
}

// Create context
const UserContext = createContext<UserContextType | undefined>(undefined);

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check if user is already logged in (from localStorage)
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        
        // Verify the stored credentials are still valid
        verifyCredentials(parsedUser.username, parsedUser.password);
      } catch (e) {
        console.error('Failed to parse stored user:', e);
        localStorage.removeItem('user');
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  // Verify the user's credentials with the backend
  const verifyCredentials = async (username: string, password: string) => {
    try {
      // Create HTTP Basic Auth credentials
      const credentials = btoa(`${username}:${password}`);
      
      // Call user endpoint to verify credentials
      const response = await fetch(`${API_URL}/users/${user?.id || 'me'}`, {
        headers: {
          'Authorization': `Basic ${credentials}`
        }
      });
      
      if (!response.ok) {
        // If verification fails, logout
        setUser(null);
        localStorage.removeItem('user');
        setError('Session expired. Please login again.');
      }
      
    } catch (e) {
      console.error('Failed to verify credentials:', e);
    } finally {
      setIsLoading(false);
    }
  };

  // Login function
  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Create HTTP Basic Auth credentials
      const credentials = btoa(`${username}:${password}`);
      
      // Call login endpoint to validate credentials
      const response = await fetch(`${API_URL}/users`, {
        headers: {
          'Authorization': `Basic ${credentials}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Invalid username or password');
      }
      
      // Get user data
      const users = await response.json();
      const loggedInUser = users.find((u: any) => u.username === username);
      
      if (!loggedInUser) {
        throw new Error('User not found');
      }
      
      // Create user object with password for future API calls
      const userWithAuth = {
        ...loggedInUser,
        password // Store password for HTTP Basic Auth
      };
      
      // Set user in state and localStorage
      setUser(userWithAuth);
      localStorage.setItem('user', JSON.stringify(userWithAuth));
      return true;
    } catch (e: any) {
      console.error('Login failed:', e);
      setError(e.message || 'Login failed. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <UserContext.Provider value={{ user, login, logout, isLoading, error }}>
      {children}
    </UserContext.Provider>
  );
}

// Custom hook to use the user context
export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}
