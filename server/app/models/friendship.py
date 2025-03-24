from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint

class Friendship(db.Model):
    __tablename__ = 'friendships'
    
    __table_args__ = (
        UniqueConstraint('user_id', 'friend_id', name='_unique_friendship'),
        CheckConstraint('user_id != friend_id', name='_prevent_self_friendship'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Friendship status options
    status_choices = ['pending', 'accepted', 'blocked']
    status = db.Column(
        db.Enum(*status_choices, name='friendship_status'), 
        default='pending', 
        nullable=False
    )
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )

    def __repr__(self):
        return f'<Friendship {self.user_id} - {self.friend_id}: {self.status}>'

    @classmethod
    def are_friends(cls, user_id, target_id):
        """
        Check if two users are friends
        
        Args:
            user_id (int): ID of first user
            target_id (int): ID of second user
        
        Returns:
            bool: Whether users are friends
        """
        # Check for accepted friendship in either direction
        friendship = cls.query.filter(
            ((cls.user_id == user_id) & (cls.friend_id == target_id) | 
             (cls.user_id == target_id) & (cls.friend_id == user_id)) & 
            (cls.status == 'accepted')
        ).first()
        
        return friendship is not None

    @classmethod
    def get_friendship_status(cls, user_id, target_id):
        """
        Get the friendship status between two users
        
        Args:
            user_id (int): ID of first user
            target_id (int): ID of second user
        
        Returns:
            str: Friendship status ('pending', 'accepted', 'blocked', or None)
        """
        friendship = cls.query.filter(
            ((cls.user_id == user_id) & (cls.friend_id == target_id) | 
             (cls.user_id == target_id) & (cls.friend_id == user_id))
        ).first()
        
        return friendship.status if friendship else None