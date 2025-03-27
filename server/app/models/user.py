from app import db 
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin  # Import SerializerMixin
# from sqlalchemy.ext.associationproxy import associationproxy
from app.models.book import Book
from app.models.friendship import Friendship
import re


class User(db.Model, SerializerMixin):  # Add SerializerMixin
    __tablename__ = 'users'
    
    __table_args__ = {'extend_existing': True}

    # SerializerMixin configuration
    serialize_rules = ('-books', '-notes','friends', '-friends.sent_friendships', '-friends.received_friendships')  # Specify fields to serialize

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # # Relationships
    books = db.relationship('Book', back_populates='uploader', lazy=True, cascade="all, delete-orphan", foreign_keys=[Book.uploaded_by_id])
    notes = db.relationship('Note', back_populates='user', lazy=True)
    sent_friendships = db.relationship('Friendship', back_populates='user', lazy=True, foreign_keys=[Friendship.user_id])
    received_friendships = db.relationship('Friendship', back_populates='friend', lazy=True, foreign_keys=[Friendship.friend_id])

#assoc proxy


    @property
    def friends(self):
        sent_friends = [{'id':friendship.friend.id, 'username':friendship.friend.username, 'email':friendship.friend.email,} for friendship in self.sent_friendships if friendship.status == 'accepted']
        received_friends = [{'id':friendship.user.id, 'username':friendship.user.username, 'email':friendship.user.email,} for friendship in self.received_friendships if friendship.status == 'accepted']
        return list(sent_friends.extend(received_friends))


#authenticate here 
#method takes potential password and compares to user pass
#return true if match, false if not 


#hybrid property to set pass
#handle password here


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