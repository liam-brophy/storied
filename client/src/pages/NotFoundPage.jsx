import React from 'react';
import { Link } from 'react-router-dom';
import './NotFoundPage.css'; // <-- Import the CSS file

const NotFoundPage = () => {
  return (
    // Use className instead of style prop
    <div className="not-found-container">
      <h2 className="not-found-heading">404 - Page Not Found</h2>
      <p className="not-found-message">
        Oops! The page you are looking for doesn't seem to exist.
      </p>
      <Link to="/" className="not-found-link">
        Go Back Home
      </Link>
    </div>
  );
};

export default NotFoundPage;