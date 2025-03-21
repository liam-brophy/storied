from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import re

class Friendship(db.Model):
    __tablename__ = 'friendships'

    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum('pending', 'accepted', 'rejected', name='friendship_status_enum'), 
                        default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='unique_friendship'),
    )
    
    @validates('friend_id')
    def validate_friend(self, key, friend_id):
        if friend_id == self.user_id:
            raise ValueError('Cannot befriend yourself')
        if User.query.get(friend_id) is None:
            raise ValueError('Friend user does not exist')
        return friend_id
    
    @validates('user_id')
    def validate_user(self, key, user_id):
        if User.query.get(user_id) is None:
            raise ValueError('User does not exist')
        return user_id