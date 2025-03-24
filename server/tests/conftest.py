import pytest
import sys
import os
from datetime import date, datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from models.strain import Strain
from models.user_strain import UserStrain
from models.diary_entry import DiaryEntry
from models.order import Order
from models.user import User
from models.post import Post
from models.comment import Comment
from models.post_tag import PostTag
from models.tag import Tag
from app import app as flask_app, api, db  # Use your existing app and db instances
from app_config import db

from app.models.book import Book
from app.models.note import Note
from app.models.friendship import Friendship

@pytest.fixture(scope="module")
def app():
    """Set up the Flask application for testing."""
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use an in-memory database
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    return flask_app


@pytest.fixture(scope="module")
def test_client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Provide a fresh database session for each test."""
    with app.app_context():
        db.create_all()  # Create all tables
        yield db.session  # Provide the session to the test
        db.session.rollback()  # Rollback any changes after the test
        db.drop_all()  # Drop all tables after the test


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(username="test_user", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_book(db_session, sample_user):
    """Create a sample book for testing."""
    book = Book(title="Sample Book", author="Author Name", uploaded_by_id=sample_user.id)
    db_session.add(book)
    db_session.commit()
    return book


@pytest.fixture
def sample_note(db_session, sample_user, sample_book):
    """Create a sample note for testing."""
    note = Note(content="Sample note content", page_number=1, user_id=sample_user.id, book_id=sample_book.id)
    db_session.add(note)
    db_session.commit()
    return note