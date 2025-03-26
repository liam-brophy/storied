from flask import Blueprint, request, jsonify, g, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import boto3
from botocore.exceptions import ClientError
import uuid
from ipdb import set_trace
import logging


from app.models import Book, FileMetadata, User
# from app.routes.auth import auth_required
from app import db

# S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
S3_BUCKET = os.getenv('S3_BUCKET_NAME')


print(f"Value assigned to S3_BUCKET variable: >>>{S3_BUCKET}<<<") # Check value assigned to variable
print("--- Finished routes/books.py top-level ---")

books_bp = Blueprint('books', __name__, url_prefix='/api/books')


#STANDARADIZED RESPONSE
# def api_response(success, message, data=None, status=200):
#     """Standardized API response format"""
#     return jsonify({
#         'success': success,
#         'message': message,
#         'data': data
#     }), status

def validate_book_access(book, user_id):
    """
    Check if user has access to the book
    
    :param book: Book object
    :param user_id: ID of the current user
    :return: Boolean indicating access
    """
    return book.is_public or book.uploaded_by_id == user_id

def generate_s3_file_key(book_id, filename):
    """
    Generate a unique S3 file key
    
    :param book_id: ID of the book
    :param filename: Original filename
    :return: Unique S3 file key
    """
    safe_filename = secure_filename(filename)
    unique_id = uuid.uuid4().hex
    file_ext = os.path.splitext(safe_filename)[1]
    return f"books/{book_id}/{unique_id}{file_ext}"

