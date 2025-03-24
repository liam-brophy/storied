from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    books = db.relationship('Book', back_populates='uploader', lazy=True, foreign_keys='books.uploaded_by_id')
    notes = db.relationship('Note', backref='user', lazy=True)
    sent_friendships = db.relationship('Friendship', backref='user', lazy=True, foreign_keys='friendships.user_id')
    received_friendships = db.relationship('Friendship', backref='friend', lazy=True, foreign_keys='friendships.friend_id')
    
    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError('Username cannot be empty')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return username
    
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('Email cannot be empty')
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            raise ValueError('Invalid email format')
        return email
    
    @validates('oauth_provider')
    def validate_oauth_provider(self, key, provider):
        valid_providers = ['google', 'facebook', 'twitter', 'github', None]
        if provider not in valid_providers:
            raise ValueError(f'OAuth provider must be one of {valid_providers}')
        return provider