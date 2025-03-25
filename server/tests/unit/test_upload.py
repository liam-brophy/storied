import pytest
from main import app
from server.app import db
from server.app.models import User
import io
import os

def test_file_upload(app, test_client, db_session, sample_user):
    """
    Test file upload functionality
    
    Args:
        app: Flask application fixture
        test_client: Test client fixture
        db_session: Database session fixture
        sample_user: Sample user fixture
    """
    # Prepare test file
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'sample_book.pdf')
    
    # Ensure test file exists
    assert os.path.exists(test_file_path), f"Test file not found at {test_file_path}"
    
    # Open file in binary mode
    with open(test_file_path, 'rb') as file:
        # Create file storage object
        file_storage = io.BytesIO(file.read())
        file_storage.name = 'sample_book.pdf'
    
    # Prepare upload data
    upload_data = {
        'file': (file_storage, 'sample_book.pdf'),
        'title': 'Test Upload Book',
        'author': 'Test Author',
        'genre': 'Test Genre',
        'is_public': 'true',
        'user_id': sample_user.id  # Pass user ID directly
    }
    
    # Send upload request
    response = test_client.post(
        '/api/upload',
        data=upload_data,
        content_type='multipart/form-data'
    )
    
    # Assert successful upload
    assert response.status_code == 201, f"Upload failed: {response.get_json()}"
    
    # Parse response
    upload_result = response.get_json()
    
    # Verify response contents
    assert 'book_id' in upload_result, "Book ID not in response"
    assert 'file_metadata_id' in upload_result, "File metadata ID not in response"
    assert 's3_url' in upload_result, "S3 URL not in response"
    
    # Fetch the book from database to verify
    with app.app_context():
        book = Book.query.get(upload_result['book_id'])
        
        assert book is not None, "Book not saved in database"
        assert book.title == 'Test Upload Book', "Book title incorrect"
        assert book.author == 'Test Author', "Book author incorrect"
        assert book.uploaded_by_id == sample_user.id, "Incorrect uploader"
        assert book.is_public is True, "Book should be public"
        assert book.s3_url == upload_result['s3_url'], "S3 URL mismatch"

def test_upload_unauthorized(test_client):
    """
    Test upload without a valid user ID
    """
    # Prepare test file
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'sample_book.pdf')
    
    with open(test_file_path, 'rb') as file:
        file_storage = io.BytesIO(file.read())
        file_storage.name = 'sample_book.pdf'
    
    # Prepare upload data without a valid user ID
    upload_data = {
        'file': (file_storage, 'sample_book.pdf'),
        'title': 'Unauthorized Book',
        'author': 'Test Author',
        'user_id': None  # or an invalid user ID
    }
    
    # Send upload request 
    response = test_client.post(
        '/api/upload',
        data=upload_data,
        content_type='multipart/form-data'
    )
    
    # Assert unauthorized or bad request
    assert response.status_code in [400, 401], "Upload without valid user should be rejected"

def test_upload_invalid_file_type(app, test_client, db_session, sample_user):
    """
    Test uploading a file with an invalid file type
    """
    # Prepare test file (assuming a non-allowed file type)
    test_file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'invalid_file.zip')
    
    # Ensure test file exists (you'll need to create this file)
    assert os.path.exists(test_file_path), f"Test file not found at {test_file_path}"
    
    with open(test_file_path, 'rb') as file:
        file_storage = io.BytesIO(file.read())
        file_storage.name = 'invalid_file.zip'
    
    # Prepare upload data
    upload_data = {
        'file': (file_storage, 'invalid_file.zip'),
        'title': 'Invalid File',
        'author': 'Test Author',
        'user_id': sample_user.id  # Include user ID directly
    }
    
    # Send upload request
    response = test_client.post(
        '/api/upload',
        data=upload_data,
        content_type='multipart/form-data'
    )
    
    # Assert file type rejection
    assert response.status_code == 400, "Invalid file type should return 400"
    assert 'File type not allowed' in response.get_json().get('error', ''), "Error message should indicate file type rejection"