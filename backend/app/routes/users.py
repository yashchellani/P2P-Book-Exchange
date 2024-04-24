# users.py
from flask import Blueprint, jsonify, request
from models import db, User, ownership, Book, WishList, BookExchange
from sqlalchemy.exc import SQLAlchemyError
from .utils import get_user_by_id
from flask_cors import CORS

users_blueprint = Blueprint("users", __name__)
CORS(users_blueprint)


@users_blueprint.route("/users", methods=["POST", "OPTIONS"])
def create_user():
    data = request.json
    new_user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )
    db.session.add(new_user)
    try:
        db.session.commit()
        user_id = new_user.id
        return (
            jsonify({"message": f"User created successfully. UserID: {user_id}"}),
            201,
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@users_blueprint.route("/users/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.password != password:
        return jsonify({"error": "Invalid password"}), 401
    return jsonify({"message": "Login successful", "user_id": user.id}), 200


@users_blueprint.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = [
        {"id": user.id, "username": user.username, "email": user.email}
        for user in users
    ]
    return jsonify(result), 200


@users_blueprint.route("/users/all", methods=["GET"])
def get_all_users():
    users = User.query.all()
    result = [
        {"id": user.id, "username": user.username, "email": user.email}
        for user in users
    ]
    return jsonify(result), 200


@users_blueprint.route("/users/<int:user_id>/books", methods=["GET"])
def get_user_books(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    books = ownership.select().where(ownership.c.user_id == user_id)
    res = db.session.execute(books).all()
    isbn_list = [row.book_isbn for row in res]
    books = Book.query.filter(Book.isbn.in_(isbn_list)).all()
    result = [
        {"isbn": book.isbn, "title": book.title, "author": book.author}
        for book in books
    ]
    return jsonify(result), 200


@users_blueprint.route("/users/<int:book_id>/wishlist", methods=["POST"])
def add_to_wishlist(book_id):
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    waiting_list_entry = WishList(user_id=user_id, book_isbn=book_id)
    db.session.add(waiting_list_entry)
    db.session.commit()
    return jsonify({"message": "Book added to wishlist"}), 200


@users_blueprint.route("/users/<int:user_id>/wishlist", methods=["GET"])
def get_wishlist(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    books = WishList.query.filter_by(user_id=user_id).all()
    result = [{"isbn": book.book_isbn} for book in books]
    return jsonify(result), 200


@users_blueprint.route("/users/<int:user_id>/books/borrowed", methods=["GET"])
def get_borrowed_books(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    books = BookExchange.query.filter_by(buyer=user_id).all()
    result = []
    for book in books:
        book_info = Book.query.filter_by(isbn=book.book_isbn).first()
        book.title = book_info.title
        book.author = book_info.author
        result.append(
            {
                "isbn": book.book_isbn,
                "title": book.title,
                "author": book.author,
                "status": book.status.value,
            }
        )

    return jsonify(result), 200
