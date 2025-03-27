// client/src/components/app/Layout/Layout.jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import NavBar from './NavBar'; // Your existing NavBar
import Footer from './Footer'; // Import the new Footer component

// Basic styles for layout structure - Move to CSS using classNames
const layoutStyle = {
  display: 'flex',
  flexDirection: 'column', // Arrange children vertically (NavBar, Main, Footer)
  minHeight: '100vh',      // Ensure layout takes at least the full viewport height
};

const mainContentStyle = {
  flexGrow: 1, // Allow the main content area to expand and fill available space
  padding: '1rem', // Add some padding around the page content (adjust as needed)
  // You might add width constraints or centering styles here or in CSS
};

const Layout = () => {
  return (
    <div style={layoutStyle} className="app-layout"> {/* Use className for CSS */}
      <NavBar />

      {/* The main content area where child routes will be rendered */}
      <main style={mainContentStyle} className="main-content">
        <Outlet /> {/* Child route component renders here */}
      </main>

      {/* Render the Footer component at the bottom */}
      <Footer />
    </div>
  );
};

export default Layout;