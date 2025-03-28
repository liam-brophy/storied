import React, { useState, useRef } from 'react'; // Added useRef
import { Upload, AlertCircle, CheckCircle } from 'lucide-react';
import { useBooks } from '../../hooks/useBooks';


const FileUploader = () => { // Renaming to BookUploadForm might be clearer
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [genre, setGenre] = useState('Fiction');
  // --- Removed is_public state, assuming default or handled differently? ---
  // If needed: const [isPublic, setIsPublic] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState(''); // For display
  const fileInputRef = useRef(null); // To clear the input
  const { addBook } = useBooks(); // 

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setSelectedFileName(selected ? selected.name : '');
    setMessage(''); // Clear message on new selection
    setIsSuccess(false);
  };

  // --- REMOVED createBook and uploadFile functions ---

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file || !title || !author) {
      setMessage('Title, Author, and File are required.');
      setIsSuccess(false);
      return;
    }

    setUploading(true);
    setMessage('Uploading...');
    setIsSuccess(false);

    // --- Construct ONE FormData object ---
    const formData = new FormData();
    formData.append('title', title);
    formData.append('author', author);
    formData.append('genre', genre); // Send genre
    formData.append('is_public', 'true'); // Send 'true' or 'false' as string for backend
    // If is_public state exists: formData.append('is_public', isPublic.toString());
    formData.append('file', file); // The actual file object

    try {
      // --- Send ONE request to /api/books ---
      // Use relative path if using proxy, otherwise prepend API_URL
      const response = await fetch(`/api/books`, {
        method: 'POST',
        body: formData,
        // NO 'Content-Type' header needed for FormData with fetch
      });

      if (!response.ok) { // Checks for 2xx status codes
        // Try to get error details from backend response
        const errorData = await response.json().catch(() => ({ error: 'Failed to parse error message' }));
        throw new Error(errorData?.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json(); // Get the created book data
      addBook(data);
      setMessage(`Book '${data.title}' uploaded successfully!`);
      setIsSuccess(true);

      // --- Clear the form ---
      setTitle('');
      setAuthor('');
      setGenre('Fiction');
      setFile(null);
      setSelectedFileName('');
      if (fileInputRef.current) {
          fileInputRef.current.value = ""; // Clear the file input visually
      }
      // setIsPublic(true); // Reset if using state for it

    } catch (error) {
      console.error('Error during upload:', error);
      setMessage(`Upload failed: ${error.message}`);
      setIsSuccess(false);
    } finally {
      setUploading(false);
    }
  };

  // --- JSX Structure (keeping your class names) ---
  return (
    <div className="story-upload-container"> {/* Your class */}
      <h2 className="upload-page-title">Upload a Book</h2> {/* Your class */}

      <form onSubmit={handleUpload} className="flex flex-col gap-4">
        {/* Title Input */}
        <div>
          <label htmlFor="book-title" className="block text-sm font-medium">Title:</label> {/* Added htmlFor */}
          <input
            id="book-title" // Added id
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full p-2 border rounded"
          />
        </div>

        {/* Author Input */}
        <div>
          <label htmlFor="book-author" className="block text-sm font-medium">Author:</label> {/* Added htmlFor */}
          <input
            id="book-author" // Added id
            type="text"
            value={author}
            onChange={(e) => setAuthor(e.target.value)}
            required
            className="w-full p-2 border rounded"
          />
        </div>

        {/* Genre Select */}
        {/* <div>
          <label htmlFor="book-genre" className="block text-sm font-medium">Genre:</label>
          <select
            id="book-genre" // Added id
            value={genre}
            onChange={(e) => setGenre(e.target.value)}
            className="w-full p-2 border rounded"
          >
            <option>Fiction</option>
            <option>Non-Fiction</option>
            <option>Thriller</option>
            <option>Romance</option>
          </select>
        </div> */}

        {/* File Input Area */}
        {/* You might need to adjust styling/logic for drag-drop appearance */}
        {/* This uses a label to trigger the hidden input */}
        <div className="form-group"> {/* Using a generic class name */}
           <label htmlFor="book-file-input" className={`story-upload-dropzone ${file ? 'story-upload-dropzone--active' : ''}`}> {/* Your class */}
              <input
                id="book-file-input" // Added id
                type="file"
                onChange={handleFileChange}
                required
                ref={fileInputRef} // Add ref here
                className="story-upload-input" // Your class - likely hidden
                accept=".pdf,.epub,.mobi,.txt,.docx" // Add accepted types
              />
              <Upload className="story-upload-icon" /> {/* Your class */}
              {/* Display selected file name or prompt */}
              {selectedFileName ? (
                  <>
                    <p className="story-upload-text">{selectedFileName}</p> {/* Your class */}
                    <p className="story-upload-subtext">Click or drag to change</p> {/* Your class */}
                  </>
              ) : (
                 <>
                    <p className="story-upload-text">Drag & drop your file here</p> {/* Your class */}
                    <p className="story-upload-subtext">or click to browse</p> {/* Your class */}
                 </>
              )}
            </label>
        </div>


        {/* Submit Button */}
        <button
          type="submit"
          disabled={uploading}
          className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-700" // Your Tailwind classes
        >
          {uploading ? 'Uploading...' : 'Upload Book'} {/* Changed text */}
        </button>
      </form>

      {/* Status Message */}
      {message && (
        <div className={`story-upload-alert ${isSuccess ? 'text-green-500' : 'text-red-500'}`}> {/* Your class */}
          {isSuccess ? <CheckCircle className="story-upload-alert-icon" /> : <AlertCircle className="story-upload-alert-icon" />} {/* Your class */}
          <span className="ml-2">{message}</span>
        </div>
      )}
    </div>
  );
};

export default FileUploader; // Or BookUploadForm