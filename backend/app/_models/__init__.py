from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User, UserRating, ownership
from .book import Book, BookExchange, BookRating
from .waiting_list import WaitingList
from .wish_list import WishList