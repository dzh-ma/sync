"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface User {
  id: string;
  username: string;
  token: string;
  active: boolean;
  role: string;
}

interface UserContextType {
  user: User | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
}

// Create context with a default value
const UserContext = createContext<UserContextType>({
  user: null,
  isLoading: true,
  login: async () => false,
  logout: () => {},
});

// API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for stored user data on initial load
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (error) {
        console.error("Failed to parse stored user:", error);
        localStorage.removeItem("user");
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // Create Basic Auth token
      const token = btoa(`${username}:${password}`);
      
      // Attempt to authenticate
      const response = await fetch(`${API_URL}/users`, {
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`Authentication failed: ${response.status}`);
      }
      
      // Get the current user's details
      const currentUserResponse = await fetch(`${API_URL}/users/${username}`, {
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!currentUserResponse.ok) {
        throw new Error(`Failed to fetch user details: ${currentUserResponse.status}`);
      }
      
      const userData = await currentUserResponse.json();
      
      // Create user object
      const authenticatedUser: User = {
        id: userData.id,
        username: userData.username,
        token: token,
        active: userData.active,
        role: userData.role || "user" // Default to regular user if no role specified
      };
      
      // Store in state and localStorage
      setUser(authenticatedUser);
      localStorage.setItem("user", JSON.stringify(authenticatedUser));
      
      return true;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  const value = {
    user,
    isLoading,
    login,
    logout,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export const useUser = () => useContext(UserContext);
