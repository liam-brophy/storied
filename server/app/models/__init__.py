# Import individual models to make them accessible when importing the models package
from .user import User
from .book import Book
from .author import Author

# Optionally, define __all__ to control what gets imported with `from models import *`
__all__ = ["User", "Book", "Author"]