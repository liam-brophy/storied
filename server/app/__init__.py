from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config 
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Initialize and configure the Flask application"""
    app = Flask(__name__)

    CORS(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storied.db'
    
    db.init_app(app)
    migrate.init_app(app, db)

    jwt = JWTManager(app)

    # Register blueprints using the function from routes
    from .routes import register_routes
    register_routes(app)

    return app