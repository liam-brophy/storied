import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { BooksProvider } from "./contexts/BookContext";
import { AuthProvider } from "./contexts/AuthContext";
import Layout from "./components/app/Layout/Layout";
import BookList from "./components/books/BookList";
import BookContent from "./components/books/BookContent";
import LoginForm from "./components/auth/LoginForm";
import UploadPage from './pages/UploadPage';
import "./index.css";

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BooksProvider>
          <Router>
            <Routes>
            <Route path="/" element={<Layout />} />
              <Route path="/books" element={<BookList />} />
              <Route path="/books/:id" element={<BookContent />} />
              <Route path="/login" element={<LoginForm />} />
              <Route path="/upload" element={<UploadPage />} />
            </Routes>
          </Router>
        </BooksProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;