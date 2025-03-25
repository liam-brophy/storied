from app import db
from datetime import datetime
from sqlalchemy.orm import validates

class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships (optional, but can help)
    book = db.relationship('Book', backref=db.backref('notes', lazy=True))
    user = db.relationship('User', backref=db.backref('notes', lazy=True))
    
    @validates('page_number')
    def validate_page_number(self, key, page_number):
        if page_number <= 0:
            raise ValueError('Page number must be positive')
        return page_number
    
    @validates('book_id')
    def validate_book(self, key, book_id):
        from models import Book  # Import here to avoid circular imports
        book = Book.query.get(book_id)
        if book is None:
            raise ValueError('Book does not exist')
        return book_id
    
    @validates('user_id')
    def validate_user(self, key, user_id):
        from models import User  # Import here to avoid circular imports
        if User.query.get(user_id) is None:
            raise ValueError('User does not exist')
        return user_id