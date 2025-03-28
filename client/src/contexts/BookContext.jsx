import React, { createContext, useState, useEffect, useContext } from "react";
import apiClient from '../services/api/axios'; // <-- Import the configured Axios instance
import { useAuth } from './AuthContext'; // <-- Import useAuth to check login status

export const BooksContext = createContext();

export const BooksProvider = ({ children }) => {
  const [books, setBooks] = useState([]);
  const [isLoading, setIsLoading] = useState(false); // <-- Add loading state
  const [error, setError] = useState(null); // <-- Add error state
  const { isAuthenticated } = useAuth(); // <-- Get authentication status

  // Define fetchBooks function (can be called manually later if needed)
  const fetchBooks = async () => {
    // Don't fetch if not authenticated
    if (!isAuthenticated) {
        setBooks([]); // Ensure books are cleared if user logs out
        return;
    }

    setIsLoading(true);
    setError(null);
    console.log("BookContext: Attempting to fetch books (User is authenticated)"); // Debug log

    try {
      // Use Axios instance (baseURL '/api' is already set)
      const response = await apiClient.get('/books'); // <-- Fetch from '/api/books'
      setBooks(response.data || []); // Set books, default to empty array if data is null/undefined
    } catch (err) {
      console.error("BookContext: Failed to fetch books:", err.response?.data || err.message);
      // Set error state for components to potentially display
      setError(err.response?.data?.error || 'Failed to load books.');
      setBooks([]); // Clear books on error
    } finally {
      setIsLoading(false);
    }
  };

  // useEffect to fetch books only when authentication status changes to true
  useEffect(() => {
    if (isAuthenticated) {
      fetchBooks();
    } else {
      // Clear books and error state if the user logs out or is not authenticated
      setBooks([]);
      setError(null);
      setIsLoading(false); // Ensure loading is reset
    }
    // Re-run this effect whenever 'isAuthenticated' changes
  }, [isAuthenticated]);

  const addBook = (newBook) => {
    // Function to add a new book to the state
    setBooks((prevBooks) => [...prevBooks, newBook]);
  };

  // Value provided by the context
  const contextValue = {
    books,
    isLoading,
    error,
    addBook,
    fetchBooks // Expose fetchBooks in case a component needs to trigger a manual refresh
  };




  return (
    <BooksContext.Provider value={contextValue}>
      {children}
    </BooksContext.Provider>
  );
};