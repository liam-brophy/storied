from config import app
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
from app import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(port=5555, debug=True)
