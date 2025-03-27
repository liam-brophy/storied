from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api # Keep if used by register_routes or other parts
from flask_cors import CORS
from .config import Config
from .routes import register_routes # Keep using this function
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
api = Api() # Keep if needed

def create_app(testing=False):
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- CRITICAL: Ensure SECRET_KEY is set for sessions ---
    if not app.config.get('SECRET_KEY'):
        # Load from environment or raise error - REQUIRED for sessions
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key-change-me')
        if app.config['SECRET_KEY'] == 'default-dev-key-change-me' and not app.config.get('TESTING'):
             print("Warning: Using default SECRET_KEY. Set a proper key in production.")
             # Optionally raise ValueError("SECRET_KEY must be set via environment variable or config")

    if testing:
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SECRET_KEY"] = 'test-secret'


    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    api.init_app(app) 


    CORS(
        app,
        # List allowed frontend origins
        origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            # Add production frontend URL later
        ],
        supports_credentials=True
    )

    register_routes(app)

    return app

app = create_app()