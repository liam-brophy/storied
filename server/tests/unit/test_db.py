from app.models.user import User

def test_create_and_delete_user(db_session):
    """Test creating, querying, and deleting a user."""

    # Create a new user
    new_user = User(username="test_user", email="test@example.com")
    new_user.password_hash = "ibviuwbfiugwiufgiuwgriuiuwrfgiugwiugiuwegriuhwriuhgiurehiuehiughieuh"
    db_session.add(new_user)
    db_session.commit()

    # Query the user
    user = User.query.filter_by(username="test_user").first()
    assert user is not None, "User should be found in the database"
    assert user.username == "test_user"
    assert user.email == "test@example.com"

    # Delete the user
    db_session.delete(user)
    db_session.commit()

    # Verify deletion
    deleted_user = User.query.filter_by(username="test_user").first()
    assert deleted_user is None, "User should be deleted from the database"