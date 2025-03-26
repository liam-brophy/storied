import React from 'react';
import FileUploader from '../components/upload/FileUploader';

const UploadPage = () => {
  return (
    <div className="upload-page">
      <h1 className="upload-page-title">Book Upload</h1>
      <FileUploader />
    </div>
  );
};

export default UploadPage;