import React, { useEffect, useState, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext"; // Adjust path
import apiClient from "../services/api/axios"; // Adjust path
import NoteCard from "../components/notes/NoteCard"; // Adjust path
import SearchBar from "../components/app/Layout/SearchBar"; // Adjust path
import "./Notes.css"; // Import the specific CSS

const NotesPage = () => {
  const { bookId } = useParams(); // Use bookId instead of storyId for clarity
  const { isAuthenticated } = useAuth();

  const [notes, setNotes] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    // Function to fetch notes
    const fetchNotes = async () => {
      // Don't fetch if not authenticated
      if (!isAuthenticated) {
        setNotes([]); // Clear notes if logged out
        console.log("NotesPage: User is not authenticated, clearing notes.");
        return;
      }

      setIsLoading(true);
      setError(null);
      console.log("NotesPage: Attempting to fetch notes...");

      // Determine API endpoint (filter by bookId if provided)
      let apiUrl = "/notes";
      if (bookId) {
        apiUrl += `?book_id=${bookId}`;
        console.log(`NotesPage: Fetching notes for book ID: ${bookId}`);
      } else {
        console.log("NotesPage: Fetching all notes");
      }

      console.log("NotesPage: API URL:", apiUrl); // Log apiUrl

      try {
        const response = await apiClient.get(apiUrl);
        console.log("NotesPage: API Response:", response); // Log the entire response
        console.log("NotesPage: API Response Data:", response.data); // Log response.data
        console.log("NotesPage: API Response Data or []:", response.data || []); //Log data or empty array

        setNotes(response.data || []); // Set notes, default to empty array
      } catch (err) {
        console.error("NotesPage: Failed to fetch notes:", err.response?.data || err.message);
        setError(err.response?.data?.error || 'Failed to load notes.');
        setNotes([]); // Clear notes on error
      } finally {
        setIsLoading(false);
      }
    };

    console.log("NotesPage: useEffect triggered - isAuthenticated:", isAuthenticated, "bookId:", bookId); //Log when useEffect is triggered.
    fetchNotes();
    // Re-run effect if authentication status or bookId changes
  }, [isAuthenticated, bookId]);

  // --- Search Functionality ---
  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  // Memoize filtered notes to avoid recalculating on every render unless notes or searchQuery change
  const filteredNotes = useMemo(() => {
    if (!searchQuery) {
      return notes; // No query? Return all notes
    }
    const lowerCaseQuery = searchQuery.toLowerCase();
    return notes.filter((note) =>
      (note.excerpt && note.excerpt.toLowerCase().includes(lowerCaseQuery)) ||
      (note.page_number && note.page_number.toString().includes(lowerCaseQuery)) || // Check if page_number exists
      (note.comment && note.comment.toLowerCase().includes(lowerCaseQuery))
      // Add other fields to search if needed (e.g., book title if included in note data)
    );
  }, [notes, searchQuery]); // Recalculate only when notes or searchQuery changes

  // --- Render Logic ---
  if (isLoading) {
    return <div className="loading-indicator">Loading notes...</div>; // Use CSS class
  }

  if (error) {
    return <div className="error-message">Error loading notes: {error}</div>; // Use CSS class
  }

  // Function to handle note deletion (passed to NoteCard)
  const handleDeleteNote = async (idToDelete) => {
      if (!window.confirm("Are you sure you want to delete this note?")) return;

      try {
          console.log(`NotesPage: Deleting note ${idToDelete}`);
          await apiClient.delete(`/notes/${idToDelete}`);
          // Remove the note from the local state without re-fetching
          setNotes(currentNotes => currentNotes.filter(note => note.id !== idToDelete));
      } catch (err) {
          console.error(`NotesPage: Failed to delete note ${idToDelete}:`, err.response?.data || err.message);
          // Optionally show an error message to the user
          alert(`Error deleting note: ${err.response?.data?.error || err.message}`);
      }
  };

  // Function to handle note update (passed to NoteCard)
  // This assumes NoteCard handles the editing UI and calls this function with the updated data
  const handleUpdateNote = (updatedNote) => {
      setNotes(currentNotes =>
          currentNotes.map(note =>
              note.id === updatedNote.id ? updatedNote : note
          )
      );
  };


  return (
    <div className="notes-page-container"> {/* Add a wrapper if needed for page padding */}
      <SearchBar onSearch={handleSearch} />

      {filteredNotes.length === 0 ? (
        <div className="no-notes-message"> {/* Use CSS class */}
          {searchQuery ? "No notes match your search." : (bookId ? "No notes found for this book." : "You haven't created any notes yet.")}
          {/* Optional: Add link to books page or upload page */}
        </div>
      ) : (
        <div className="notes-container"> {/* Use class from your CSS */}
          {filteredNotes.map((note) => (
            <NoteCard
                key={note.id}
                note={note}
                onDelete={handleDeleteNote} // Pass delete handler
                onUpdate={handleUpdateNote} // Pass update handler
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default NotesPage;