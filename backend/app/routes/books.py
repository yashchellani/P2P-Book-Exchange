# books.py
from flask import Blueprint, jsonify, request
from models import db, Book, ownership, WaitingList, WishList, BookRating
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from .utils import get_user_by_id, get_book_by_isbn, get_book_quantity, create_or_update_ownership, search_book_by_keywords
from .recommendation_engine import get_recommendations_from_ai
from flask_cors import CORS

books_blueprint = Blueprint('books', __name__)
# CORS(books_blueprint)

@books_blueprint.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for book in books:
        quantity = get_book_quantity(book)
        result.append({
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'Quantity available': quantity,
        })
    return jsonify(result), 200

@books_blueprint.route('/books', methods=['POST'])
def create_book():
    data = request.json
    isbn = data['isbn']
    book = get_book_by_isbn(isbn)
    if not book:
        book = Book(title=data['title'], author=data['author'], isbn=isbn)
        db.session.add(book)
    else:
        return jsonify({'error': 'Book already exists'}), 400
    user_id = data['owner_id']
    quantity = data.get('quantity', 1)
    user = get_user_by_id(user_id)
    if user:
        db.session.commit()
        create_or_update_ownership(book, user_id, quantity)
        return jsonify({'message': 'Book created successfully'}), 201
    else:
        db.session.rollback()
        return jsonify({'error': 'User not found'}), 404

# add multiple books at one
@books_blueprint.route('/books/add', methods=['POST'])
def add_books():
    data = request.json
    for book in data:
        user_id = book['owner_id']
        isbn = book['isbn']
        quantity = book.get('quantity', 1)
        exists = get_book_by_isbn(isbn)
        if not exists:
            add_book = Book(title=book['title'], author=book['author'], isbn=isbn)
            db.session.add(add_book)
        else:
            add_book = exists
        create_or_update_ownership(add_book, user_id, quantity)
    db.session.commit()
    return jsonify({'message': 'Books added successfully'}), 200
    
@books_blueprint.route('/books/search', methods=['POST'])
def search_book():
    data = request.json
    title = data.get('title', "")
    author = data.get('author', "")
    isbn = data.get('isbn', "")

    if not title and not author and not isbn:
        return jsonify({'error': 'Title, author, or ISBN is required'}), 400

    result = search_book_by_keywords(title=title, author=author, isbn=isbn)
    return result


#  use ai to get book recommendations based on user wishlist and past ratings
@books_blueprint.route('/books/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    wishlist = WishList.query.filter_by(user_id=user_id).all()
    past_ratings = BookRating.query.filter_by(user_id=user_id).all()

    # get the book isbn from wishlist and past_ratings, and fetch the book details
    book_names = []
    for rating in sorted(past_ratings, key=lambda x: x.rating, reverse=True):
        book_names.append(Book.query.filter_by(isbn=rating.book_isbn).first())
    for book in wishlist:
        book_names.append(Book.query.filter_by(isbn=book.book_isbn).first())
    print("book names: ", book_names)

    # get a random sample from the existing books in the database
    books_in_database = Book.query.all()

    #taking only 30 book names due to credit constraints. 
    existing_books = [(book.isbn, book.title) for book in books_in_database][0:30]

    recommendations = get_recommendations_from_ai(book_names, existing_books)
    
    return jsonify(recommendations), 200

