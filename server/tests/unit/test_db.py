from config import db, app
from app.models.book import Book
from app.models.user import User



with app.app_context():

    new_user = User(username="test_user", email="test@example.com")
    db.session.add(new_user)
    db.session.commit()
    

    user = User.query.filter_by(username="test_user").first()
    print(f"Found user: {user.username}, {user.email}")
    

    db.session.delete(user)
    db.session.commit()