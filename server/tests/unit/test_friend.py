# import pytest
# from app import create_app, db
# from app.models import User, Friendship
# from flask import Flask

# @pytest.fixture
# def app():
#     app = create_app()
#     app.config['TESTING'] = True
#     return app

# @pytest.fixture
# def client(app):
#     return app.test_client()
# @pytest.fixture
# def init_database(app):
#    db.create_all()
#    yield
#    db.drop_all()

# def test_send_friend_request(client, init_database):
#     """Test sending a friend request."""
#     #Set up all tests
#     # all of them
#     assert True


import pytest
from flask import Flask
from tests.conftest import app, db, create_app,User, Friendship


@pytest.fixture(scope='module')
def app():
    """Create and configure a new Flask app instance for each test module."""
    app = create_app(testing=True)
    with app.app_context():
        yield app  # provide the app instance


@pytest.fixture()
def test_client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='module')
def init_database(app):
    """Create and populate the database with test data."""
    with app.app_context():
        db.create_all()

        user1 = User(username='testuser1', email='test1@example.com', password_hash='password')
        user2 = User(username='testuser2', email='test2@example.com', password_hash='password')

        db.session.add_all([user1, user2])
        db.session.commit()

        yield db  # provide the database object

        db.session.remove()
        db.drop_all()


@pytest.fixture
def set_session(test_client, init_database, app):
    """Sets the user_id in the session"""
    db = init_database
    with app.app_context():
        user1 = User.query.filter_by(username='testuser1').first()
        with test_client.session_transaction() as sess:
            sess['user_id'] = user1.id
            yield # Provide context


def test_send_friend_request(test_client, set_session):
    """Test sending a friend request."""
    with test_client as client:
        # Set up the test
        headers = {'Content-Type': 'application/json'}
        with client.session_transaction() as sess:
            user1_id = sess.get('user_id')
        user2 = User.query.filter_by(username='testuser2').first()
        data = {'friend_id': user2.id}

        # Make the API call
        response = client.post('/api/users/friends/request', json=data, headers=headers)

        # Assert the response
        assert response.status_code == 201

        friendship = Friendship.query.filter_by(
            user_id=user1_id, friend_id=user2.id
        ).first()

        assert friendship is not None
        assert friendship.status == 'pending'