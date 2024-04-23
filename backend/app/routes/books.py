# books.py
from flask import Blueprint, jsonify, request
from models import db, Book, ownership, WaitingList, WishList, BookRating
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from .utils import get_user_by_id, get_book_by_isbn, get_book_quantity, create_or_update_ownership, search_book_by_keywords
from .recommendation_engine import get_recommendations_from_ai

books_blueprint = Blueprint('books', __name__)

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
    data = request.get_json()
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
    
@books_blueprint.route('/books/search/', methods=['GET'])
def search_book():
    title = request.args.get('title')
    author = request.args.get('author')
    isbn = request.args.get('isbn')

    if not title and not author and not isbn:
        return jsonify({'error': 'Title, author, or ISBN is required'}), 400

    result = search_book_by_keywords(title=title, author=author, isbn=isbn)
    return result


#  use ai to get book recommendations based on user wishlist and past ratings
@books_blueprint.route('/books/recommendations', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    # Call ChatGPT API to get book recommendations
    # get user's wishlist
    # get user's past ratings

    wishlist = WishList.query.filter_by(user_id=user_id).all()
    past_ratings = BookRating.query.filter_by(user_id=user_id).all()

    # get the book isbn from wishlist and past_ratings, and fetch the book details
    book_names = []
    for rating in sorted(past_ratings, key=lambda x: x.rating, reverse=True):
        book_names.append(Book.query.filter_by(isbn=rating.book_isbn).first())
    for book in wishlist:
        book_names.append(Book.query.filter_by(isbn=book.book_isbn).first())

    recommendations = get_recommendations_from_ai(book_names)
    
    return jsonify(recommendations), 200

