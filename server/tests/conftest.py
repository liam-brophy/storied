import pytest
import sys
import os
from datetime import date, datetime

# Get the project root directory
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Add the project root directory to the Python path
sys.path.insert(0, root_dir)

from app import create_app, db  # Import app factory
from app.models import User, Friendship

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
        connection = db.engine.connect()
        transaction = connection.begin()

        db_session = db.create_scoped_session(options={"bind": connection, "binds": {}})

        db.session = db_session  # Use the scoped session

        yield db_session  # Provide the session to the test

        transaction.rollback()
        connection.close()
        db_session.remove()

@pytest.fixture
def create_user(db_session):
    """Create a user."""
    def _create_user(username, email, password):
        user = User(username=username, email=email, password_hash=password)
        db_session.add(user)
        db_session.commit()
        return user

    return _create_user

@pytest.fixture
def set_session(test_client, create_user):
    """Sets the user_id in the session"""
    def _set_session(user):
        with test_client.session_transaction() as sess:
            sess['user_id'] = user.id
            return sess

    return _set_session