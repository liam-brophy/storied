from flask import Blueprint, request, jsonify, g, current_app, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Friendship
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
from .auth import auth_required
from ipdb import set_trace

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
    except Exception as e:  # Fixed typo by adding "Exception as e"
        return jsonify({'error': str(e)}), 500


@user_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    """Get current user's profile"""
    user = g.user
    
    return jsonify(user.to_dict()), 200  # Use SerializerMixin

@user_bp.route('/profile', methods=['PATCH'])
@auth_required
def update_profile():
    """Update current user's profile"""
    try:
        user = g.user
        data = request.json

        #let database check uniqueness of username and email

        
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
        set_trace()
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
        return jsonify({'error': str(e)}), 500



@user_bp.route('/delete', methods=['DELETE'])
@auth_required
def delete_user():
    """Delete the current user's account using SQLAlchemy ORM."""
    try:
        user = g.user  # Get the authenticated user from g

        if not user:
            return jsonify({'error': 'No user found in session'}), 401

        # Delete friendships associated with the user (Crucial!)
        Friendship.query.filter(
            (Friendship.user_id == user.id) | (Friendship.friend_id == user.id)
        ).delete(synchronize_session=False)  # Added cascade delete in Friendship model is better
        db.session.flush()  # Flush the session to execute the delete queries

        db.session.delete(user)
        db.session.commit()

        session.pop('user_id', None) # Remove the user from the session
        return jsonify({'message': 'Account deleted successfully'}), 200

    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"IntegrityError during user deletion: {str(e)}")
        return jsonify({'error': 'Failed to delete account due to data integrity issues'}, 500)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({'error': str(e)}, 500)




# Helper function to fetch user with eager loading
def get_user_with_friendships(user_id):
    return User.query.options(
        joinedload(User.sent_friend_requests),
        joinedload(User.received_friend_requests)
    ).get(user_id)

@user_bp.route('/friends/request', methods=['POST'])
@auth_required
def send_friend_request():
    """Send a friend request to another user"""
    user_id = g.user.id
    data = request.json

    if not data.get('friend_id'):
        return jsonify({'error': 'Friend ID is required'}), 400

    friend_id = data['friend_id']

    if friend_id == user_id:
        return jsonify({'error': 'Cannot send friend request to yourself'}), 400

    # Check if friend exists
    friend = User.query.get(friend_id)  # Fetch the friend

    if not friend:
        return jsonify({'error': 'User not found'}), 404

    # Check if friendship already exists (either way)
    existing_friendship = Friendship.query.filter(
        ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
        ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
    ).first()

    if existing_friendship:
        if existing_friendship.status == 'accepted':
            return jsonify({'error': 'Already friends with this user'}), 400
        elif existing_friendship.status == 'pending':
            return jsonify({'error': 'Friend request already pending'}), 400  # Could check who sent it
        elif existing_friendship.status == 'rejected':  # Handle rejected requests as needed
            existing_friendship.status = 'pending'
            db.session.commit()
            return jsonify({'message': 'Friend request resent'}), 200

    try:
        # Create a new friendship
        friendship = Friendship(user_id=user_id, friend_id=friend_id, status='pending')
        db.session.add(friendship)
        db.session.commit()
        return jsonify(friendship.to_dict()), 201

          # Use SerializerMixin
        # return jsonify({'message': 'Friend request sent', 'id': friendship.id}), 201

    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'error': 'Integrity Error: Unable to send friend request'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending friend request: {str(e)}")
        return jsonify({'error': 'Failed to send friend request'}), 500


@user_bp.route('/friends/request/<int:request_id>/respond', methods=['POST'])
@auth_required
def respond_to_friend_request(request_id):
    """Accept or reject a friend request"""
    user_id = g.user.id
    data = request.json

    if 'status' not in data or data['status'] not in ['accepted', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be "accepted" or "rejected"'}), 400

    friendship = Friendship.query.get_or_404(request_id) # Get Friendship

    # Security check: Ensure user is the receiver
    if friendship.friend_id != user_id:
        return jsonify({'error': 'Unauthorized to respond to this request'}), 403

    if friendship.status != 'pending':
        return jsonify({'error': 'Friend request already processed'}), 400

    try:
        # Update status
        friendship.status = data['status']
        db.session.commit()
        return jsonify({'message': f'Friend request {data["status"]}'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error responding to friend request: {str(e)}")
        return jsonify({'error': 'Failed to process friend request'}), 500


@user_bp.route('/friends/<int:friendship_id>', methods=['DELETE'])
@auth_required
def remove_friend(friendship_id):
    """Remove a friend (delete friendship)"""
    user_id = g.user.id

    friendship = Friendship.query.get_or_404(friendship_id) # Get Friendship

    # Security check: Ensure user is part of this friendship
    if friendship.user_id != user_id and friendship.friend_id != user_id:
        return jsonify({'error': 'Unauthorized to remove this friendship'}), 403

    try:
        db.session.delete(friendship)
        db.session.commit()
        return jsonify({'message': 'Friendship removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing friendship: {str(e)}")
        return jsonify({'error': 'Failed to remove friendship'}), 500


@user_bp.route('/friends', methods=['GET'])
@auth_required
def get_friends():
    """Get current user's friends"""
    user_id = g.user.id

    # Load sent and received friend requests
    user = get_user_with_friendships(user_id)  # Use eager loading

    if not user:
        return jsonify({'error': 'User not found'}), 404

    friends = []

    # Process sent friend requests
    for friendship in user.sent_friend_requests:
        if friendship.status == 'accepted':
            friend = User.query.get(friendship.friend_id)
            friends.append({
                'id': friend.id,
                'username': friend.username,
                'email': friend.email  # Include other relevant user details
            })

    # Process received friend requests
    for friendship in user.received_friend_requests:
        if friendship.status == 'accepted':
            friend = User.query.get(friendship.user_id)
            friends.append({
                'id': friend.id,
                'username': friend.username,
                'email': friend.email  # Include other relevant user details
            })

    return jsonify(friends), 200


@user_bp.route('/friends/requests', methods=['GET'])
@auth_required
def get_friend_requests():
    """Get pending friend requests"""
    user_id = g.user.id
    user = get_user_with_friendships(user_id)  # Use eager loading

    if not user:
        return jsonify({'error': 'User not found'}), 404

    sent_requests = []
    received_requests = []

    # Sent requests
    for friendship in user.sent_friend_requests:
        if friendship.status == 'pending':
            friend = User.query.get(friendship.friend_id)
            sent_requests.append({
                'id': friendship.id,
                'friend_id': friend.id,
                'friend_username': friend.username
            })

    # Received requests
    for friendship in user.received_friend_requests:
        if friendship.status == 'pending':
            sender = User.query.get(friendship.user_id)
            received_requests.append({
                'id': friendship.id,
                'sender_id': sender.id,
                'sender_username': sender.username
            })

    return jsonify({'sent': sent_requests, 'received': received_requests}), 200



@user_bp.route('/search', methods=['GET'])
@auth_required
def search_users():
    """Search for users by username"""
    query = request.args.get('q', '').strip()
    set_trace()
    try:
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400

        # Search for users by username or email
        users = User.query.filter(
            (User.username.ilike(f'%{query}%'))
        ).all()

        # Serialize user data
        user_list = [user.to_dict() for user in users]

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

