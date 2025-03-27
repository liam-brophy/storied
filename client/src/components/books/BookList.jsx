import React from 'react';
import { Link } from 'react-router-dom'; // Import Link for navigation
import { useBooks } from '../../hooks/useBooks'; // Import the custom hook
import './BookList.css'

const BookList = () => {
    // Use the custom hook to access context state AND loading/error states
    const { books, isLoading, error } = useBooks();

    // 1. Handle Loading State
    if (isLoading) {
        // You can customize this loading indicator
        return <div className="loading-indicator">Loading your books...</div>;
    }

    // 2. Handle Error State
    if (error) {
        // You can customize this error display
        return <div className="error-message">Error loading books: {error}</div>;
    }

    // 3. Handle No Books State (after loading and no error)
    if (!books || books.length === 0) {
        return (
            <div className="no-books-message"> {/* Added a class for styling */}
                <p>No books found.</p>
                <p>
                    Ready to start reading? <Link to="/upload">Upload your first book!</Link>
                </p>
            </div>
        );
    }

    // 4. Render Book List using the desired structure and class names
    return (
        <div className="bookList"> {/* Use the class name from your original */}
            <h2>My Books</h2> {/* Added a heading */}
            {books.map((book) => (
                // Wrap the entire card in a Link to make it clickable
                <Link to={`/books/${book.id}`} key={book.id} className="bookCardLink"> {/* Added key here, and a className */}
                    <div className="bookCard"> {/* Use the class name from your original */}
                        {/* Make title potentially clickable too, or rely on card link */}
                        <h3>{book.title || 'Untitled Book'}</h3>
                        <p>{book.author || 'Unknown Author'}</p>
                        {/* You can add additional information or actions for each book here */}
                        {/* e.g., <p>Genre: {book.genre}</p> */}
                    </div>
                </Link>
            ))}
        </div>
    );
};

export default BookList;