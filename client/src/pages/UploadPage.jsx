import React from 'react';
import FileUploader from '../components/upload/FileUploader';
import './UploadPage.css'; // Import the CSS

const UploadPage = () => {
  return (
    <div className="upload-page">
      <h1 className="upload-page-title">Book Upload</h1>
      <div className="file-uploader">
        <FileUploader />
      </div>
    </div>
  );
};

export default UploadPage;