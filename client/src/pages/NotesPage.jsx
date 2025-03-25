import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import NoteCard from "./NoteCard";
import SearchBar from "./SearchBar";

const Notes = () => {
  const { storyId } = useParams(); // Capture story ID from URL
  const [notes, setNotes] = useState([]);
  const [searchQuery, setSearchQuery] = useState("")
  // const [filteredNotes, setFilteredNotes] = useState([]);
  const [stories, setStories] = useState([]); // Store stories separately
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch both notes and stories
        const [notesResponse, storiesResponse] = await Promise.all([
          fetch("http://localhost:3001/notes"),
          fetch("http://localhost:3001/stories"),
        ]);

        if (!notesResponse.ok || !storiesResponse.ok) {
          throw new Error("Failed to fetch data");
        }

        const notesData = await notesResponse.json();
        const storiesData = await storiesResponse.json();

        setStories(storiesData); // Store stories

        if (storyId) {
          // Filter notes by story ID if present
          const filteredNotes = notesData.filter(note => note.story === storyId);
          setNotes(filteredNotes);
          // setFilteredNotes(filteredNotes);
          // setFilteredNotes(notesData);
        } else {
          setNotes(notesData);
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [storyId]); // Re-run when storyId changes

  const handleSearch = (query) => {
    setSearchQuery(query) 
  };

  const filteredNotes = notes.filter((note) =>
    note.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
    note.page.toString().includes(searchQuery) || note.comment.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) return <div>Loading notes...</div>;

  if (notes.length === 0) return <div>No notes available for this story</div>; //"Make some notes!" -> link elsewhere

  return (
    <div>
      <SearchBar onSearch={handleSearch} />
      <div className="notes-container">
        {filteredNotes.map((note) => (
          <NoteCard key={note.id} note={note} setNotes={setNotes} stories={stories} />
        ))}
      </div>
    </div>
  );
};

export default Notes;