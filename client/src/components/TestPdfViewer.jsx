import React from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

const TestPdfViewer = () => {
    console.log("TestPdfViewer is rendering!");  // Add this line
    const pdfUrl = 'https://storied-book-storage.s3.us-east-2.amazonaws.com/books/TestBook.pdf';
  
    try {
      return (
        <div>
          <h1>Test PDF Viewer</h1>
          <Document file={pdfUrl}>
            <Page pageNumber={1} />
          </Document>
        </div>
      );
    } catch (error) {
      console.error("Error rendering TestPdfViewer:", error);
      return <div>Error loading PDF</div>;
    }
  };


  export default TestPdfViewer;