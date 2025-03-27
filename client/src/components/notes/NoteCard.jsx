import React, { useState } from "react"; // Correct React import
import { IconButton, TextField, Button } from "@mui/material";
import { Edit, Delete, Save, Cancel } from "@mui/icons-material";
import apiClient from "../../services/api/axios"; // Adjust path as needed

// Assume the note object now looks like:
// { id: 1, excerpt: "...", page_number: 5, comment: "...", book_id: 12, book_title: "Example Book", ... }

const NoteCard = ({ note, onDelete, onUpdate }) => {
  // State for managing edit mode and the edited comment text
  const [isEditing, setIsEditing] = useState(false);
  const [editComment, setEditComment] = useState(note.comment || ''); // Initialize with current comment
  const [error, setError] = useState(null); // Local error state for edit/delete actions
  const [isProcessing, setIsProcessing] = useState(false); // State for disabling buttons during API calls

  // --- Event Handlers ---

  // Enter Edit Mode
  const handleEnterEdit = () => {
    setEditComment(note.comment || ''); // Reset edit field to current comment
    setError(null); // Clear any previous errors
    setIsEditing(true);
  };

  // Cancel Edit Mode
  const handleCancelEdit = () => {
    setIsEditing(false);
    setError(null); // Clear error on cancel
    // No need to reset editComment state here, handleEnterEdit does it next time
  };

  // Save Edited Note (API Call)
  const handleSaveEdit = async () => {
    if (editComment === note.comment) {
        // No change, just exit edit mode
        setIsEditing(false);
        return;
    }

    setError(null);
    setIsProcessing(true);
    try {
      const response = await apiClient.patch(`/notes/${note.id}`, { comment: editComment });
      // Call the onUpdate prop passed from NotesPage with the updated note data from API
      onUpdate(response.data);
      setIsEditing(false); // Exit edit mode on successful save
    } catch (err) {
      const errorMsg = err.response?.data?.error || "Failed to save note.";
      console.error("Error updating note:", errorMsg, err);
      setError(errorMsg); // Set local error to display to user
      // Optional: alert(`Error: ${errorMsg}`);
    } finally {
       setIsProcessing(false);
    }
  };

  // Delete Note (API Call)
  const handleDelete = async () => {
    // Use the onDelete prop directly passed from NotesPage, which handles confirmation and API call
     setError(null); // Clear local error before attempting delete
    try {
        setIsProcessing(true); // Disable buttons while deleting
        await onDelete(note.id); // Call parent's delete handler
        // No need to do anything else here, parent manages state
    } catch (err) {
        // This catch might not be strictly necessary if parent handles errors,
        // but can be useful for local feedback
        const errorMsg = err.message || "Failed to initiate delete.";
        console.error("Error during delete initiation in NoteCard:", errorMsg, err);
        setError(errorMsg);
        setIsProcessing(false); // Re-enable buttons if parent's call failed before disabling
    }
    // No finally needed here if parent always handles the processing state
  };


  // --- Data for Display ---
  // Use optional chaining and fallbacks for safety
  const bookTitle = note.book_title || "Unknown Book";
  // const bookAuthor = note.book_author || "Unknown Author"; // If available
  const excerptText = note.excerpt || "";
  const truncatedExcerpt = excerptText.length > 50 ? excerptText.slice(0, 50) + "..." : excerptText;
  const pageNum = note.page_number;

  return (
    // Use the same container class as before
    <div className="note-card-container">
      {/* Apply theme classes or styles if needed */}
      <div className="note-card">
        <div className="note-content">
          <div className="note-header">
             {/* Display Book Title */}
            <span className="note-story-title">{bookTitle}</span>
            {/* Display Page Number if available */}
            {pageNum && <span className="note-page-number">p. {pageNum}</span>}
          </div>

          {/* Display Excerpt if available */}
          {truncatedExcerpt && (
            <div className="note-excerpt">
                <p>"{truncatedExcerpt}"</p>
            </div>
          )}


          {isEditing ? (
            // --- Edit State ---
            <div className="note-edit-section">
              <TextField
                fullWidth
                multiline
                variant="outlined"
                label="Edit Comment"
                value={editComment}
                onChange={(e) => setEditComment(e.target.value)}
                disabled={isProcessing}
                error={!!error} // Show error state on TextField
                helperText={error} // Display error message below TextField
                className="note-edit-textarea" // Use class from CSS
              />
            </div>
          ) : (
             // --- View State ---
             <div className="note-comment">
                <p>{note.comment || <i>No comment added.</i>}</p>
             </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="note-actions">
          {isEditing ? (
            <>
              <Button
                className="save-button"
                variant="contained" // Keep MUI styling
                size="small"
                startIcon={<Save />}
                onClick={handleSaveEdit}
                disabled={isProcessing} // Disable while saving
              >
                Save
              </Button>
              <Button
                className="cancel-button"
                size="small"
                startIcon={<Cancel />}
                onClick={handleCancelEdit}
                disabled={isProcessing} // Disable if processing (though less critical for cancel)
              >
                Cancel
              </Button>
            </>
          ) : (
            <>
              <IconButton
                className="edit-button"
                size="small"
                onClick={handleEnterEdit}
                aria-label="Edit note"
                disabled={isProcessing}
              >
                <Edit fontSize="small"/>
              </IconButton>
              <IconButton
                className="delete-button"
                size="small"
                onClick={handleDelete} // Call the local handler that calls the prop
                aria-label="Delete note"
                disabled={isProcessing}
              >
                <Delete fontSize="small"/>
              </IconButton>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default NoteCard;