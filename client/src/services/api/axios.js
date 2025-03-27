// client/src/services/api/axios.js
import axios from 'axios';

const BASE_URL = '/api'; // Your Flask API prefix

// Create an axios instance with default configuration
const apiClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // VERY IMPORTANT: Allows sending session cookies
  headers: {
    'Content-Type': 'application/json', // Default content type for POST/PUT etc.
    'Accept': 'application/json',       // We expect JSON responses
  },
});

// --- Optional but Recommended: Interceptors ---

// Request Interceptor (Example: could be used for logging or adding auth tokens later)
apiClient.interceptors.request.use(
  (config) => {
    // You could modify the config here before the request is sent
    // console.log('Starting Request', config);
    return config;
  },
  (error) => {
    // Handle request error
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// Response Interceptor (Example: Centralized logging or error handling)
apiClient.interceptors.response.use(
  (response) => {
    // Any status code within the range of 2xx causes this function to trigger
    // console.log('Response Received:', response);
    // Often, you might just want to return response.data directly from here,
    // but returning the full response gives more flexibility in the calling function.
    return response;
  },
  (error) => {
    // Any status codes outside the range of 2xx cause this function to trigger
    console.error('API Error Interceptor:', error.response || error.message);

    // You could add global error handling here, e.g.:
    // if (error.response && error.response.status === 401) {
    //   // Trigger logout or redirect to login
    //   console.log('Unauthorized, logging out...');
    //   // Potentially call logout function from auth context here (more complex setup)
    //   window.location.href = '/login'; // Simple redirect
    // }

    // IMPORTANT: Reject the promise so the error can be caught by the calling function's .catch()
    return Promise.reject(error);
  }
);

export default apiClient; // Export the configured instance