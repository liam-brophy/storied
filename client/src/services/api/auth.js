import apiClient from './axios'; // Import the configured axios instance

// Matches POST /api/users/register
// Axios automatically stringifies the userData object to JSON
export const registerUser = async (userData) => {
  const response = await apiClient.post('/users/register', userData);
  return response.data; // Axios wraps the response body in 'data'
};

// Matches POST /api/users/login
export const loginUser = async (credentials) => {
  const response = await apiClient.post('/users/login', credentials);
  return response.data;
};

// Matches DELETE /api/users/logout
export const logoutUser = async () => {
  // For DELETE, usually no request body. Axios handles this.
  // Backend returns 204 No Content, axios won't throw an error for 2xx.
  const response = await apiClient.delete('/users/logout');
  // response.data will likely be empty for 204, which is fine.
  return response; // Return the full response or response.status if needed
};

// Matches GET /api/users/me
export const getCurrentUser = async () => {
  const response = await apiClient.get('/users/me');
  return response.data;
};

// Matches GET /api/users/profile (Using /me as discussed before)
export const getUserProfile = async () => {
   const response = await apiClient.get('/users/me');
   return response.data;
};

// Matches PUT /api/users/profile
export const updateUserProfile = async (profileData) => {
  const response = await apiClient.put('/users/profile', profileData);
  return response.data;
};