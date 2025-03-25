from flask import Blueprint, request, jsonify, g, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import boto3
from botocore.exceptions import ClientError
import uuid

from app.models.book import Book
from app.models.file_metadata import FileMetadata
from app.models.user import User
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

books_bp = Blueprint('books', __name__, url_prefix='/api/books')

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
        user_id = g.user.id
        
        # Get books that are either public or uploaded by the user
        books = Book.query.filter(
            (Book.is_public == True) | (Book.uploaded_by_id == user_id)
        ).all()
        
        # Serialize book data
        result = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_public': book.is_public,
            'uploaded_by': book.uploader.username,
            'created_at': book.created_at.isoformat(),
            'has_file': bool(book.file_metadata)
        } for book in books]
        
        return jsonify(result), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching books: {str(e)}")
        return jsonify({'error': 'Failed to fetch books'}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
# @auth_required
def get_book(book_id):
    """Get a specific book with access control"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Validate user access
        if not validate_book_access(book, g.user.id):
            return jsonify({'error': 'You do not have access to this book'}), 403
        
        # Prepare book data
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_public': book.is_public,
            'uploaded_by': book.uploader.username,
            'created_at': book.created_at.isoformat(),
            'file_metadata': None
        }
        
        # Add file metadata if available
        if book.file_metadata:
            book_data['file_metadata'] = {
                'file_name': book.file_metadata.file_name,
                'file_type': book.file_metadata.file_type,
                'size': book.file_metadata.size,
                'uploaded_at': book.file_metadata.uploaded_at.isoformat()
            }
        
        return jsonify(book_data), 200
    
    except Exception as e:
        current_app.logger.error(f"Error fetching book: {str(e)}")
        return jsonify({'error': 'Failed to fetch book'}), 500

@books_bp.route('', methods=['POST'])
# @auth_required
def create_book():
    """Create a new book entry"""
    try:
        data = request.json
        
        # Validate required fields
        if not all(field in data for field in ['title', 'author']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new book
        new_book = Book(
            title=data['title'],
            author=data['author'],
            genre=data.get('genre', 'Unknown'),
            is_public=data.get('is_public', True),
            uploaded_by_id=g.user.id
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            'id': new_book.id,
            'title': new_book.title,
            'author': new_book.author,
            'genre': new_book.genre,
            'is_public': new_book.is_public,
            'uploaded_by': g.user.username,
            'created_at': new_book.created_at.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating book: {str(e)}")
        return jsonify({'error': 'Failed to create book'}), 500

@books_bp.route('/<int:book_id>/upload', methods=['POST'])
# @auth_required
def upload_book_file(book_id):
    """Upload a file for a specific book"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Verify user ownership
        if book.uploaded_by_id != g.user.id:
            return jsonify({'error': 'Unauthorized to upload for this book'}), 403
        
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Validate file name and type
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Validate file extension
        valid_extensions = {'txt', 'pdf', 'epub', 'mobi', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in valid_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(valid_extensions)}'}), 400
        
        # Generate unique S3 key
        s3_key = generate_s3_file_key(book_id, file.filename)
        
        # Upload to S3
        s3_client.upload_fileobj(
            file, 
            S3_BUCKET, 
            s3_key,
            ExtraArgs={
                'ContentType': file.content_type,
                'ACL': 'private'
            }
        )
        
        # Create or update file metadata
        file_metadata = book.file_metadata or FileMetadata(book_id=book.id)
        file_metadata.file_name = secure_filename(file.filename)
        file_metadata.file_type = file_ext
        file_metadata.size = file.content_length or 0
        
        db.session.add(file_metadata)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_name': file_metadata.file_name,
            'file_type': file_metadata.file_type,
            'size': file_metadata.size
        }), 201
    
    except ClientError as s3_error:
        db.session.rollback()
        current_app.logger.error(f"S3 Upload Error: {str(s3_error)}")
        return jsonify({'error': 'Failed to upload file to storage'}), 500
    
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
        if not book.file_metadata:
            return jsonify({'error': 'No file available for download'}), 404
        
        # Generate presigned URL
        s3_key = f"books/{book_id}/{book.file_metadata.file_name}"
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': s3_key,
                'ResponseContentDisposition': f'attachment; filename="{book.file_metadata.file_name}"'
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return jsonify({
            'download_url': download_url,
            'file_name': book.file_metadata.file_name,
            'expires_in': '1 hour'
        }), 200
    
    except ClientError as s3_error:
        current_app.logger.error(f"Download URL generation error: {str(s3_error)}")
        return jsonify({'error': 'Failed to generate download link'}), 500