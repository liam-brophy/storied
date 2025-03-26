from flask import Blueprint, request, jsonify, g, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Friendship
from sqlalchemy.exc import IntegrityError
from .auth import auth_required

user_bp = Blueprint('user', __name__, url_prefix='/api/users')


#error handler global for 404s

@user_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        
        # Check required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate password complexity
        password = data['password']
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(password),
            oauth_provider=data.get('oauth_provider')
        )
        
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        
        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()  # Use SerializerMixin
        }), 201
        
    except (ValueError, TypeError, AttributeError, IntegrityError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        current_app.logger.error(f"Error registering user: {str(e)}")
        return jsonify({'error': 'Failed to register user'}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """Log in an existing user"""
    try:
        data = request.json
        
        # Check required fields
        if not data.get('username') and not data.get('email'):
            return jsonify({'error': 'Either username or email is required'}), 400
        
        if not data.get('password'):
            return jsonify({'error': 'Password is required'}), 400
        

        #data.get('username') or data.get('email')   .first()
        # Find user by username or email
        if data.get('username'):
            user = User.query.filter_by(username=data['username']).first()
        else:
            user = User.query.filter_by(email=data['email']).first()
        
        # Check if user exists and password is correct
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()  # Use SerializerMixin
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        return jsonify({'error': str(e)}), 500



@user_bp.route('/logout', methods=['DELETE'])
def logout():
    try:
        session.pop('user_id', None)
        return jsonify(''), 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    try:
        return jsonify(g.user.to_dict()), 200
    except:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """Get current user's profile"""
    user = g.user
    
    return jsonify(user.to_dict()), 200  # Use SerializerMixin

@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update current user's profile"""
    try:
        user = g.user
        data = request.json
        
        if 'username' in data and data['username'] != user.username:
            #if username is already taken
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            #if email is already registered
            if User.query.filter_by(email=data['email']).first():
                return jsonify({'error': 'Email already registered'}), 400
            user.email = data['email']
        
        #update password if provided
        if 'password' in data:
            #validate password complexity
            if len(data['password']) < 8:
                return jsonify({'error': 'Password must be at least 8 characters long'}), 400
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()  # Use SerializerMixin
        }), 200
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating profile: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/friends', methods=['GET'])
def get_friends():
    """Get current user's friends"""
    user_id = g.user.id
    
    #get accepted friendships
    sent_friendships = Friendship.query.filter_by(
        user_id=user_id, status='accepted'
    ).all()
    
    received_friendships = Friendship.query.filter_by(
        friend_id=user_id, status='accepted'
    ).all()
    
    friends = []
    
    for friendship in sent_friendships + received_friendships:
        friend = User.query.get(friendship.friend_id if friendship.user_id == user_id else friendship.user_id)
        friends.append({
            **friend.to_dict(),  # Use SerializerMixin
            'friendship_id': friendship.id,
            'since': friendship.updated_at.isoformat()
        })
    
    return jsonify(friends), 200

@user_bp.route('/friends/requests', methods=['GET'])
def get_friend_requests():
    """Get pending friend requests"""
    user_id = g.user.id
    
    #get pending requests sent by the user
    sent_requests = Friendship.query.filter_by(
        user_id=user_id, status='pending'
    ).all()
    
    #get pending requests received by the user
    received_requests = Friendship.query.filter_by(
        friend_id=user_id, status='pending'
    ).all()
    
    sent = [{'id': req.id, 'friend': User.query.get(req.friend_id).to_dict(), 'created_at': req.created_at.isoformat()} for req in sent_requests]
    received = [{'id': req.id, 'user': User.query.get(req.user_id).to_dict(), 'created_at': req.created_at.isoformat()} for req in received_requests]
    
    return jsonify({'sent': sent, 'received': received}), 200

@user_bp.route('/friends/request', methods=['POST'])
def send_friend_request():
    """Send a friend request to another user"""
    user_id = g.user.id
    data = request.json
    
    if not data.get('friend_id'):
        return jsonify({'error': 'Friend ID is required'}), 400
    
    friend_id = data['friend_id']
    
    #check if friend exists
    friend = User.query.get(friend_id)
    if not friend:
        return jsonify({'error': 'User not found'}), 404
    
    #check if trying to befriend self
    if friend_id == user_id:
        return jsonify({'error': 'Cannot send friend request to yourself'}), 400
    
    #check if friendship already exists
    existing = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            return jsonify({'error': 'Already friends with this user'}), 400
        elif existing.status == 'pending':
            if existing.user_id == user_id:
                return jsonify({'error': 'Friend request already sent'}), 400
            else:
                return jsonify({'error': 'This user has already sent you a friend request'}), 400
        elif existing.status == 'rejected':
            # update rejected to pending for another try
            existing.status = 'pending'
            existing.user_id = user_id
            existing.friend_id = friend_id
            db.session.commit()
            return jsonify({'message': 'Friend request sent'}), 200
    
    try:
        # create new friendship
        friendship = Friendship(
            user_id=user_id,
            friend_id=friend_id,
            status='pending'
        )
        
        db.session.add(friendship)
        db.session.commit()
        
        return jsonify({'message': 'Friend request sent', 'id': friendship.id}), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending friend request: {str(e)}")
        return jsonify({'error': 'Failed to send friend request'}), 500

@user_bp.route('/friends/request/<int:request_id>/respond', methods=['POST'])
def respond_to_friend_request(request_id):
    """Accept or reject a friend request"""
    user_id = g.user.id
    data = request.json
    
    if 'status' not in data or data['status'] not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be "accepted" or "rejected"'}), 400
    
    # find the friend request
    friendship = Friendship.query.get_or_404(request_id)
    
    # check if the request is for this user
    if friendship.friend_id != user_id:
        return jsonify({'error': 'This friend request is not for you'}), 403
    
    # check if the request is pending
    if friendship.status != 'pending':
        return jsonify({'error': 'This request has already been processed'}), 400
    
    # update the status
    friendship.status = data['status']
    
    try:
        db.session.commit()
        
        return jsonify({
            'message': f'Friend request {data["status"]}',
            'friendship': friendship.to_dict()  # Use SerializerMixin
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error responding to friend request: {str(e)}")
        return jsonify({'error': 'Failed to process friend request'}), 500

@user_bp.route('/friends/<int:friendship_id>', methods=['DELETE'])
def remove_friend(friendship_id):
    """Remove a friend (delete friendship)"""
    user_id = g.user.id
    
    # find the friendship
    friendship = Friendship.query.get_or_404(friendship_id)
    
    # check if the user is part of this friendship
    if friendship.user_id != user_id and friendship.friend_id != user_id:
        return jsonify({'error': 'You are not part of this friendship'}), 403
    
    try:
        db.session.delete(friendship)
        db.session.commit()
        
        return jsonify({'message': 'Friendship removed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing friendship: {str(e)}")
        return jsonify({'error': 'Failed to remove friendship'}), 500

@user_bp.route('/search', methods=['GET'])
def search_users():
    """Search for users by username"""
    query = request.args.get('q', '')
    
    if not query or len(query) < 3:
        return jsonify({'error': 'Search query must be at least 3 characters long'}), 400
    
    # search for users by username (exclude current user)
    users = User.query.filter(
        User.username.ilike(f'%{query}%'),
        User.id != g.user.id
    ).limit(10).all()
    
    results = [user.to_dict() for user in users]  # Use SerializerMixin
    
    return jsonify(results), 200