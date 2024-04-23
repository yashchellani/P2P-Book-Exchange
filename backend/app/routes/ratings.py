# ratings.py
from flask import Blueprint, jsonify, request
from models import db, BookRating, UserRating, BookExchange
from .utils import get_user_by_id, get_book_by_isbn

ratings_blueprint = Blueprint('ratings', __name__)

def validate_rating_data(data, required_fields):
    for field in required_fields:
        if field not in data:
            return False
    return True

@ratings_blueprint.route('/books/rate', methods=['POST'])
def rate_book():
    data = request.json
    required_fields = ['user_id', 'book_id', 'rating']
    if not validate_rating_data(data, required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    user_id = data['user_id']
    book_id = data['book_id']
    rating = data['rating']

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    rating_entry = BookRating.query.filter_by(user_id=user_id, book_isbn=book_id).first()
    if rating_entry:
        rating_entry.rating = rating
    else:
        rating_entry = BookRating(user_id=user_id, book_isbn=book_id, rating=rating)
        db.session.add(rating_entry)

    db.session.commit()
    return jsonify({'message': 'Book rated successfully'}), 200

@ratings_blueprint.route('/users/rate', methods=['POST'])
def rate_user():
    data = request.json
    required_fields = ['rater_id', 'rated_id', 'rating']
    if not validate_rating_data(data, required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    rater_id = data['rater_id']
    rated_id = data['rated_id']
    rating = data['rating']

    rater = get_user_by_id(rater_id)
    if not rater:
        return jsonify({'error': 'Rater not found'}), 404

    rated = get_user_by_id(rated_id)
    if not rated:
        return jsonify({'error': 'Rated user not found'}), 404

    exchange = BookExchange.query.filter_by(user_id=rater_id, owner_id=rated_id, status=3).first()
    if not exchange:
        return jsonify({'error': 'You need to complete a transaction with the user first.'}), 403

    rating_entry = UserRating.query.filter_by(rater_id=rater_id, rated_id=rated_id).first()
    if rating_entry:
        rating_entry.rating = rating
    else:
        rating_entry = UserRating(rater_id=rater_id, rated_id=rated_id, rating=rating)
        db.session.add(rating_entry)

    db.session.commit()
    return jsonify({'message': 'User rated successfully'}), 200

@ratings_blueprint.route('/books/ratings/<string:book_id>', methods=['GET'])
def get_book_ratings(book_id):
    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    ratings = BookRating.query.filter_by(book_isbn=book_id).all()
    result = [{'user_id': rating.user_id, 'rating': rating.rating} for rating in ratings]
    return jsonify(result), 200

@ratings_blueprint.route('/books/ratings/<string:book_id>/average', methods=['GET'])
def get_book_average_rating(book_id):
    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    ratings = BookRating.query.filter_by(book_isbn=book_id).all()
    if not ratings:
        return jsonify({'average_rating': 0}), 200

    avg_rating = sum([rating.rating for rating in ratings]) / len(ratings)
    return jsonify({'average_rating': avg_rating}), 200

@ratings_blueprint.route('/users/books/ratings/<int:user_id>', methods=['GET'])
def get_book_ratings_by_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    ratings = BookRating.query.filter_by(user_id=user_id).all()
    result = [{'book_id': rating.book_isbn, 'rating': rating.rating} for rating in ratings]
    return jsonify(result), 200
