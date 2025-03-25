import React, { createContext, useState, useEffect } from "react";

export const BooksContext = createContext();

export const BooksProvider = ({ children }) => {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    const fetchBooks = async () => {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/books`);
      const data = await response.json();
      setBooks(data);
    };

    fetchBooks();
  }, []);

  return (
    <BooksContext.Provider value={{ books }}>
      {children}
    </BooksContext.Provider>
  );
};