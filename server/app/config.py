import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Generate a random secret key for development or use environment variable
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
    
    # # JWT settings
    # JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_jwt_secret_key")
    # JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    # JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///e_reader.db")
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), '../uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # OAuth settings
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Frontend URL for redirects
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'
    
    # AWS settings
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")