import pytest
import sys
import os
from datetime import date, datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app import create_app, db  # Import app factory

@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""
    flask_app = create_app(testing=True)  # Ensure testing mode
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    with flask_app.app_context():
        db.create_all()
    
    yield flask_app  # Provide the app to tests
    
    with flask_app.app_context():
        db.drop_all()  # Cleanup

@pytest.fixture(scope="module")
def test_client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()

@pytest.fixture(scope="function")
def db_session(app):
    """Provide a fresh database session for each test."""
    with app.app_context():
        db.session.begin()
        yield db.session  # Provide the session to the test
        db.session.rollback()  # Rollback changes after test