import React, { useContext } from "react";
import { BooksContext } from "../../contexts/BookContext";
import "../../index.css";

const BookList = () => {
  const { books } = useContext(BooksContext);

  if (!books || books.length === 0) {
    return <p>No books found</p>;
  }

  return (
    <div className="bookList">
      {books.map((book) => (
        <div key={book.id} className="bookCard">
          <h3>{book.title}</h3>
          <p>{book.author}</p>
          {/* You can add additional information or actions for each book */}
        </div>
      ))}
    </div>
  );
};

export default BookList;