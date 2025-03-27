import React from "react";
import '../index.css';

const BookCard = ({ book }) => { //Renamed story to book
  return (
    <div className="storyCard"> {/*No onClick anymore*/}
      <img className="storyCover" src={book.image} alt={book.title} /> {/* Access book.image */}
      <div className="bookInfo"> {/* Renamed storyInfo to bookInfo */}
        <h2 className="bookTitle" >{book.title}</h2> {/* Renamed storyTitle to bookTitle */}
        <p className="bookAuthor" >{book.author}</p> {/* Renamed storyAuthor to bookAuthor */}
      </div>
    </div>
  );
};

export default BookCard;