from app.models import Book
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.utils import secure_filename
import os
import boto3
from botocore.exceptions import ClientError
import uuid
from .auth import auth_required

book_bp = Blueprint('book', __name__, url_prefix='/api/books')

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION')
)
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

@book_bp.route('', methods=['GET'])
@auth_required
def get_books():
    """Get all books that the user has access to (public books and own books)"""
    try:
        user_id = g.user.id
        
        books = Book.query.filter(
            (Book.is_public == True) | (Book.uploaded_by_id == user_id)
        ).all()
        
        result = []
        for book in books:
            result.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'genre': book.genre,
                'is_public': book.is_public,
                'uploaded_by': book.uploader.username,
                'created_at': book.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching books: {str(e)}")
        return jsonify({'error': 'Failed to fetch books'}), 500

@book_bp.route('/<int:book_id>', methods=['GET'])
@auth_required
def get_book(book_id):
    """Get a book by ID if the user has access to it"""
    try:
        user_id = g.user.id
        book = Book.query.get_or_404(book_id)
        
        # Check if user has access to the book
        if not book.is_public and book.uploaded_by_id != user_id:
            return jsonify({'error': 'You do not have access to this book'}), 403
        
        # Get file metadata if available
        file_data = None
        if book.file_metadata:
            file_data = {
                'file_name': book.file_metadata.file_name,
                'file_type': book.file_metadata.file_type,
                'size': book.file_metadata.size,
                'uploaded_at': book.file_metadata.uploaded_at.isoformat()
            }
        
        result = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_public': book.is_public,
            'content': book.content,  # Added content field
            'uploaded_by': book.uploader.username,
            'created_at': book.created_at.isoformat(),
            'file': file_data
        }
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching book: {str(e)}")
        return jsonify({'error': 'Failed to fetch book'}), 500

@book_bp.route('', methods=['POST'])
@auth_required
def create_book():
    """Create a new book"""
    try:
        user_id = g.user.id
        data = request.json
        
        required_fields = ['title', 'author']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new book object
        new_book = Book(
            title=data['title'],
            author=data['author'],
            genre=data.get('genre', 'Unknown'),
            is_public=data.get('is_public', True),
            content=data.get('content', ''),  # Added content field
            uploaded_by_id=user_id
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify({
            'id': new_book.id,
            'title': new_book.title,
            'author': new_book.author,
            'genre': new_book.genre,
            'is_public': new_book.is_public,
            'content': new_book.content,  # Include content in response
            'uploaded_by': g.user.username,
            'created_at': new_book.created_at.isoformat()
        }), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating book: {str(e)}")
        return jsonify({'error': 'Failed to create book'}), 500

@book_bp.route('/<int:book_id>', methods=['PUT'])
@auth_required
def update_book(book_id):
    """Update an existing book if the user is the owner"""
    try:
        user_id = g.user.id
        book = Book.query.get_or_404(book_id)
        
        # Check if user is the owner
        if book.uploaded_by_id != user_id:
            return jsonify({'error': 'You do not have permission to update this book'}), 403
        
        data = request.json
        
        # Update fields
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        if 'genre' in data:
            book.genre = data['genre']
        if 'is_public' in data:
            book.is_public = data['is_public']
        if 'content' in data:
            book.content = data['content']  # Update content field
        
        db.session.commit()
        
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'is_public': book.is_public,
            'content': book.content,  # Include content in response
            'uploaded_by': book.uploader.username,
            'created_at': book.created_at.isoformat()
        }), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating book: {str(e)}")
        return jsonify({'error': 'Failed to update book'}), 500

@book_bp.route('/<int:book_id>', methods=['DELETE'])
@auth_required
def delete_book(book_id):
    """Delete a book if the user is the owner"""
    user_id = g.user.id
    book = Book.query.get_or_404(book_id)
    
    # Check if user is the owner
    if book.uploaded_by_id != user_id:
        return jsonify({'error': 'You do not have permission to delete this book'}), 403
    
    try:
        # If there's a file associated with this book, delete it from S3 too
        if book.file_metadata:
            try:
                file_key = f"books/{book.id}/{book.file_metadata.file_name}"
                s3_client.delete_object(Bucket=S3_BUCKET, Key=file_key)
            except ClientError as e:
                current_app.logger.error(f"Error deleting file from S3: {str(e)}")
                # Continue with deletion even if S3 delete fails
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({'message': 'Book deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting book: {str(e)}")
        return jsonify({'error': 'Failed to delete book'}), 500

@book_bp.route('/<int:book_id>/upload', methods=['POST'])
@auth_required
def upload_file(book_id):
    """Upload a file for a book"""
    user_id = g.user.id
    book = Book.query.get_or_404(book_id)
    
    # Check if user is the owner
    if book.uploaded_by_id != user_id:
        return jsonify({'error': 'You do not have permission to upload files for this book'}), 403
    
    # Check if file is included in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if filename is valid
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    valid_extensions = {'txt': 'txt', 'html': 'html', 'docx': 'docx', 'pdf': 'pdf'}
    
    if file_extension not in valid_extensions:
        return jsonify({'error': 'Invalid file type. Allowed types: txt, html, docx, pdf'}), 400
    
    # Generate secure filename
    secure_name = secure_filename(file.filename)
    file_key = f"books/{book.id}/{secure_name}"
    
    try:
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file_key,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )
        
        # Create or update file metadata
        if book.file_metadata:
            # Update existing metadata
            book.file_metadata.file_name = secure_name
            book.file_metadata.file_type = valid_extensions[file_extension]
            book.file_metadata.size = file.content_length or 0
        else:
            # Create new metadata
            file_metadata = FileMetadata(
                file_name=secure_name,
                file_type=valid_extensions[file_extension],
                size=file.content_length or 0,
                book_id=book.id
            )
            db.session.add(file_metadata)
        
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_name': secure_name,
            'file_type': valid_extensions[file_extension],
            'size': file.content_length or 0
        }), 201
        
    except ClientError as e:
        db.session.rollback()
        current_app.logger.error(f"S3 upload error: {str(e)}")
        return jsonify({'error': 'Failed to upload file to storage'}), 500
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': 'Failed to process file upload'}), 500

@book_bp.route('/<int:book_id>/download', methods=['GET'])
@auth_required
def download_file(book_id):
    """Generate a download URL for a book's file"""
    user_id = g.user.id
    book = Book.query.get_or_404(book_id)
    
    # Check if user has access to the book
    if not book.is_public and book.uploaded_by_id != user_id:
        return jsonify({'error': 'You do not have access to this book'}), 403
    
    # Check if book has a file
    if not book.file_metadata:
        return jsonify({'error': 'No file available for this book'}), 404
    
    try:
        # Generate presigned URL for download
        file_key = f"books/{book.id}/{book.file_metadata.file_name}"
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': file_key
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )
        
        return jsonify({
            'download_url': url,
            'file_name': book.file_metadata.file_name,
            'file_type': book.file_metadata.file_type,
            'expires_in': '1 hour'
        }), 200
        
    except ClientError as e:
        current_app.logger.error(f"Error generating download URL: {str(e)}")
        return jsonify({'error': 'Failed to generate download link'}), 500