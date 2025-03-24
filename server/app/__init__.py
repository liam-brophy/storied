from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_cors import CORS
from .config import Config
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app():
    """Initialize and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)  # Ensure your config is properly set up

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app)
    CORS(app)

    # Register routes
    from .routes import register_routes
    register_routes(app)

    return app