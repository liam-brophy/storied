import React from "react";
// Make sure BrowserRouter is imported as Router
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { BooksProvider } from "./contexts/BookContext";
import { AuthProvider } from "./contexts/AuthContext"; // Check path
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import UploadPage from './pages/UploadPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './components/auth/ProtectedRoute'; // Check path
import Layout from "./components/app/Layout/Layout"; // Check path
import BookList from "./components/books/BookList"; // Check path
import BookContent from "./components/books/BookContent"; // Check path
// import HomePage from './pages/HomePage';
import NotesPage from './pages/NotesPage';
import PdfReaderView from './components/reader/PdfReaderView'; // Check path

import "./index.css";

function App() {
  return (
    // 1. Router should be the outermost component related to routing
    <Router>
      {/* 2. Context Providers can now be inside Router */}
      <ThemeProvider>
        <AuthProvider> {/* AuthProvider is now a child of Router */}
          <BooksProvider>
            {/* 3. Routes component renders the specific page components */}
            <Routes>
              {/* Routes WITH the Layout */}
              <Route path="/" element={<Layout />}>
              {/*<TestPdfViewer /> REMOVED HERE*/}
                 <Route index element={<Navigate to="/books" replace />} />
                <Route path="books" element={<BookList />} />
                <Route path="books/:id" element={<BookContent />} />
                <Route path="reader/:bookId" element={<PdfReaderView />} />
                <Route
                  path="notes" // Relative path -> /notes
                  element={
                    <ProtectedRoute>
                      <NotesPage /> {/* Render NotesPage Component */}
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="upload"
                  element={<ProtectedRoute><UploadPage /></ProtectedRoute>}
                />
                <Route
                  path="profile"
                  element={<ProtectedRoute><ProfilePage /></ProtectedRoute>}
                />
                <Route path="*" element={<NotFoundPage />} />
              </Route>

              {/* Routes WITHOUT the Layout */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Routes>
          </BooksProvider>
        </AuthProvider>
      </ThemeProvider>
    </Router> // Router closes here
  );
}

export default App;