@books_bp.route('', methods=['GET'])
# @auth_required
def get_books():
    """Get all books that the user has access to"""
    try:
        # user_id = g.user.id

        # Get books that are either public or uploaded by the user
        books = Book.query.filter(
            (Book.is_public == True) #| (Book.uploaded_by_id == user_id)
        ).all()
        
        # Serialize book data using SerializerMixin
        result = [book.to_dict() for book in books]
        
        return jsonify(result), 200
    
    except Exception as e:
        # current_app.logger.error(f"Error fetching books: {str(e)}")
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
# @auth_required
def get_book(book_id):
    """Get a specific book with access control"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Validate user access
        if not validate_book_access(book, g.user.id):
            return jsonify({'error': 'You do not have access to this book'}), 403
        
        # Serialize book data using SerializerMixin
        book_data = book.to_dict()
        
        return jsonify(book_data), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching book: {str(e)}")
        return jsonify({'error': 'Failed to fetch book'}), 500

@books_bp.route('', methods=['POST'])
# @auth_required
def create_book():
    """Create a new book entry with file upload"""
    try:
        # Use request.form directly
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre', 'Unknown')
        is_public = request.form.get('is_public', 'true').lower() == 'true' # Handle potential string 'false'

        # Validate required fields using the fetched variables
        # Use request.form to check existence robustly
        if not title or not author:
             # Or: if not all(field in request.form for field in ['title', 'author']):
            return jsonify({'error': 'Missing required fields: title and author'}), 400

        # Handle file upload
        file = request.files.get('file')
        if not file or not file.filename: # Also check if filename is not empty
            return jsonify({'error': 'File with a filename is required'}), 400

        # Secure the filename
        filename = secure_filename(file.filename)

        # --- S3 Upload Section ---
        file_key = f"books/{filename}" # Consider adding user ID or UUID for uniqueness
        file_url = None
        file_size = None
        file_type = None

        try:
            # Option 1: Get size before upload (can be memory intensive)
            # file.seek(0, os.SEEK_END) # Seek to end to get size
            # file_size = file.tell()    # Get size
            # file.seek(0)               # Reset file pointer for S3 upload

            # Option 2: Read into memory (original way, memory intensive)
            # Be cautious with large files
            file_content = file.read()
            file_size = len(file_content)
            file.seek(0) # Reset file pointer if read() consumed it (depends on underlying stream type, but good practice)

            # Upload to S3 bucket
            # If using file_content: use upload_fileobj(io.BytesIO(file_content), ...)
            # If using original file object after seek(0): use upload_fileobj(file, ...)
            s3_client.upload_fileobj(
                file, # Or io.BytesIO(file_content) if using Option 2 rigorously
                S3_BUCKET,
                file_key,
                ExtraArgs={ # Optional: Explicitly set ContentType for S3 object
                    'ContentType': file.content_type
                }
            )

            # File URL after upload
            # Ensure your bucket policy allows public reads if this URL is for direct access
            file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_key}"
            file_type = file.content_type.replace('application/', '')

        except Exception as e:
            # Use current_app.logger for Flask context
            current_app.logger.error(f"Error uploading file to S3: {str(e)}", exc_info=True) # Log traceback
            return jsonify({'error': 'Failed to upload file to S3'}), 500
        # --- End S3 Upload Section ---

        # Get user ID safely
        uploader_id = None
        if hasattr(g, 'user') and g.user:
             uploader_id = g.user.id
        # else:
             # Decide what to do if no user is found (e.g., raise error, allow None)
             # If auth is required, the decorator should handle this before the function runs.
             # If auth is optional, allowing None might be okay if DB column is nullable.
             # pass # uploader_id remains None


        # Create new book using variables defined earlier
        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            is_public=is_public,
            uploaded_by_id=uploader_id, # Use the safe variable
            s3_url=file_url,
            file_size=file_size,
            file_type=file_type
            # Consider adding filename=filename to the model too
        )

        db.session.add(new_book)
        db.session.commit()

        new_book_data = FileMetadata(
            file_name=filename,
            file_type=file_type,
            size=file_size,
            book_id=new_book.id
        )

        db.session.add(new_book_data)
        db.session.commit()

        # Serialize and return the new book data
        # Ensure Book model has a functioning to_dict method
        return jsonify(new_book.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        # Use current_app.logger and include traceback
        current_app.logger.error(f"Error creating book: {str(e)}", exc_info=True)
        # Avoid exposing internal error details in production responses
        return jsonify({'error': str(e)}), 500


@books_bp.route('/<int:book_id>/upload', methods=['POST'])
# @auth_required
def upload_book_file(book_id):
    """Upload a file for a specific book and store S3 URL"""
    try:
        book = Book.query.get_or_404(book_id)

        # Check ownership
        if book.uploaded_by_id != g.user.id:
            return jsonify({'error': 'Unauthorized to upload for this book'}), 403

        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Validate file extension
        valid_extensions = {'txt', 'pdf', 'epub', 'mobi', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower()

        if file_ext not in valid_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(valid_extensions)}'}), 400

        # Generate unique S3 key
        s3_key = generate_s3_file_key(book_id, file.filename)

        # Upload to S3
        try:
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                s3_key,
                ExtraArgs={
                    'ContentType': file.content_type,
                    'ACL': 'private'
                }
            )
        except ClientError as s3_error:
            current_app.logger.error(f"S3 Upload Error: {str(s3_error)}")
            return jsonify({'error': 'Failed to upload file to S3'}), 500

        # Calculate file size with fallback
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        # Create or update FileMetadata
        file_metadata = book.file_metadata or FileMetadata(book_id=book.id)
        file_metadata.file_name = secure_filename(file.filename)
        file_metadata.file_type = file_ext
        file_metadata.size = file_size

        # Store S3 URL in the Book model
        book.s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

        # Save changes
        db.session.add(file_metadata)
        db.session.commit()

        return jsonify({
            'message': 'File uploaded successfully',
            's3_url': book.s3_url,
            'file_name': file_metadata.file_name,
            'file_type': file_metadata.file_type,
            'size': file_metadata.size
        }), 201

    except ClientError as s3_error:
        db.session.rollback()
        current_app.logger.error(f"S3 Upload Error: {str(s3_error)}")
        return jsonify({'error': 'Failed to upload file to S3'}), 500

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'Failed to process file upload'}), 500


@books_bp.route('/<int:book_id>/download', methods=['GET'])
# @auth_required
def generate_download_url(book_id):
    """Generate a temporary download URL for a book file"""
    try:
        book = Book.query.get_or_404(book_id)

        # Validate access
        if not validate_book_access(book, g.user.id):
            return jsonify({'error': 'Unauthorized to download this book'}), 403

        # Check if file exists
        if not book.file_metadata or not book.s3_url:
            return jsonify({'error': 'No file available for download'}), 404

        # Extract S3 key from URL
        s3_key = book.s3_url.split('.com/')[-1]

        try:
            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{book.file_metadata.file_name}"'
                },
                ExpiresIn=3600  # 1 hour
            )

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return jsonify({'error': 'File not found on S3'}), 404
            raise e

        return jsonify({
            'download_url': download_url,
            'file_name': book.file_metadata.file_name,
            'expires_in': '1 hour'
        }), 200

    except ClientError as s3_error:
        current_app.logger.error(f"Download URL error: {str(s3_error)}")
        return jsonify({'error': 'Failed to generate download link'}), 500

    except Exception as e:
        current_app.logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Failed to generate download link'}), 500