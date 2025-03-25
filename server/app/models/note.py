from app import db
from datetime import datetime
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

class Note(db.Model, SerializerMixin):
    __tablename__ = 'notes'

    # Enable serialization for specific fields
    serialize_only = ('id', 'content', 'page_number', 'book_id', 'user_id', 'created_at')

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (optional, but can help)
    book = db.relationship('Book', back_populates='notes', lazy=True)
    user = db.relationship('User', back_populates='notes', lazy=True)

    @validates('content')
    def validate_content(self, key, content):
        if not content or len(content.strip()) == 0:
            raise ValueError('Note content cannot be empty')
        return content
    
    @validates('page_number')
    def validate_page_number(self, key, page_number):
        if page_number <= 0:
            raise ValueError('Page number must be positive')
        return page_number
    
    @validates('book_id')
    def validate_book(self, key, book_id):
        from app.models import Book  # Import here to avoid circular imports
        book = Book.query.get(book_id)
        if book is None:
            raise ValueError('Book does not exist')
        return book_id
    
    @validates('user_id')
    def validate_user(self, key, user_id):
        from app.models import User  # Import here to avoid circular imports
        if User.query.get(user_id) is None:
            raise ValueError('User does not exist')
        return user_id