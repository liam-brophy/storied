from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from server.app.models.book import Book
from server.app.models.user import User
from server.app.models.friendship import Friendship
from flask_jwt_extended import jwt_required, get_jwt_identity

search_bp = Blueprint('search', __name__)

@search_bp.route('/api/search', methods=['GET'])
@jwt_required()
def search():
    """Search for books and users"""
    try:
        # Get the current user ID
        current_user_id = get_jwt_identity()
        
        # Get search parameters
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'all')  # 'all', 'books', 'users'
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Validate the search term
        if not query or len(query) < 2:
            return jsonify({"error": "Search query must be at least 2 characters"}), 400
        
        results = {"books": [], "users": [], "total_count": 0}
        
        # Search books
        if search_type in ['all', 'books']:
            # Get user friends to determine which books they can see
            friends_query = Friendship.query.filter(
                or_(
                    Friendship.user_id == current_user_id,
                    Friendship.friend_id == current_user_id
                ),
                Friendship.status == 'accepted'
            )
            
            friend_ids = []
            for friendship in friends_query.all():
                if friendship.user_id == current_user_id:
                    friend_ids.append(friendship.friend_id)
                else:
                    friend_ids.append(friendship.user_id)
            
            # Books query - include public books or books owned by the user or their friends
            books_query = Book.query.filter(
                and_(
                    or_(
                        Book.is_public == True,
                        Book.uploaded_by_id == current_user_id,
                        Book.uploaded_by_id.in_(friend_ids)
                    ),
                    or_(
                        Book.title.ilike(f'%{query}%'),
                        Book.author.ilike(f'%{query}%'),
                        Book.genre.ilike(f'%{query}%')
                    )
                )
            )
            
            # Paginate books results
            books_pagination = books_query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Format books for response
            for book in books_pagination.items:
                uploader = User.query.get(book.uploaded_by_id)
                book_data = {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre,
                    "is_public": book.is_public,
                    "uploader": {
                        "id": uploader.id,
                        "username": uploader.username
                    }
                }
                results["books"].append(book_data)
        
        # Search users
        if search_type in ['all', 'users']:
            # Users query - search by username
            users_query = User.query.filter(
                User.username.ilike(f'%{query}%'),
                User.id != current_user_id  # Exclude current user
            )
            
            # Paginate users results
            users_pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Format users for response
            for user in users_pagination.items:
                # Check if they're friends
                friendship = Friendship.query.filter(
                    or_(
                        and_(Friendship.user_id == current_user_id, Friendship.friend_id == user.id),
                        and_(Friendship.user_id == user.id, Friendship.friend_id == current_user_id)
                    )
                ).first()
                
                friendship_status = None
                if friendship:
                    friendship_status = friendship.status
                
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "friendship_status": friendship_status
                }
                results["users"].append(user_data)
        
        # Calculate total count
        if search_type == 'books':
            results["total_count"] = books_query.count()
        elif search_type == 'users':
            results["total_count"] = users_query.count()
        else:
            results["total_count"] = (books_query.count() if 'books_query' in locals() else 0) + (users_query.count() if 'users_query' in locals() else 0)
        
        # Add pagination info
        results["pagination"] = {
            "page": page,
            "per_page": per_page,
            "has_next": books_pagination.has_next if search_type in ['books', 'all'] else users_pagination.has_next,
            "has_prev": books_pagination.has_prev if search_type in ['books', 'all'] else users_pagination.has_prev,
            "total_pages": books_pagination.pages if search_type in ['books', 'all'] else users_pagination.pages
        }
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@search_bp.route('/api/books/<int:book_id>', methods=['GET'])
@jwt_required()
def get_book_details(book_id):
    """Get detailed information about a specific book"""
    try:
        current_user_id = get_jwt_identity()
        
        book = Book.query.get(book_id)
        
        if not book:
            return jsonify({"error": "Book not found"}), 404
        
        # Check if user has access to view this book
        if not book.is_public and book.uploaded_by_id != current_user_id:
            # Check if they're friends
            friendship = Friendship.query.filter(
                or_(
                    and_(Friendship.user_id == current_user_id, Friendship.friend_id == book.uploaded_by_id, Friendship.status == 'accepted'),
                    and_(Friendship.user_id == book.uploaded_by_id, Friendship.friend_id == current_user_id, Friendship.status == 'accepted')
                )
            ).first()
            
            if not friendship:
                return jsonify({"error": "You don't have permission to view this book"}), 403
        
        uploader = User.query.get(book.uploaded_by_id)
        
        # Get book details including notes count
        book_data = {
            "id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "is_public": book.is_public,
            "uploaded_at": book.created_at.isoformat() if hasattr(book, 'created_at') else None,
            "uploader": {
                "id": uploader.id,
                "username": uploader.username
            },
            "notes_count": len(book.notes) if hasattr(book, 'notes') else 0
        }
        
        return jsonify(book_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500