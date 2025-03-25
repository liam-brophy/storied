import { useState } from "react";
import { IconButton, TextField, Button } from "@mui/material";
import { Edit, Delete, Save, Cancel } from "@mui/icons-material";


const NoteCard = ({ note, setNotes, stories }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [updatedComment, setUpdatedComment] = useState(note.comment);

  const handleEditNote = () => {
    fetch(`http://localhost:3001/notes/${note.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ comment: updatedComment }),
    })
      .then((response) => {
        if (response.ok) {
          setNotes((prevNotes) =>
            prevNotes.map((n) =>
              n.id === note.id ? { ...n, comment: updatedComment } : n
            )
          );
          setIsEditing(false);
        } else {
          console.error("Failed to edit the note. Response status:", response.status);
        }
      })
      .catch((error) => console.error("Error during PATCH request:", error));
  };

  const handleDeleteNote = (noteId) => {
    fetch(`http://localhost:3001/notes/${noteId}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    })
      .then((response) => {
        if (response.ok) {
          setNotes((prevNotes) => prevNotes.filter((note) => note.id !== noteId));
        } else {
          console.error("Failed to delete the note. Response status:", response.status);
        }
      })
      .catch((error) => console.error("Error during DELETE request:", error));
  };



  const story = stories.find((story) => story.id === note.story);
  const storyTitle = story?.title || "Unknown Story";
  const storyAuthor = story?.author || "Unknown Author";
  const truncatedText = note.text.length > 50 ? note.text.slice(0, 50) + "..." : note.text;

  return (
    <div className="note-card-container">
      <div className="note-card">
        <div className="note-content">
          <div className="note-header">
            <p className="note-story-title">{storyTitle}</p>
            <p className="note-story-author">{storyAuthor}</p>
          </div>

          <div className="note-text">
            <p className="note-page-number">
              page {note.page} | "{truncatedText}"
            </p>
          </div>

          {isEditing ? (
            <>
              <TextField
                fullWidth
                multiline
                variant="outlined"
                value={updatedComment}
                onChange={(e) => setUpdatedComment(e.target.value)}
              />
            </>
          ) : (
            <div className="note-comment">
            <p>{note.comment}</p>
            </div>
          )}
        </div>

        <div className="note-actions">
          {isEditing ? (
            <>
              <Button
                className="save-button"
                variant="contained"
                startIcon={<Save />}
                onClick={handleEditNote}
              >
                Save
              </Button>
              <Button
                className="cancel-button"
                startIcon={<Cancel />}
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </Button>
            </>
          ) : (
            <>
              <IconButton className="edit-button" onClick={() => setIsEditing(true)}>
                <Edit />
              </IconButton>
              <IconButton className="delete-button" onClick={() => handleDeleteNote(note.id)}>
                <Delete />
              </IconButton>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default NoteCard;