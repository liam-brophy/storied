import React from "react";
import StoryCard from "./StoryCard";
import StoryUpload from "./StoryUpload"
import '../index.css';

const StoryList = ({ stories, handleUpload}) => {

  return (
<div className="storyList">
      {stories.length === 0 ? (
        <p>No stories found</p>
      ) : (
        stories.map((story) => (
          <StoryCard key={story.id} story={story} />
        ))
      )}
      {/* <StoryUpload onUpload={handleUpload} /> */}
    </div>
  );
};

export default StoryList;