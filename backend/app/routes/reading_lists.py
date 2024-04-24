# reading_lists.py
from flask import Blueprint, jsonify, request
from models import db, WishList
from sqlalchemy.exc import SQLAlchemyError
from .utils import get_user_by_id

reading_lists_blueprint = Blueprint("reading_lists", __name__)


@reading_lists_blueprint.route("/users/books/wishlist", methods=["POST"])
def add_to_wishlist():
    data = request.json
    user_id = data.get("user_id")
    book_ids = data.get("book_ids", [])
    if not book_ids:
        return jsonify({"error": "Book IDs are required"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    for book_id in book_ids:
        reading_list_entry = WishList(user_id=user_id, book_isbn=book_id)
        db.session.add(reading_list_entry)
    db.session.commit()
    return jsonify({"message": "Books added to reading list"}), 200


# view all books in reading list
@reading_lists_blueprint.route("/users/books/wishlist/<int:user_id>", methods=["GET"])
def get_wishlist(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    books = WishList.query.filter_by(user_id=user_id).all()
    result = [{"isbn": book.book_isbn} for book in books]
    return jsonify(result), 200
