from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re


class Note(db.Model):
    __tablename__ = 'notes'
    
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    @validates('page_number')
    def validate_page_number(self, key, page_number):
        if page_number <= 0:
            raise ValueError('Page number must be positive')
        return page_number
    
    @validates('book_id')
    def validate_book(self, key, book_id):
        book = Book.query.get(book_id)
        if book is None:
            raise ValueError('Book does not exist')
        return book_id
    
    @validates('user_id')
    def validate_user(self, key, user_id):
        if User.query.get(user_id) is None:
            raise ValueError('User does not exist')
        return user_id