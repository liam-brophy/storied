import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';

const LoginForm = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/profile'; // Redirect after login

  const validationSchema = Yup.object({
    identifier: Yup.string()
      .required('Username or Email is required'),
    password: Yup.string()
      .required('Password is required'),
  });

  const initialValues = {
    identifier: '',
    password: '',
  };

  const handleSubmit = async (values, { setSubmitting, setFieldError }) => {
    const isEmail = values.identifier.includes('@');
    const credentials = isEmail
      ? { email: values.identifier, password: values.password }
      : { username: values.identifier, password: values.password };

    try {
      await login(credentials);
      navigate(from, { replace: true });
    } catch (err) {
      setFieldError('general', err.response?.data?.error || 'Login failed. Please check your credentials.');
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
          <h2>Login</h2>
          {errors.general && <p style={{ color: 'red' }}>{errors.general}</p>} {/* General error */}

          <div>
            <label htmlFor="identifier">Username or Email:</label>
            <Field type="text" id="identifier" name="identifier" />
            <ErrorMessage name="identifier" component="div" style={{ color: 'red' }} />
          </div>

          <div>
            <label htmlFor="password">Password:</label>
            <Field type="password" id="password" name="password" />
            <ErrorMessage name="password" component="div" style={{ color: 'red' }} />
          </div>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
        </Form>
      )}
    </Formik>
  );
};

export default LoginForm;