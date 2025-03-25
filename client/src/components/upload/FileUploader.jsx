import React, { useState } from 'react';
import { Upload, AlertCircle } from 'lucide-react';
// import { Alert, AlertDescription } from '@/components/ui/alert';

const StoryUpload = ({ onUpload }) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');

  const processFile = async (file) => {
    if (!file.name.endsWith('.txt')) {
      setError('Please upload a .txt file');
      return;
    }

    try {
      const text = await file.text();
      
      // Generate a unique filename for the content
      const filename = `${file.name.replace(/\s+/g, '-').toLowerCase()}`;
      
      // Create story object matching your data structure
      const newStory = {
        id: `story-${Date.now()}`,
        image: "/placeholder-cover.jpg",
        title: file.name.replace('.txt', ''),
        author: "Unknown",
        contentPath: `/data/${filename}`
      };

      onUpload({ storyData: newStory, content: text });
      setError('');
    } catch (err) {
      setError('Error reading file. Please try again.');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      await processFile(file);
    }
  };

  const handleChange = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      await processFile(file);
    }
  };

  return (
    <div className="story-upload-container">
      <div
        className={`story-upload-dropzone ${dragActive ? 'story-upload-dropzone--active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".txt"
          onChange={handleChange}
          className="story-upload-input"
        />
        
        <Upload className="story-upload-icon" />
        <p className="story-upload-text">
          Drag and drop your story file here, or click to select
        </p>
        <p className="story-upload-subtext">
          Only .txt files are supported
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="story-upload-alert">
          <AlertCircle className="story-upload-alert-icon" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </div>
  );
};

export default StoryUpload;