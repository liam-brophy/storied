from flask import request, jsonify, g, current_app, Blueprint, session
from functools import wraps
from datetime import datetime, timedelta
from app.models.user import User  # Changed to absolute import
from sqlalchemy.orm.exc import NoResultFound
from ipdb import set_trace

auth_bp = Blueprint('auth', __name__)


def auth_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            print(f"Session data in auth_required: {session.get('user_id')}") #Debug session
            user_id = session.get('user_id')

            if user_id is None:
                current_app.logger.debug("auth_required: No user_id in session")
                return jsonify({'error': 'Login Required: No session'}), 401

            try:
                user = User.query.filter_by(id=user_id).one() #Use filter_by and one() to catch user not found
            except NoResultFound:
                current_app.logger.warning(f"auth_required: User with id {user_id} not found")
                session.pop('user_id', None)  # Clear potentially invalid session
                return jsonify({'error': 'Login Required: Invalid user'}), 401

            g.user = user
            return f(*args, **kwargs)

        except Exception as e:
            current_app.logger.error(f"auth_required: Exception during authentication: {type(e).__name__}: {str(e)}") # log exception
            return jsonify({'error': f'Authentication Error: {str(e)}'}), 500

    return decorated