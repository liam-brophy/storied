from app import db
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

class Book(db.Model, SerializerMixin):
    __tablename__ = 'books'

    # Fields to include in serialization
    serialize_rules = ('-notes', '-uploader.books', '-file_metadata.book')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50), default='Unknown')
    is_public = db.Column(db.Boolean, default=True, nullable=False)
    s3_url = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    notes = db.relationship('Note', back_populates='book', lazy='dynamic', cascade='all, delete-orphan')
    uploader = db.relationship('User', back_populates='books', lazy=True)
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
        # Use deferred import to avoid circular dependency
        from .user import User
        if User.query.get(user_id) is None:
            raise ValueError('Uploaded by user does not exist')
        return user_id