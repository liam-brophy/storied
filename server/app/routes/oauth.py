from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session
# import requests
# from app.models.user import User
# from datetime import datetime
# import uuid
# import jwt
# from flask_jwt_extended import create_access_token, create_refresh_token

# oauth_bp = Blueprint('oauth', __name__)

# def get_oauth_providers():
#     """Dynamically fetch OAuth provider configuration."""
#     return {
#         'google': {
#             'auth_url': 'https://accounts.google.com/o/oauth2/auth',
#             'token_url': 'https://oauth2.googleapis.com/token',
#             'user_info_url': 'https://www.googleapis.com/oauth2/v1/userinfo',
#             'scope': 'openid email profile',
#             'client_id': current_app.config.get('GOOGLE_CLIENT_ID'),
#             'client_secret': current_app.config.get('GOOGLE_CLIENT_SECRET'),
#         },
#         # Add other providers as needed (GitHub, Facebook, etc.)
#     }

# @oauth_bp.route('/api/oauth/<provider>/login')
# def oauth_login(provider):
#     """Initiate OAuth flow for the specified provider."""
#     try:
#         oauth_providers = get_oauth_providers()
#         if provider not in oauth_providers:
#             return jsonify({"error": f"OAuth provider '{provider}' not supported"}), 400
        
#         # Generate state parameter to prevent CSRF attacks
#         state = str(uuid.uuid4())
#         session['oauth_state'] = state
        
#         provider_config = oauth_providers[provider]
        
#         # Create OAuth authorization URL
#         auth_url = (
#             f"{provider_config['auth_url']}?response_type=code"
#             f"&client_id={provider_config['client_id']}"
#             f"&redirect_uri={url_for('oauth.oauth_callback', provider=provider, _external=True)}"
#             f"&scope={provider_config['scope']}&state={state}"
#         )
        
#         return jsonify({"auth_url": auth_url})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @oauth_bp.route('/api/oauth/<provider>/callback')
# def oauth_callback(provider):
#     """Handle OAuth callback from provider."""
#     try:
#         oauth_providers = get_oauth_providers()
#         if provider not in oauth_providers:
#             return jsonify({"error": f"OAuth provider '{provider}' not supported"}), 400
        
#         # Verify state parameter to prevent CSRF attacks
#         if request.args.get('state') != session.get('oauth_state'):
#             return jsonify({"error": "Invalid state parameter"}), 400
        
#         # Clean up the state from session
#         session.pop('oauth_state', None)
        
#         # Get authorization code from request
#         code = request.args.get('code')
#         if not code:
#             return jsonify({"error": "No authorization code received"}), 400
        
#         # Exchange code for access token
#         provider_config = oauth_providers[provider]
#         token_response = requests.post(
#             provider_config['token_url'],
#             data={
#                 'grant_type': 'authorization_code',
#                 'code': code,
#                 'redirect_uri': url_for('oauth.oauth_callback', provider=provider, _external=True),
#                 'client_id': provider_config['client_id'],
#                 'client_secret': provider_config['client_secret'],
#             },
#             headers={'Accept': 'application/json'}
#         )
        
#         token_response.raise_for_status()
#         token_data = token_response.json()
#         access_token = token_data.get('access_token')
        
#         # Get user info from provider
#         user_info_response = requests.get(
#             provider_config['user_info_url'],
#             headers={'Authorization': f"Bearer {access_token}"}
#         )
        
#         user_info_response.raise_for_status()
#         user_info = user_info_response.json()
        
#         # Find or create user in our database
#         email = user_info.get('email')
#         if not email:
#             return jsonify({"error": "Email not provided by OAuth provider"}), 400
        
#         user = User.query.filter_by(email=email).first()
        
#         if user:
#             # Update OAuth provider info
#             user.oauth_provider = provider
#             user.updated_at = datetime.utcnow()
#         else:
#             # Create new user
#             username = user_info.get('name') or email.split('@')[0]
#             user = User(
#                 username=username,
#                 email=email,
#                 oauth_provider=provider,
#                 created_at=datetime.utcnow(),
#                 updated_at=datetime.utcnow()
#             )
#             user.save()
        
#         # Create JWT tokens for authenticated session
#         access_token = create_access_token(identity=user.id)
#         refresh_token = create_refresh_token(identity=user.id)
        
#         # Redirect to frontend with tokens
#         redirect_url = f"{current_app.config.get('FRONTEND_URL')}/auth/callback?access_token={access_token}&refresh_token={refresh_token}"
#         return redirect(redirect_url)
#     except requests.exceptions.RequestException as e:
#         return jsonify({"error": "Failed to communicate with OAuth provider", "details": str(e)}), 400
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @oauth_bp.route('/api/oauth/refresh', methods=['POST'])
# def refresh_token():
#     """Refresh the JWT access token"""
#     try:
#         refresh_token = request.json.get('refresh_token')
        
#         if not refresh_token:
#             return jsonify({"error": "Refresh token is required"}), 400
        
#         # Decode and verify the refresh token
#         token_data = jwt.decode(
#             refresh_token, 
#             current_app.config.get('JWT_SECRET_KEY'), 
#             algorithms=['HS256']
#         )
        
#         user_id = token_data['sub']
        
#         # Check if user exists
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({"error": "User not found"}), 404
        
#         # Generate new access token
#         new_access_token = create_access_token(identity=user_id)
        
#         return jsonify({
#             "access_token": new_access_token
#         })
#     except jwt.ExpiredSignatureError:
#         return jsonify({"error": "Refresh token has expired"}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({"error": "Invalid refresh token"}), 401
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500