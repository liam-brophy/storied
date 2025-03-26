from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_cors import CORS
from .config import Config
from .routes import register_routes
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv()
# from .models import Book, FileMetadata, User, Note, Friendship

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api()

def create_app(testing=False):
    """Initialize and configure the Flask application."""
    app = Flask(__name__)

    # Load default config
    app.config.from_object(Config)

    # Override settings for testing
    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLALCHEMY_DATABASE_URI

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app)
    CORS(app)

    register_routes(app)

    return app

app = create_app()


def configure_cors(app):
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",  # Vite default dev server
                "http://127.0.0.1:5173",
                # Add your production frontend URL when deployed
            ]
        }
    })