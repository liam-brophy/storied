from config import app
from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from models import db
from routes.user import user_bp
from routes.book import book_bp
from routes.note import note_bp

# Load environment variables
load_dotenv()

def create_app():
    """Initialize and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(note_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        return {'message': 'Reading Notes API'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5555, debug=True)
