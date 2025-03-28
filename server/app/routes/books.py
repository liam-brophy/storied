from flask import Blueprint, request, jsonify, g, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import boto3
from botocore.exceptions import ClientError
import uuid
from app.models import Book, FileMetadata, User
from app import db

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION', 'us-east-1')
)
S3_BUCKET = os.getenv('S3_BUCKET_NAME')

books_bp = Blueprint('books', __name__, url_prefix='/api/books')


def validate_book_access(book, user_id):
    return book.is_public or book.uploaded_by_id == user_id

def generate_s3_file_key(book_id, filename):
    safe_filename = secure_filename(filename)
    unique_id = uuid.uuid4().hex
    file_ext = os.path.splitext(safe_filename)[1]
    return f"books/{book_id}/{unique_id}{file_ext}"

@books_bp.route('', methods=['GET'])
def get_books():
    try:
        books = Book.query.filter(
            (Book.is_public == True)
        ).all()
        result = [book.to_dict() for book in books]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if not validate_book_access(book, g.user.id):
            return jsonify({'error': 'You do not have access to this book'}), 403
        book_data = book.to_dict()
        return jsonify(book_data), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching book: {str(e)}")
        return jsonify({'error': 'Failed to fetch book'}), 500

@books_bp.route('', methods=['POST'])
def create_book():
    try:
        title = request.form.get('title')
        author = request.form.get('author')
        genre = request.form.get('genre', 'Unknown')
        is_public = request.form.get('is_public', 'true').lower() == 'true'

        if not title or not author:
            return jsonify({'error': 'Missing required fields: title and author'}), 400

        file = request.files.get('file')
        if not file or not file.filename:
            return jsonify({'error': 'File with a filename is required'}), 400

        filename = secure_filename(file.filename)
        file_key = f"books/{filename}"
        file_url = None
        file_size = None
        file_type = None

        try:
            file_content = file.read()
            file_size = len(file_content)
            file.seek(0)
            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                file_key,
                ExtraArgs={'ContentType': file.content_type}
            )
            file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_key}"
            file_type = file.content_type.replace('application/', '')
        except Exception as e:
            current_app.logger.error(f"Error uploading file to S3: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to upload file to S3'}), 500

        uploader_id = g.user.id if hasattr(g, 'user') and g.user else None

        new_book = Book(
            title=title,
            author=author,
            genre=genre,
            is_public=is_public,
            uploaded_by_id=uploader_id,
            s3_url=file_url,
            file_size=file_size,
            file_type=file_type
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

        return jsonify(new_book.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating book: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@books_bp.route('/<int:book_id>', methods=['DELETE'])
@auth_required
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if book.uploaded_by_id != g.user.id:
            current_app.logger.warning(f"User {g.user.id} attempted to delete book {book_id} owned by user {book.uploaded_by_id}")
            return jsonify({'error': 'Forbidden: You do not own this book'}), 403

        s3_url_to_delete = book.s3_url
        s3_key_to_delete = None
        bucket_name = current_app.config.get('S3_BUCKET')

        if s3_url_to_delete:
            try:
                if f"/{bucket_name}/" in s3_url_to_delete:
                    s3_key_to_delete = s3_url_to_delete.split(f"/{bucket_name}/", 1)[1]
                elif f"//{bucket_name}." in s3_url_to_delete:
                    s3_key_to_delete = s3_url_to_delete.split(f"{bucket_name}.s3.{current_app.config.get('S3_REGION')}.amazonaws.com/", 1)[1]
                if not s3_key_to_delete:
                    current_app.logger.error(f"Could not extract S3 key from URL: {s3_url_to_delete}")
            except Exception as parse_error:
                current_app.logger.error(f"Error parsing S3 URL {s3_url_to_delete}: {parse_error}")
                s3_key_to_delete = None

        db.session.delete(book)
        db.session.commit()

        if s3_key_to_delete and bucket_name:
            try:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=current_app.config.get('S3_KEY'),
                    aws_secret_access_key=current_app.config.get('S3_SECRET')
                )
                s3.delete_object(Bucket=bucket_name, Key=s3_key_to_delete)
                current_app.logger.info(f"Successfully deleted S3 object: s3://{bucket_name}/{s3_key_to_delete}")
            except Exception as s3_e:
                current_app.logger.error(f"Error deleting S3 object s3://{bucket_name}/{s3_key_to_delete} after deleting DB record for book {book_id}: {str(s3_e)}")
        elif not bucket_name:
            current_app.logger.error(f"S3_BUCKET config missing, cannot delete S3 object for book {book_id}")

        current_app.logger.info(f"User {g.user.id} successfully deleted book {book_id}")
        return '', 204
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting book {book_id} for user {g.user.id}: {str(e)}")
        return jsonify({'error': 'Failed to delete book', 'details': str(e)}), 500

@books_bp.route('/<int:book_id>/upload', methods=['POST'])
def upload_book_file(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if book.uploaded_by_id != g.user.id:
            return jsonify({'error': 'Unauthorized to upload for this book'}), 403

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        valid_extensions = {'txt', 'pdf', 'epub', 'mobi', 'docx'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower()

        if file_ext not in valid_extensions:
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(valid_extensions)}'}), 400

        s3_key = generate_s3_file_key(book_id, file.filename)

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

        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        file_metadata = book.file_metadata or FileMetadata(book_id=book.id)
        file_metadata.file_name = secure_filename(file.filename)
        file_metadata.file_type = file_ext
        file_metadata.size = file_size

        book.s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_key}"

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
def generate_download_url(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if not validate_book_access(book, g.user.id):
            return jsonify({'error': 'Unauthorized to download this book'}), 403

        if not book.file_metadata or not book.s3_url:
            return jsonify({'error': 'No file available for download'}), 404

        s3_key = book.s3_url.split('.com/')[-1]

        try:
            download_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': S3_BUCKET,
                    'Key': s3_key,
                    'ResponseContentDisposition': f'attachment; filename="{book.file_metadata.file_name}"'
                },
                ExpiresIn=3600
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