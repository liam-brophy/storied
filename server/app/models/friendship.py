from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy_serializer import SerializerMixin
# from sqlalchemy.orm import relationship
# from .user import User



class Friendship(db.Model, SerializerMixin):
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

    #Relationships
    user = db.relationship("User", foreign_keys=[user_id], backref="sent_friend_requests")
    friend = db.relationship("User", foreign_keys=[friend_id], backref="received_friend_requests")


    serialize_rules = ('-user', '-friend')  # Define serialization rules

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
        try:
            # Check for accepted friendship in either direction
            friendship = cls.query.filter(
                ((cls.user_id == user_id) & (cls.friend_id == target_id) | 
                 (cls.user_id == target_id) & (cls.friend_id == user_id)) & 
                (cls.status == 'accepted')
            ).first()
            return friendship is not None
        except Exception as e:
            # Log or handle the exception as needed
            print(f"Error checking friendship: {e}")
            return False

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
        try:
            friendship = cls.query.filter(
                ((cls.user_id == user_id) & (cls.friend_id == target_id) | 
                 (cls.user_id == target_id) & (cls.friend_id == user_id))
            ).first()
            return friendship.status if friendship else None
        except Exception as e:
            # Log or handle the exception as needed
            print(f"Error retrieving friendship status: {e}")
            return None