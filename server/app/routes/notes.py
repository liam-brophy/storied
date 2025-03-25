from flask import Blueprint, request, jsonify, g, current_app
from ..models import db, Note, Book
# from .auth import auth_required

notes_bp = Blueprint('note', __name__, url_prefix='/api/notes')

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
        
        result = []
        for note in notes:
            result.append({
                'id': note.id,
                'content': note.content,
                'page_number': note.page_number,
                'book_id': note.book_id,
                'created_at': note.created_at.isoformat()
            })
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching notes: {str(e)}")
        return jsonify({'error': 'Failed to fetch notes'}), 500

@notes_bp.route('', methods=['POST'])

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
        
        return jsonify({
            'id': new_note.id,
            'content': new_note.content,
            'page_number': new_note.page_number,
            'book_id': new_note.book_id,
            'user_id': new_note.user_id,
            'created_at': new_note.created_at.isoformat()
        }), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating note: {str(e)}")
        return jsonify({'error': 'Failed to create note'}), 500

@notes_bp.route('/<int:note_id>', methods=['GET'])

def get_note(note_id):
    """Get a specific note"""
    try:
        user_id = g.user.id
        
        note = Note.query.get_or_404(note_id)
        
        # Check if user has access to this note
        if note.user_id != user_id:
            return jsonify({'error': 'You do not have access to this note'}), 403
        
        return jsonify({
            'id': note.id,
            'content': note.content,
            'page_number': note.page_number,
            'book_id': note.book_id,
            'created_at': note.created_at.isoformat()
        }), 200
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
        
        return jsonify({
            'id': note.id,
            'content': note.content,
            'page_number': note.page_number,
            'book_id': note.book_id,
            'created_at': note.created_at.isoformat()
        }), 200
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