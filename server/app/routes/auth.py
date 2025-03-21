from flask import request, jsonify, g, current_app, Blueprint
from functools import wraps
import jwt
from datetime import datetime, timedelta
from models import User


auth_bp = Blueprint('auth', __name__)


def create_access_token(user_id):
    """Create a JWT access token for the user"""
    try:
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }
        
        # Sign the token with the secret key
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return token
    except Exception as e:
        current_app.logger.error(f"Error creating access token: {str(e)}")
        return None

def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        try:
            # Check if token is in the Authorization header
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            
            if not token:
                return jsonify({'error': 'Authentication token is missing'}), 401
            
            # Decode the token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Get the user from the database
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({'error': 'Invalid authentication token'}), 401
            
            # Store the user in Flask's g object for use in the route
            g.user = user
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Authentication token has expired'}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            current_app.logger.error(f"Auth error: {str(e)}")
            return jsonify({'error': 'Invalid authentication token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated