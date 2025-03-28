import React from 'react';
import { Link } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';
import './RegisterPage.css'; // Import CSS

const RegisterPage = () => {
  return (
    <div className="register-page">
      <div className="register-container">
        <RegisterForm />
        <p>
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;