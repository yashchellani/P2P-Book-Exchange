from flask import Blueprint, jsonify, request
import random
from models import db, Book, ownership, WaitingList, WishList, BookRating, BookExchange
from sqlalchemy import and_
from .utils import (
    get_user_by_id,
    get_book_by_isbn,
    get_book_quantity,
    create_or_update_ownership,
    search_book_by_keywords,
)
from .recommendation_engine import get_recommendations_from_ai
from flask_cors import CORS

books_blueprint = Blueprint("books", __name__)
CORS(books_blueprint)


def serialize_book(book, owner_id):
    quantity = get_book_quantity(book)
    return {
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "quantity": quantity,
        "owner_id": owner_id,
    }


@books_blueprint.route("/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    result = []
    for book in books:
        owns = ownership.select().where(
            and_(ownership.c.book_isbn == book.isbn, ownership.c.quantity > 0)
        )
        owner = db.session.execute(owns).first()
        owner_id = owner[0] if owner else None
        result.append(serialize_book(book, owner_id))
    return jsonify(result), 200


#deprecated method, do not use
@books_blueprint.route("/books", methods=["POST"])
def create_book():
    data = request.json
    isbn = data["isbn"]
    book = get_book_by_isbn(isbn)
    if book:
        return jsonify({"error": "Book already exists"}), 400
    book = Book(title=data["title"], author=data["author"], isbn=isbn)
    db.session.add(book)
    user_id = data["owner_id"]
    quantity = data.get("quantity", 1)
    user = get_user_by_id(user_id)
    if not user:
        db.session.rollback()
        return jsonify({"error": "User not found"}), 404
    db.session.commit()
    create_or_update_ownership(book, user_id, quantity)
    return jsonify({"message": "Book created successfully"}), 201


@books_blueprint.route("/books/add", methods=["POST"])
def add_books():
    """
    add multiple books at one go
    allow multiple people to list the same isbn
    """
    data = request.json
    for book in data:
        user_id = book["owner_id"]
        isbn = book["isbn"]
        quantity = book.get("quantity", 1)
        exists = get_book_by_isbn(isbn)
        if not exists:
            add_book = Book(title=book["title"], author=book["author"], isbn=isbn)
            db.session.add(add_book)
        else:
            add_book = exists
        create_or_update_ownership(add_book, user_id, quantity)
        BookExchange.query.filter_by(buyer=user_id, book_isbn=isbn).delete()
    db.session.commit()
    return jsonify({"message": "Books added successfully"}), 200


@books_blueprint.route("/books/search", methods=["POST"])
def search_book():
    data = request.json
    title = data.get("title", "")
    author = data.get("author", "")
    isbn = data.get("isbn", "")
    if not any([title, author, isbn]):
        return jsonify({"error": "Title, author, or ISBN is required"}), 400
    result = search_book_by_keywords(title=title, author=author, isbn=isbn)
    return result


@books_blueprint.route("/books/recommendations", methods=["POST"])
def get_recommendations():
    """
    sample 20 random books that a user might have interacted with based on their wishlist, past ratings, and books given away
    using the list of other available books, get recommendations from the AI model
    """
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # get books that the user has interacted with
    wishlist = WishList.query.filter_by(user_id=user_id).all()
    past_ratings = BookRating.query.filter(and_(BookRating.user_id == user_id, BookRating.rating >= 4)).all()
    books_sold = BookExchange.query.filter_by(seller=user_id).all()
    
    book_names = [
        Book.query.filter_by(isbn=item.book_isbn).first()
        for item in wishlist + past_ratings + books_sold
    ]

    # randomly sample 20 books from book_names
    book_names = random.sample(book_names, min(20, len(book_names)))

    # get books not  currentlyowned by the user
    owns = ownership.select().where(ownership.c.user_id != user_id)
    res = db.session.execute(owns).all()
    existing_books = [row.book_isbn for row in res][:30]

    recommendations = get_recommendations_from_ai(book_names, existing_books)
    result = []
    for recommendation in recommendations:
        book = Book.query.filter_by(isbn=recommendation.strip()).first()
        if book:
            result.append(
                {"isbn": book.isbn, "title": book.title, "author": book.author}
            )
    return jsonify(result), 200
