import React, { createContext, useState, useEffect } from "react";

export const StoriesContext = createContext();

export const StoriesProvider = ({ children }) => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch initial stories
  useEffect(() => {
    const fetchStories = async () => {
      try {
        const response = await fetch("http://localhost:3001/stories");
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setStories(data);
      } catch (error) {
        console.error("Error fetching stories:", error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStories();
  }, []);

  const addStory = async (storyData, content) => {
    try {
      // First, save the content file
      const contentResponse = await fetch("http://localhost:3001/content", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          path: storyData.contentPath,
          content: content 
        }),
      });

      if (!contentResponse.ok) {
        throw new Error("Failed to save story content");
      }

      // Then save the story metadata
      const storyResponse = await fetch("http://localhost:3001/stories", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(storyData),
      });

      if (!storyResponse.ok) {
        throw new Error("Failed to save story metadata");
      }

      const savedStory = await storyResponse.json();
      setStories(prevStories => [...prevStories, savedStory]);
      
      return savedStory;
    } catch (error) {
      console.error("Error adding story:", error);
      throw error;
    }
  };

  const contextValue = {
    stories,
    loading,
    error,
    addStory,
  };

  return (
    <StoriesContext.Provider value={contextValue}>
      {children}
    </StoriesContext.Provider>
  );
};