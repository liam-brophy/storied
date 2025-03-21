from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.models.file_metadata import FileMetadata
from app.models.book import Book
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'epub', 'mobi', 'txt', 'doc', 'docx', 'html'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Create directory if it doesn't exist
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Get the current user's ID
            current_user_id = get_jwt_identity()
            
            # Create file metadata
            file_type = file.content_type if hasattr(file, 'content_type') else "application/octet-stream"
            file_size = os.path.getsize(file_path)
            
            # Create the file metadata record
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
            
            new_book = Book(
                title=title,
                author=author,
                genre=genre,
                uploaded_by_id=current_user_id,
                file_id=new_file_metadata.id,
                is_public=request.form.get('is_public', False)
            )
            
            new_book.save()
            
            return jsonify({
                "message": "File uploaded successfully",
                "book_id": new_book.id,
                "file_metadata_id": new_file_metadata.id,
                "filename": filename
            }), 201
        
        return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    except Exception as e:
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
        if not book.is_public and book.uploaded_by_id != current_user_id:
            # TODO: Add friendship check here when friendship model is implemented
            return jsonify({"error": "You don't have permission to download this file"}), 403
        
        # Get file metadata
        file_metadata = FileMetadata.query.get(book.file_id)
        
        if not file_metadata:
            return jsonify({"error": "File metadata not found"}), 404
        
        # Construct the file path
        filename = f"{file_metadata.id}_{file_metadata.file_name}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on server"}), 404
        
        # Return the file
        return send_file(file_path, as_attachment=True, download_name=file_metadata.file_name)
    except Exception as e:
        return jsonify({"error": f"An error occurred during file download: {str(e)}"}), 500