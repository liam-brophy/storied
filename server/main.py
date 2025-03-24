from config import app, db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
import os
from dotenv import load_dotenv
from models import db
from routes.user import user_bp
from routes.book import book_bp
from routes.note import note_bp
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

app.config.update(
    AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID'),
    AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY'),
    AWS_REGION=os.getenv('AWS_REGION'),
    S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')
)

app = create_app()

if __name__ == '__main__':
    app.run(port=5555, debug=True)
