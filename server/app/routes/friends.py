from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from app.models.user import User
from app.models.friendship import Friendship
from app.models.book import Book
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/api/friends', methods=['GET'])
@jwt_required()
def get_friends():
    """Get the current user's friends"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find all accepted friendships where the current user is involved
        friendships = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == current_user_id, Friendship.status == 'accepted'),
                and_(Friendship.friend_id == current_user_id, Friendship.status == 'accepted')
            )
        ).all()
        
        friends_list = []
        
        for friendship in friendships:
            # Determine which ID is the friend
            friend_id = friendship.friend_id if friendship.user_id == current_user_id else friendship.user_id
            
            # Get the friend's user object
            friend = User.query.get(friend_id)
            
            if friend:
                friends_list.append({
                    "id": friend.id,
                    "username": friend.username,
                    "friendship_id": friendship.id,
                    "created_at": friendship.created_at.isoformat() if hasattr(friendship, 'created_at') else None
                })
        
        return jsonify({
            "friends": friends_list,
            "count": len(friends_list)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    """Get pending friend requests for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find all pending friendships where the current user is the recipient
        pending_requests = Friendship.query.filter(
            Friendship.friend_id == current_user_id,
            Friendship.status == 'pending'
        ).all()
        
        requests_list = []
        
        for request in pending_requests:
            # Get the requestor's user object
            requestor = User.query.get(request.user_id)
            
            if requestor:
                requests_list.append({
                    "id": request.id,
                    "user": {
                        "id": requestor.id,
                        "username": requestor.username
                    },
                    "created_at": request.created_at.isoformat() if hasattr(request, 'created_at') else None
                })
        
        return jsonify({
            "requests": requests_list,
            "count": len(requests_list)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/add/<int:user_id>', methods=['POST'])
@jwt_required()
def send_friend_request(user_id):
    """Send a friend request to another user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if the user exists
        target_user = User.query.get(user_id)
        if not target_user:
            return jsonify({"error": "User not found"}), 404
        
        # Can't friend yourself
        if current_user_id == user_id:
            return jsonify({"error": "You cannot send a friend request to yourself"}), 400
        
        # Check if a friendship already exists
        existing_friendship = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == current_user_id, Friendship.friend_id == user_id),
                and_(Friendship.user_id == user_id, Friendship.friend_id == current_user_id)
            )
        ).first()
        
        if existing_friendship:
            if existing_friendship.status == 'accepted':
                return jsonify({"error": "You are already friends with this user"}), 400
            elif existing_friendship.status == 'pending':
                # If the other user sent the request, accept it
                if existing_friendship.user_id == user_id:
                    existing_friendship.status = 'accepted'
                    existing_friendship.updated_at = datetime.utcnow()
                    existing_friendship.save()
                    return jsonify({"message": "Friend request accepted"}), 200
                # If current user already sent the request
                else:
                    return jsonify({"error": "Friend request already sent"}), 400
        
        # Create new friendship request
        new_friendship = Friendship(
            user_id=current_user_id,
            friend_id=user_id,
            status='pending',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        new_friendship.save()
        
        return jsonify({
            "message": "Friend request sent successfully",
            "friendship_id": new_friendship.id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    """Accept a pending friend request"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find the friendship request
        friendship = Friendship.query.get(request_id)
        
        if not friendship:
            return jsonify({"error": "Friend request not found"}), 404
        
        # Verify the current user is the recipient of the request
        if friendship.friend_id != current_user_id:
            return jsonify({"error": "You are not authorized to accept this request"}), 403
        
        # Verify the request is pending
        if friendship.status != 'pending':
            return jsonify({"error": "This request has already been processed"}), 400
        
        # Accept the request
        friendship.status = 'accepted'
        friendship.updated_at = datetime.utcnow()
        friendship.save()
        
        # Get the requestor's info
        requestor = User.query.get(friendship.user_id)
        
        return jsonify({
            "message": "Friend request accepted",
            "friendship": {
                "id": friendship.id,
                "user": {
                    "id": requestor.id,
                    "username": requestor.username
                },
                "status": friendship.status
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_friend_request(request_id):
    """Reject a pending friend request"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find the friendship request
        friendship = Friendship.query.get(request_id)
        
        if not friendship:
            return jsonify({"error": "Friend request not found"}), 404
        
        # Verify the current user is the recipient of the request
        if friendship.friend_id != current_user_id:
            return jsonify({"error": "You are not authorized to reject this request"}), 403
        
        # Verify the request is pending
        if friendship.status != 'pending':
            return jsonify({"error": "This request has already been processed"}), 400
        
        # Delete the request
        friendship.delete()
        
        return jsonify({
            "message": "Friend request rejected"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/<int:friendship_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friendship_id):
    """Remove a friend"""
    try:
        current_user_id = get_jwt_identity()
        
        # Find the friendship
        friendship = Friendship.query.get(friendship_id)
        
        if not friendship:
            return jsonify({"error": "Friendship not found"}), 404
        
        # Verify the current user is part of this friendship
        if friendship.user_id != current_user_id and friendship.friend_id != current_user_id:
            return jsonify({"error": "You are not authorized to remove this friendship"}), 403
        
        # Delete the friendship
        friendship.delete()
        
        return jsonify({
            "message": "Friend removed successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@friends_bp.route('/api/friends/<int:friend_id>/books', methods=['GET'])
@jwt_required()
def get_friend_books(friend_id):
    """Get books shared by a friend"""
    try:
        current_user_id = get_jwt_identity()
        
        # Check if they are friends
        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == current_user_id, Friendship.friend_id == friend_id, Friendship.status == 'accepted'),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user_id, Friendship.status == 'accepted')
            )
        ).first()
        
        if not friendship:
            return jsonify({"error": "You are not friends with this user"}), 403
        
        # Get the friend's books that are either public or shared
        books = Book.query.filter(
            Book.uploaded_by_id == friend_id,
            or_(
                Book.is_public == True,
                # Add additional sharing criteria here if needed
            )
        ).all()
        
        books_list = []
        
        for book in books:
            books_list.append({
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "is_public": book.is_public,
                "uploaded_at": book.created_at.isoformat() if hasattr(book, 'created_at') else None
            })
        
        friend = User.query.get(friend_id)
        
        return jsonify({
            "friend": {
                "id": friend.id,
                "username": friend.username
            },
            "books": books_list,
            "count": len(books_list)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500