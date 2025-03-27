from flask import Blueprint, request, jsonify, g, current_app
from app import db
from app.models import Note, Book
from .auth import auth_required

notes_bp = Blueprint('note', __name__, url_prefix='/api/notes')


@notes_bp.route('', methods=['GET']) # <-- Ensure 'GET' is listed here
@auth_required
def get_notes():
    """Get notes for the current user, optionally filtered by book_id."""
    try:
        book_id_filter = request.args.get('book_id', type=int) # Get optional book_id query param

        query = Note.query.filter_by(user_id=g.user.id) # Always filter by logged-in user

        if book_id_filter:
            query = query.filter_by(book_id=book_id_filter)

        notes = query.order_by(Note.created_at.desc()).all() # Example ordering

        # Assuming Note model has a to_dict() method
        return jsonify([note.to_dict() for note in notes]), 200

    except Exception as e:
        current_app.logger.error(f"Error fetching notes for user {g.user.id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve notes', 'details': str(e)}), 500




@notes_bp.route('/book/<int:book_id>', methods=['GET'])
def get_notes_by_book(book_id):
    """Get all notes for a specific book that the user has access to"""
    try:
        user_id = g.user.id
        
        # Check if book exists and user has access
        book = Book.query.get_or_404(book_id)
        if not book.is_public and book.uploaded_by_id != user_id:
            return jsonify({'error': 'You do not have access to this book'}), 403
        
        # Get notes for this book made by the current user
        notes = Note.query.filter_by(
            book_id=book_id,
            user_id=user_id
        ).order_by(Note.page_number).all()
        
        return jsonify([note.to_dict() for note in notes]), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching notes: {str(e)}")
        return jsonify({'error': 'Failed to fetch notes'}), 500

@notes_bp.route('', methods=['POST'])
@auth_required
def create_note():
    """Create a new note"""
    try:
        user_id = g.user.id
        data = request.json
        
        # Check required fields
        required_fields = ['content', 'page_number', 'book_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if book exists and user has access
        book = Book.query.get_or_404(data['book_id'])
        if not book.is_public and book.uploaded_by_id != user_id:
            return jsonify({'error': 'You do not have access to this book'}), 403
        
        # Create new note
        new_note = Note(
            content=data['content'],
            page_number=data['page_number'],
            book_id=data['book_id'],
            user_id=user_id
        )
        
        db.session.add(new_note)
        db.session.commit()
        
        return jsonify(new_note.to_dict()), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating note: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note"""
    try:
        user_id = g.user.id
        
        note = Note.query.get_or_404(note_id)
        
        # Check if user has access to this note
        if note.user_id != user_id:
            return jsonify({'error': 'You do not have access to this note'}), 403
        
        return jsonify(note.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching note: {str(e)}")
        return jsonify({'error': 'Failed to fetch note'}), 500

@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        user_id = g.user.id
        
        note = Note.query.get_or_404(note_id)
        
        # Check if user has access to this note
        if note.user_id != user_id:
            return jsonify({'error': 'You do not have access to this note'}), 403
        
        data = request.json
        
        # Update fields
        if 'content' in data:
            note.content = data['content']
        if 'page_number' in data:
            note.page_number = data['page_number']
        
        db.session.commit()
        
        return jsonify(note.to_dict()), 200
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating note: {str(e)}")
        return jsonify({'error': 'Failed to update note'}), 500

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        user_id = g.user.id
        
        note = Note.query.get_or_404(note_id)
        
        # Check if user has access to this note
        if note.user_id != user_id:
            return jsonify({'error': 'You do not have access to this note'}), 403
        
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({'message': 'Note deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting note: {str(e)}")
        return jsonify({'error': 'Failed to delete note'}), 500