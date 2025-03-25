from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin  # Import SerializerMixin
import re

class FileMetadata(db.Model, SerializerMixin):  # Add SerializerMixin
    __tablename__ = 'file_metadata'

    __table_args__ = {'extend_existing': True}
    
    # Enable serialization for specific fields
    serialize_only = ('id', 'file_name', 'file_type', 'size', 'book_id', 'uploaded_at')

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.Enum('txt', 'html', 'docx', 'pdf', name='file_type_enum'), nullable=False)
    size = db.Column(db.Float, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, unique=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @validates('file_name')
    def validate_file_name(self, key, file_name):
        if not file_name:
            raise ValueError('File name cannot be empty')
        if re.search(r'[<>:"/\\|?*]', file_name):
            raise ValueError('File name contains illegal characters')
        return file_name
    
    @validates('size')
    def validate_size(self, key, size):
        if size <= 0:
            raise ValueError('Size must be positive')
        if size > 100 * 1024 * 1024:  # 100 MB limit
            raise ValueError('File size exceeds maximum allowed (100 MB)')
        return size
    
    @validates('book_id')
    def validate_book(self, key, book_id):
        book = Book.query.get(book_id)
        if book is None:
            raise ValueError('Book does not exist')
        # Check if this book already has a file
        existing = FileMetadata.query.filter_by(book_id=book_id).first()
        if existing and existing.id != getattr(self, 'id', None):
            raise ValueError('Book already has a file associated with it')
        return book_id