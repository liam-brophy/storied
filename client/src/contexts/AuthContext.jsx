import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios'; // Import axios directly
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  const checkUserSession = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/users/me');  // Direct axios call
      setUser(response.data); // Access the data directly
    } catch (error) {
      setUser(null);
      console.error('No active session or error checking session:', error.response?.data?.error || error.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkUserSession();
  }, [checkUserSession]);

  const login = async (credentials) => {
    try {
      const response = await axios.post('/api/users/login', credentials); // Direct axios call
      setUser(response.data.user);
      return response.data; // Returns message and user
    } catch (error) {
      console.error("Login failed context:", error.response?.data || error.message);
      setUser(null);
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/users/register', userData); // Direct axios call
      setUser(response.data.user);
      return response.data;
    } catch (error) {
      console.error("Registration failed context:", error.response?.data || error.message);
      setUser(null);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await axios.delete('/api/users/logout'); // Direct axios call
    } catch (error) {
      console.error("Logout API call failed context:", error.response?.data || error.message);
    } finally {
      setUser(null);
      navigate('/login');
    }
  };

  const updateUserProfile = async (profileData) => {
    try {
      const response = await axios.patch('/api/users/profile', profileData); // Direct axios call
      setUser(response.data.user);
      return response.data;
    } catch (error) {
      console.error("Profile update failed context:", error.response?.data || error.message);
      throw error;
    }
  };


  const addFriendtoUser = async (friend_id) =>{
    try{
      const response = await axios.post('/api/users/friends/request', 
          {friend_id}
      ).then(() => {
          if (!response.ok){
              response.json.then((errorObj)=> {
                  setError(errorObj.error)
              })
          } else {
              response.json.then((friendship) => {
              setUser(prevUser => ({...prevUser, sent_friendships:[...prevUser.sent_friendships, friendship]}))  
              })
          }   
      })

} catch (error) {

}
}


  const deleteUser = async () => {
    try {
      await axios.delete('/api/users/delete'); // Adjust your API endpoint as needed
      setUser(null); // Clear user from context
      localStorage.removeItem('token'); // Remove token
      navigate('/'); // Redirect to homepage or login page
    } catch (error) {
      console.error("Error deleting account:", error);
      throw error; // Re-throw the error so the component can handle it
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    updateUserProfile,
    checkUserSession,
    deleteUser,
    addFriendtoUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};