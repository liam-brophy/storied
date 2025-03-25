from flask import Blueprint

# Create the main API blueprint
api_bp = Blueprint('api', __name__)

# Define the register_routes function without importing blueprints here
def register_routes(app):
    # Import blueprints inside the function to avoid circular imports
    # from .auth import auth_bp  
    # from .oauth import oauth_bp
    from .books import books_bp
    from .notes import notes_bp
    from .search import search_bp
    from .upload import upload_bp
    from .user import user_bp
    from .friends import friends_bp
    
    # # Register blueprints with the main API blueprint
    # api_bp.register_blueprint(auth_bp)
    # api_bp.register_blueprint(oauth_bp)
    api_bp.register_blueprint(books_bp)
    api_bp.register_blueprint(notes_bp)
    api_bp.register_blueprint(search_bp)
    api_bp.register_blueprint(upload_bp)
    api_bp.register_blueprint(user_bp)
    api_bp.register_blueprint(friends_bp)
    
    # Register the main API blueprint with the app
    app.register_blueprint(api_bp, url_prefix='/api')
    
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    # Your error handlers code remains the same
    # ...

    #UPLOAD HELPER
    #Download Helper