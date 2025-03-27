import React, { useState, useEffect, useRef, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { Document, Page, pdfjs } from 'react-pdf';
import { Slider } from "@mui/material";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import CommentBankIcon from '@mui/icons-material/CommentBank';
import './CommentPopover.css';
import { BooksContext } from '../../contexts/BookContext'; // Import BookContext

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const PdfReaderView = () => {
    const { bookId } = useParams(); // Renamed from storyId to bookId
    const [book, setBook] = useState(null); // Renamed from story to book
    const [numPages, setNumPages] = useState(null);
    const [pageNumber, setPageNumber] = useState(1);
    const [pdfFile, setPdfFile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [fontSize, setFontSize] = useState(16);
    const [showPopover, setShowPopover] = useState(false);
    const [popoverPosition, setPopoverPosition] = useState({ x: 0, y: 0 });
    const [selectedText, setSelectedText] = useState("");
    const [commentText, setCommentText] = useState("");
    const popoverRef = useRef(null);
    const { books, isLoading: isBooksLoading, error: booksError } = useContext(BooksContext); // Access books from context

    useEffect(() => {
        // Find the book in the context
        const foundBook = books.find((book) => book.id === parseInt(bookId)); // Renamed storyId to bookId

        if (foundBook) {
            setBook(foundBook); // Renamed setStory to setBook
            // Assuming your book data now contains a 'contentPath' or similar
            // property that points to the S3 URL of the PDF
            const fetchPdf = async () => {
                try {
                    setLoading(true);
                    const pdfResponse = await fetch(foundBook.s3_url);  // Assuming data.contentPath holds the S3 URL
                    if (!pdfResponse.ok) throw new Error("PDF not found");

                    const blob = await pdfResponse.blob();
                    setPdfFile(URL.createObjectURL(blob)); // Use a blob URL
                } catch (error) {
                    console.error("Error fetching PDF:", error);
                } finally {
                    setLoading(false);
                }
            };
            fetchPdf();

        } else if (!isBooksLoading && !booksError) {
            // Only set an error if the books have finished loading AND there's no general book loading error
            console.log(`Book with ID ${bookId} not found`); // Renamed storyId to bookId
        }
    }, [bookId, books, isBooksLoading, booksError]); // Renamed storyId to bookId

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (popoverRef.current && !popoverRef.current.contains(event.target)) {
                setShowPopover(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const onDocumentLoadSuccess = ({ numPages }) => {
        setNumPages(numPages);
    };

    const changePage = (offset) => {
        setPageNumber(prevPageNumber => Math.max(1, Math.min(prevPageNumber + offset, numPages)));
    };

    const previousPage = () => changePage(-1);
    const nextPage = () => changePage(1);

    const increaseFontSize = () => setFontSize((size) => Math.min(size + 2, 30));
    const decreaseFontSize = () => setFontSize((size) => Math.max(size - 2, 12));

    const handleSliderChange = (event, value) => {
        const newPage = Math.floor((value / 100) * (numPages - 1)) + 1;
        setPageNumber(newPage);
    };

    const handleKeyDown = (event) => {
        if (event.key === "ArrowLeft" && pageNumber > 1) {
            setPageNumber(pageNumber - 1);
        } else if (event.key === "ArrowRight" && pageNumber < numPages) {
            setPageNumber(pageNumber + 1);
        }
    };

    useEffect(() => {
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [pageNumber, numPages]);

    // Text selection and Commenting
    const getHighlightedText = () => {
        //This function will need to be adjusted to work with react-pdf
        const selection = window.getSelection();
        return selection ? selection.toString() : "";
    };

    const handleTextSelection = () => {
        const text = getHighlightedText();
        if (text) {
            //This part will need to be adjusted to work with react-pdf
            const rect = window.getSelection().getRangeAt(0).getBoundingClientRect();
            setPopoverPosition({ x: rect.x, y: rect.y });
            setSelectedText(text);
            setShowPopover(true);
        }
    };

    const handleSaveComment = async () => {
        const newComment = {
            content: commentText, //text was renamed content
            page_number: pageNumber, //page was renamed page_number
            book_id: bookId, //book was renamed book_id
        };
        try {
            await fetch(`http://localhost:5555/api/notes`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newComment),
                credentials: 'include',
            });
            setShowPopover(false);
        } catch (error) {
            console.error("Error saving comment:", error);
        }
    };

    if (loading || isBooksLoading) return <div>Loading...</div>;
    if (!book || !pdfFile) return <div>Book not found</div>; // Renamed story to book
    if (booksError) return <div>Error loading books: {booksError}</div>

    return (
        <div>
            <div className="running-hed">
                <p className="reader-title">{book.title} | </p> {/* Renamed story to book */}
                <p className="reader-author"> | {book.author}</p>
            </div>

            <div className="pdf-container">
                <Document
                    file={pdfFile}
                    onLoadSuccess={onDocumentLoadSuccess}
                >
                    <Page pageNumber={pageNumber} renderTextLayer={true} renderAnnotationLayer={false} onMouseUp={handleTextSelection} width={fontSize * 25} />
                </Document>
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
                    onClick={previousPage}
                    disabled={pageNumber <= 1}>
                    <NavigateBeforeIcon />
                </button>
                <button
                    className="next-button"
                    onClick={nextPage}
                    disabled={pageNumber >= numPages}
                >
                    <NavigateNextIcon />
                </button>
            </div>

            <div className="page-number">
                <span>{pageNumber}</span> / <span>{numPages}</span>
            </div>

            <div className="font-controls">
                <button onClick={decreaseFontSize}>a</button>
                <button onClick={increaseFontSize}>A</button>
            </div>

            <div className="slider-container">
                <Slider
                    value={((pageNumber) / numPages) * 100}
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
                        }
                    }}
                />
            </div>
        </div>
    );
};

export default PdfReaderView;




// <Document
//           file={pdfUrl}
//           onLoadSuccess={({ numPages }) => setNumPages(numPages)}
//         >
//           <Page pageNumber={currentPage} scale={scale} />
//         </Document>