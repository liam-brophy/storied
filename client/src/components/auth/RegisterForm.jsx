import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import './RegisterForm.css';

const RegisterForm = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const validationSchema = Yup.object({
    username: Yup.string()
      .required('Username is required')
      .min(3, 'Username must be at least 3 characters'),
    email: Yup.string()
      .email('Invalid email address')
      .required('Email is required'),
    password: Yup.string()
      .required('Password is required')
      .min(8, 'Password must be at least 8 characters'),
  });

  const initialValues = {
    username: '',
    email: '',
    password: '',
  };

  const handleSubmit = async (values, { setSubmitting, setFieldError }) => {
    try {
      await register(values);
      navigate('/profile');
    } catch (err) {
      // Set the error message in Formik state
      setFieldError('general', err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, errors }) => (
        <Form>
          <h2>Register</h2>
          {/* General error message (if registration fails) */}
          {errors.general && <p style={{ color: 'red' }}>{errors.general}</p>}

          <div>
            <label htmlFor="reg-username">Username:</label>
            <Field type="text" id="reg-username" name="username" />
            <ErrorMessage name="username" component="div" style={{ color: 'red' }} />
          </div>

          <div>
            <label htmlFor="reg-email">Email:</label>
            <Field type="email" id="reg-email" name="email" />
            <ErrorMessage name="email" component="div" style={{ color: 'red' }} />
          </div>

          <div>
            <label htmlFor="reg-password">Password:</label>
            <Field type="password" id="reg-password" name="password" />
            <ErrorMessage name="password" component="div" style={{ color: 'red' }} />
          </div>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Registering...' : 'Register'}
          </button>
        </Form>
      )}
    </Formik>
  );
};

export default RegisterForm;