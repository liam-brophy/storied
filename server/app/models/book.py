from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re


class Book(db.Model):
    __tablename__ = 'books'

    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), default='Unknown')
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    content = db.Column(db.Text, nullable=True)  #WILL USE BOTO3
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    notes = db.relationship('Note', backref='book', lazy=True, cascade='all, delete-orphan')
    file_metadata = db.relationship('FileMetadata', backref='book', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError('Title cannot be empty')
        if len(title) < 2:
            raise ValueError('Title must be at least 2 characters long')
        return title
    
    @validates('genre')
    def validate_genre(self, key, genre):
        valid_genres = ['Fiction', 'Non-Fiction', 'Fantasy', 'Sci-Fi', 'Mystery', 
                        'Thriller', 'Romance', 'Biography', 'History', 'Self-Help', 
                        'Poetry', 'Academic', 'Unknown']
        if genre not in valid_genres:
            raise ValueError(f'Genre must be one of {valid_genres}')
        return genre
    
    @validates('uploaded_by_id')
    def validate_uploader(self, key, user_id):
        if User.query.get(user_id) is None:
            raise ValueError('Uploaded by user does not exist')
        return user_id