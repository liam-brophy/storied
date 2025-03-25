#!/usr/bin/env python3

from app import app, db
from app.models.user import User
from app.models.book import Book
from app.models.note import Note
from app.models.file_metadata import FileMetadata
from app.models.friendship import Friendship
from app import bcrypt

def seed_data():
    with app.app_context():
        # Clear all data in a specific order to avoid foreign key constraints
        db.session.query(Note).delete()
        db.session.query(FileMetadata).delete()
        db.session.query(Book).delete()
        db.session.query(Friendship).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Seed Users
        users = [
            User(
                username='liam', 
                email='liam@example.com', 
                password_hash=bcrypt.generate_password_hash('password123').decode('utf-8')
            ),
            User(
                username='alice', 
                email='alice@example.com', 
                password_hash=bcrypt.generate_password_hash('alicepass').decode('utf-8')
            ),
            User(
                username='bob', 
                email='bob@example.com', 
                password_hash=bcrypt.generate_password_hash('bobpass').decode('utf-8')
            )
        ]
        
        db.session.add_all(users)
        db.session.commit()

        # Seed Friendships (optional)
        friendships = [
            Friendship(
                user_id=users[0].id, 
                friend_id=users[1].id, 
                status='accepted'
            ),
            Friendship(
                user_id=users[1].id, 
                friend_id=users[2].id, 
                status='pending'
            )
        ]

        db.session.add_all(friendships)
        db.session.commit()

        # Seed Books
        books = [
            Book(
                title='The Great Gatsby', 
                author='F. Scott Fitzgerald', 
                uploaded_by_id=users[0].id,
                s3_url='http://example.com/gatsby.pdf',
                file_size=1024,
                file_type='pdf',
                genre='Fiction'
            ),
            Book(
                title='1984', 
                author='George Orwell', 
                uploaded_by_id=users[1].id,
                s3_url='http://example.com/1984.pdf',
                file_size=1024,
                file_type='pdf',
                genre='Sci-Fi'
            ),
            Book(
                title='Brave New World', 
                author='Aldous Huxley', 
                uploaded_by_id=users[2].id,
                s3_url='http://example.com/brave_new_world.pdf',
                file_size=1024,
                file_type='pdf',
                genre='Sci-Fi'
            )
        ]

        db.session.add_all(books)
        db.session.commit()

        # Seed Notes
        notes = [
            Note(content="A haunting vision of the future.", book_id=books[0].id, user_id=users[0].id),
            Note(content="Chilling and prescient.", book_id=books[1].id, user_id=users[1].id),
            Note(content="Philosophical and eerie.", book_id=books[2].id, user_id=users[2].id)
        ]

        db.session.add_all(notes)
        db.session.commit()

        print("✅ Database seeded successfully!")

if __name__ == '__main__':
    seed_data()