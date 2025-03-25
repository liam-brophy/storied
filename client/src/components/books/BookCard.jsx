import React from "react";
import '../index.css';
import { useNavigate } from "react-router-dom";

const BookCard = ({ story }) => {
  const navigate = useNavigate();

  const handleReadStory = () => {
    navigate(`/reader/${story.id}`);
  };

  return (
    <div onClick={handleReadStory} className="storyCard">
      <img className="storyCover" src={story.image}></img>
      <div className="storyInfo">
        <h2 className="storyTitle" >{story.title}</h2>
        <p className="storyAuthor" >{story.author}</p>
      </div>
    </div>
  );
};

export default BookCard;