import React from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

const FileUploader = () => {
  const validationSchema = Yup.object({
    file: Yup.mixed()
      .required("File is required")
      .test(
        "fileSize",
        "File size is too large (max 5MB)",
        value => value && value.size <= 1024 * 1024 * 5 // 5MB
      )
      .test(
        "fileType",
        "Unsupported file type (only PDF)",
        value => value && ['application/pdf'].includes(value.type) // Example: Allow only PDF
      ),
      title: Yup.string()
      .required("Book Title is Required"),
      author: Yup.string()
      .required("Author Name is Required")
  });

  const initialValues = {
    file: null,
    title: '',
    author: ''
  };

  const handleSubmit = (values, { setSubmitting, resetForm }) => {
    // Handle form submission here
    console.log(values);

    // Simulate an upload process
    setTimeout(() => {
      alert(JSON.stringify(values, null, 2));
      setSubmitting(false);
      resetForm();
    }, 2000);
  };

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
    >
      {({ isSubmitting, setFieldValue, values }) => (
        <Form>
          <div className="form-group">
            <label htmlFor="title">Book Title:</label>
            <Field type="text" id="title" name="title" className="form-control" />
            <ErrorMessage name="title" component="div" className="error-message" />
          </div>

          <div className="form-group">
            <label htmlFor="author">Author:</label>
            <Field type="text" id="author" name="author" className="form-control" />
            <ErrorMessage name="author" component="div" className="error-message" />
          </div>

          <div className="form-group">
            <label htmlFor="file">Choose File (PDF):</label>
            <input
              type="file"
              id="file"
              name="file"
              className="form-control-file"
              onChange={(event) => {
                setFieldValue("file", event.currentTarget.files[0]);
              }}
            />
            <ErrorMessage name="file" component="div" className="error-message" />
            {values.file && <p>Selected File: {values.file.name}</p>}
          </div>

          <button type="submit" disabled={isSubmitting} className="btn btn-primary">
            {isSubmitting ? 'Uploading...' : 'Upload'}
          </button>
        </Form>
      )}
    </Formik>
  );
};

export default FileUploader;