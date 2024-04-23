# users.py
from flask import Blueprint, jsonify, request
from models import db, User, ownership, Book
from sqlalchemy.exc import SQLAlchemyError
from .utils import get_user_by_id

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
        user_id = new_user.id
        return jsonify({'message': f'User created successfully. UserID: {user_id}'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@users_blueprint.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(result), 200

# view all users
@users_blueprint.route('/users/all', methods=['GET'])
def get_all_users():
    users = User.query.all()
    result = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(result), 200


@users_blueprint.route('/users/<int:user_id>/books', methods=['GET'])
def get_user_books(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    books = ownership.select().where(ownership.c.user_id == user_id)
    res = db.session.execute(books).all()
    isbn_list = [row.book_isbn for row in res]
    books = Book.query.filter(Book.isbn.in_(isbn_list)).all()
    result = [{'isbn': book.isbn, 'title': book.title, 'author': book.author} for book in books]
    return jsonify(result), 200
