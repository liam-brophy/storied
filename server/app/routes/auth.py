from flask import request, jsonify, g, current_app, Blueprint, session
from functools import wraps
# import jwt
from datetime import datetime, timedelta
from ..models.user import User  
from ipdb import set_trace

auth_bp = Blueprint('auth', __name__)


# def create_access_token(user_id):
#     """Create a JWT access token for the user"""
#     try:
#         payload = {
#             'user_id': user_id,
#             'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
#         }
        
#         # Sign the token with the secret key
#         # token = jwt.encode(
#         #     payload,
#         #     current_app.config['SECRET_KEY'],
#         #     algorithm='HS256'
#         # )
        
#         # return token
#     except Exception as e:
#         current_app.logger.error(f"Error creating access token: {str(e)}")
#         return None

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        
        try:
            # Get the user from the database
            user = User.query.get(session.get('user_id', 0))
            if not user:
                return jsonify({'error': 'Login Required'}), 401
            
            # Store the user in Flask's g object for use in the route
            g.user = user

            return f(*args, **kwargs)

        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
    return decorated