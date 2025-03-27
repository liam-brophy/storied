import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { Slider } from "@mui/material";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import CommentBankIcon from '@mui/icons-material/CommentBank';
import { useCallback } from "react";
import './CommentPopover.css'

const ReaderView = () => {
  const { storyId } = useParams();
  const [story, setStory] = useState(null);
  const [storyContent, setStoryContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [showPopover, setShowPopover] = useState(false);
  const [popoverPosition, setPopoverPosition] = useState({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState("");
  const [commentText, setCommentText] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [pageContent, setPageContent] = useState("");
  const [fontSize, setFontSize] = useState(16);
  const [totalPages, setTotalPages] = useState(0);
  const contentRef = useRef(null);
  const popoverRef = useRef(null);

  useEffect(() => {
    const fetchStoryData = async () => {
      try {
        const response = await fetch(
          `http://localhost:3001/stories/${storyId}`
        );
        if (!response.ok) throw new Error("Story not found");

        const data = await response.json();
        setStory(data);

        const storyResponse = await fetch(data.contentPath);
        if (!storyResponse.ok) throw new Error("Content not found");

        const text = await storyResponse.text();
        setStoryContent(text);
      } catch (error) {
        console.error("Error fetching story content:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStoryData();
  }, [storyId]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popoverRef.current && !popoverRef.current.contains(event.target)) {
        setShowPopover(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const getHighlightedText = () => {
    const selection = window.getSelection();
    return selection ? selection.toString() : "";
  };

  const handleTextSelection = () => {
    const text = getHighlightedText();
    if (text) {
      const rect = window.getSelection().getRangeAt(0).getBoundingClientRect();
      setPopoverPosition({ x: rect.x, y: rect.y });
      setSelectedText(text);
      setShowPopover(true);
    }
  };

  const handleSaveComment = async () => {
    const newComment = {
      text: selectedText,
      comment: commentText,
      page: currentPage + 1,
      story: storyId,
    };
    try {
      await fetch(`http://localhost:3001/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newComment),
      });
      setShowPopover(false);
    } catch (error) {
      console.error("Error saving comment:", error);
    }
  };

  const getCharactersPerPage = useCallback(() => {
    if (!contentRef.current) return 2000;

    const { clientWidth: width, clientHeight: height } = contentRef.current;
    const computedStyle = window.getComputedStyle(contentRef.current);
    const lineHeight = parseFloat(computedStyle.lineHeight) || fontSize * 1.2;
    const charWidth = fontSize * 0.55; // Adjusted estimate

    // Calculate how many lines fit on the page
    const linesPerPage = Math.floor(height / lineHeight);
    const charsPerLine = Math.floor(width / charWidth);

    // Split the story content into lines, accounting for newlines
    const textLines = storyContent.split("\n");

    // Calculate the total number of characters that will fit on the page
    // We count up to the number of lines that can fit on the page and then sum the characters of each line.
    let charsOnPage = 0;
    for (let i = 0; i < Math.min(linesPerPage, textLines.length); i++) {
      charsOnPage += Math.min(textLines[i].length, charsPerLine);
    }

    return charsOnPage; // Total number of characters per page
  }, [fontSize, storyContent]); // Include storyContent and fontSize in dependency array

  useEffect(() => {
    if (storyContent.length && contentRef.current) {
      const charsPerPage = getCharactersPerPage();
      setTotalPages(Math.ceil(storyContent.length / charsPerPage));
      setPageContent(
        storyContent.slice(
          currentPage * charsPerPage,
          (currentPage + 1) * charsPerPage
        )
      );
    }
  }, [storyContent, fontSize, currentPage, getCharactersPerPage]);

  useEffect(() => {
    document.documentElement.style.setProperty(
      "--reader-font-size",
      `${fontSize}px`
    );
    // calculatePagination(); // Recalculate pagination when font size changes
  }, [fontSize]);

  const changePage = (direction) => {
    const newPage = currentPage + direction;
    if (newPage >= 0 && newPage < totalPages) {
      setCurrentPage(newPage);
      const charsPerPage = getCharactersPerPage();
      const newPageContent = storyContent.slice(
        newPage * charsPerPage,
        (newPage + 1) * charsPerPage
      );

      // Adjust the start of the next page to avoid partial lines
      setPageContent(newPageContent);
    }
  };

  const increaseFontSize = () => setFontSize((size) => Math.min(size + 2, 30));
  const decreaseFontSize = () => setFontSize((size) => Math.max(size - 2, 12));

  const handleSliderChange = (event, value) => {
    const newPage = Math.floor((value / 100) * (totalPages - 1));
    setCurrentPage(newPage);
    const charsPerPage = getCharactersPerPage();
    setPageContent(
      storyContent.slice(newPage * charsPerPage, (newPage + 1) * charsPerPage)
    );
  };



  // handle keydown for left and right arrow keys page turning
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "ArrowLeft" && currentPage > 0) {
        setCurrentPage(currentPage - 1); // Previous page
      } else if (event.key === "ArrowRight" && currentPage < totalPages - 1) {
        setCurrentPage(currentPage + 1); // Next page
      }
    };

    // Add keydown event listener
    document.addEventListener("keydown", handleKeyDown);

    // Clean up the event listener
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [currentPage, totalPages]); // Depend on currentPage and totalPages to update correctly



  if (loading) return <div>Loading...</div>;
  if (!story) return <div>Story not found</div>;

  return (
    <div>
      <div className="running-hed">
        <p className="reader-title">{story.title} | </p>
        <p className="reader-author"> | {story.author}</p>
      </div>


      <div className="reader-text" ref={contentRef} style={{ fontSize }} onMouseUp={handleTextSelection}>
        <pre>{pageContent}</pre>
      </div>

      {/* Comment Controls */}
      {showPopover && (
        <div
          ref={popoverRef}
          className="comment-popover"
          style={{ top: popoverPosition.y, left: popoverPosition.x }}
        >
          <textarea
            className="comment-textarea"
            placeholder="Add a comment"
            onChange={(e) => setCommentText(e.target.value)}
          />
          <button className="comment-button" onClick={handleSaveComment}>
            <CommentBankIcon />
          </button>
        </div>
      )}




      {/* Pagination Controls */}
      <div className="pagination-controls">
        <button
          className="prev-button"
          onClick={() => changePage(-1)}
          disabled={currentPage === 0}>
          <NavigateBeforeIcon />
        </button>
        <button
          className="next-button"
          onClick={() => changePage(1)}
          disabled={currentPage === totalPages - 1}
        >
          <NavigateNextIcon />
        </button>
      </div>

      {/* <div className="bottom-toggles-reader"> */}
      <div className="page-number">
        <span>{currentPage + 1}</span> / <span>{totalPages}</span>
      </div>

      <div className="font-controls">
          <button onClick={decreaseFontSize}>a</button>
          <button onClick={increaseFontSize}>A</button>
        </div>
      {/* </div> */}

        <div className="slider-container">
          <Slider
            value={((currentPage + 1) / totalPages) * 100}
            onChange={handleSliderChange}
            aria-labelledby="progress-slider"
            min={0}
            max={100}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${Math.floor(value)}%`}
            sx={{
              '& .MuiSlider-thumb': {
                  color: "black"
              },
              '& .MuiSlider-track': {
                  color: "black"
              },
              '& .MuiSlider-rail': {
                  color: "gray"
              },
              '& .MuiSlider-active': {
                  color: "green"
              }}}
          />
        </div>


    </div>
  );
};

export default ReaderView;