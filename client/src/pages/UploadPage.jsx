import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { StoriesContext } from '../StoriesContext';
import StoryUpload from './StoryUpload';

const UploadPage = () => {
  const navigate = useNavigate();
  const { addStory } = useContext(StoriesContext);

  const handleUpload = async ({ storyData, content }) => {
    try {
      const response = await fetch("http://localhost:3001/stories", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ storyData, content }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const newStory = await response.json();
      addStory(newStory);
      navigate('/'); // Redirect to home page after successful upload
    } catch (error) {
      console.error('Failed to upload story:', error);
    }
  };

  return (
    <div className="upload-page">
      <h1 className="upload-page-title">Upload a New Story</h1>
      <StoryUpload onUpload={handleUpload} />
    </div>
  );
};

export default UploadPage;