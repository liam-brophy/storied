// client/src/context/AuthContext.js (Recommended location)
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
// Import the specific API call functions from auth.js
import {
  loginUser,
  registerUser,
  logoutUser,
  getCurrentUser,
  updateUserProfile as updateUserProfileApi // Rename import
} from '../services/api/auth'; // Correct path to your API module
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const checkUserSession = useCallback(async () => {
    setIsLoading(true);
    try {
      // Use the imported axios-based API function
      // It already returns response.data
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (error) {
      // Axios error object has error.response for HTTP errors
      setUser(null);
      // The interceptor already logged the error, but you can add specific handling here
      console.log('No active session or error checking session:', error.response?.data?.error || error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkUserSession();
  }, [checkUserSession]);

  const login = async (credentials) => {
    try {
      // loginUser now uses axios and returns response.data
      const responseData = await loginUser(credentials);
      setUser(responseData.user);
      return responseData; // Contains 'message' and 'user'
    } catch (error) {
      console.error("Login failed context:", error.response?.data || error.message);
      setUser(null);
      // Re-throw the axios error object so components can access response details
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const responseData = await registerUser(userData);
      setUser(responseData.user);
      return responseData;
    } catch (error) {
      console.error("Registration failed context:", error.response?.data || error.message);
      setUser(null);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await logoutUser(); // Axios handles the request
    } catch (error) {
      // Even if logout API fails, log client-side out
      console.error("Logout API call failed context:", error.response?.data || error.message);
    } finally {
      setUser(null);
      navigate('/login');
    }
  };

  const updateUserProfile = async (profileData) => {
    try {
        const responseData = await updateUserProfileApi(profileData); // Uses axios via the import
        setUser(responseData.user);
        return responseData;
    } catch (error) {
        console.error("Profile update failed context:", error.response?.data || error.message);
        throw error;
    }
  };

  // Value provided to consumers
  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateUserProfile,
    checkUserSession
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook remains the same
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};