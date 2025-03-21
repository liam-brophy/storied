from flask import Blueprint
from app.routes.auth import auth_bp
from app.routes.oauth import oauth_bp
from app.routes.books import books_bp
from app.routes.notes import notes_bp
from app.routes.search import search_bp
from app.routes.upload import upload_bp
from app.routes.user import user_bp
from app.routes.friends import friends_bp

#main API blueprint that all other blueprints will be registered to
api_bp = Blueprint('api', __name__)

#all route blueprints with the main API blueprint
def register_routes(app):
    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(oauth_bp)
    api_bp.register_blueprint(books_bp)
    api_bp.register_blueprint(notes_bp)
    api_bp.register_blueprint(search_bp)
    api_bp.register_blueprint(upload_bp)
    api_bp.register_blueprint(user_bp)
    api_bp.register_blueprint(friends_bp)
    
    #the main api blueprint with the app
    app.register_blueprint(api_bp, url_prefix='/api')
    
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers for common HTTP errors"""
    
    @app.errorhandler(400)
    def bad_request(e):
        return {"error": "Bad request", "message": str(e)}, 400
        
    @app.errorhandler(401)
    def unauthorized(e):
        return {"error": "Unauthorized", "message": "Authentication required"}, 401
        
    @app.errorhandler(403)
    def forbidden(e):
        return {"error": "Forbidden", "message": "You don't have permission to access this resource"}, 403
        
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Not found", "message": "The requested resource was not found"}, 404
        
    @app.errorhandler(500)
    def server_error(e):
        return {"error": "Server error", "message": "An internal server error occurred"}, 500