import boto3
from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.models import FileMetadata, Book
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
import mimetypes

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'epub', 'mobi', 'txt', 'doc', 'docx', 'html'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, unique_filename):
    """
    Upload file to S3 bucket
    
    Args:
        file: File object to upload
        unique_filename: Unique filename for S3 storage
    
    Returns:
        str: S3 URL of the uploaded file
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )
        
        # Determine content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            current_app.config['S3_BUCKET_NAME'],
            unique_filename,
            ExtraArgs={
                'ContentType': content_type
            }
        )
        
        # Generate S3 URL
        s3_url = f"https://{current_app.config['S3_BUCKET_NAME']}.s3.amazonaws.com/{unique_filename}"
        
        return s3_url
    
    except Exception as e:
        current_app.logger.error(f"S3 Upload Error: {str(e)}")
        raise

@upload_bp.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename):
            # Secure the filename to prevent injection attacks
            filename = secure_filename(file.filename)
            
            # Generate a unique filename using UUID
            unique_filename = f"books/{uuid.uuid4()}_{filename}"
            
            # Upload to S3
            s3_url = upload_to_s3(file, unique_filename)
            
            # Get the current user's ID
            current_user_id = get_jwt_identity()
            
            # Get file details
            file_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            # Determine file size 
            # Note: For S3 uploads, you might need to reset file pointer or use different method
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            # Create file metadata
            new_file_metadata = FileMetadata(
                file_name=filename,
                file_type=file_type,
                size=file_size,
                uploaded_at=datetime.utcnow(),
                uploaded_by_id=current_user_id
            )
            
            # Save to database
            new_file_metadata.save()
            
            # Create a book record associated with this file
            title = request.form.get('title', filename)  # Use filename as title if not provided
            author = request.form.get('author', 'Unknown')
            genre = request.form.get('genre', None)
            is_public = request.form.get('is_public', 'false').lower() == 'true'
            
            new_book = Book(
                title=title,
                author=author,
                genre=genre,
                uploaded_by_id=current_user_id,
                file_id=new_file_metadata.id,
                is_public=is_public,
                s3_url=s3_url,  # Store S3 URL in the book model
                file_size=file_size,
                file_type=file_type
            )
            
            new_book.save()
            
            return jsonify({
                "message": "File uploaded successfully",
                "book_id": new_book.id,
                "file_metadata_id": new_file_metadata.id,
                "filename": filename,
                "s3_url": s3_url
            }), 201
        
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    except Exception as e:
        current_app.logger.error(f"Upload Error: {str(e)}")
        return jsonify({"error": f"An error occurred during file upload: {str(e)}"}), 500

@upload_bp.route('/api/books/<int:book_id>/download', methods=['GET'])
@jwt_required()
def download_file(book_id):
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        
        # Find the book
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        # Check if user has access to this book
        if not book.is_public:
            # Check if user is the owner
            if book.uploaded_by_id != current_user_id:
                # Check if users are friends
                if not Friendship.are_friends(current_user_id, book.uploaded_by_id):
                    return jsonify({"error": "You don't have permission to download this file"}), 403
        
        # Verify S3 URL exists
        if not book.s3_url:
            return jsonify({"error": "No S3 URL associated with this book"}), 404
        
        # Generate pre-signed URL for download
        s3_client = boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION']
        )
        
        # Extract the S3 object key from the full S3 URL
        s3_bucket = current_app.config['S3_BUCKET_NAME']
        s3_key = book.s3_url.split(f"{s3_bucket}.s3.amazonaws.com/", 1)[1]
        
        # Generate pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': s3_bucket,
                'Key': s3_key
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
        
        return jsonify({
            "download_url": presigned_url,
            "filename": book.title  # or use original filename if available
        }), 200
    
    except Exception as e:
        current_app.logger.error(f"Download Error: {str(e)}")
        return jsonify({"error": f"An error occurred during file download: {str(e)}"}), 500