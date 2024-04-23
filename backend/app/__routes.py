from flask import Blueprint, jsonify, request
from models import db, User, Book, BookRating, ownership
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_

routes_blueprint = Blueprint('routes', __name__)

# Run before the first request to create tables
@routes_blueprint.before_app_request
def create_tables():
    db.create_all()

# Utility function to get book quantity
def get_book_quantity(book):
    owners = ownership.select().where(ownership.c.book_isbn == book.isbn)
    res = db.session.execute(owners).all()
    return sum([row.quantity for row in res])

# Utility function to get user by id
def get_user_by_id(user_id):
    return User.query.get(user_id)

# Utility function to get book by isbn
def get_book_by_isbn(isbn):
    return Book.query.get(isbn)

# Utility function to create or update book ownership
def create_or_update_ownership(book, user_id, quantity):
    current_quantity = ownership.select().where(and_(ownership.c.book_isbn == book.isbn, ownership.c.user_id == user_id))
    res = db.session.execute(current_quantity).all()
    quantity += res[0].quantity if res else 0

    if res:
        ownership_entry = ownership.update().where(and_(ownership.c.book_isbn == book.isbn, ownership.c.user_id == user_id)).values(quantity=quantity)
    else:
        ownership_entry = ownership.insert().values(user_id=user_id, book_isbn=book.isbn, quantity=quantity)

    db.session.execute(ownership_entry)
    db.session.commit()

# Utility function to handle database errors
def handle_db_error(error_message):
    db.session.rollback()
    return jsonify({'error': error_message}), 400

# Route to create a new user
@routes_blueprint.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 400

    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
        return jsonify({'message': f'User created successfully. UserID: {new_user.id}'}), 201
    except SQLAlchemyError as e:
        return handle_db_error(str(e))

# Route to get all users
@routes_blueprint.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
    return jsonify(result), 200

# Route to get all books
@routes_blueprint.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    result = []
    for book in books:
        quantity = get_book_quantity(book)
        result.append({
            'isbn': book.isbn,
            'title': book.title,
            'author': book.author,
            'quantity_available': quantity,
        })
    return jsonify(result), 200

# Route to create a new book
@routes_blueprint.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    required_fields = ['isbn', 'title', 'author', 'owner_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    isbn = data['isbn']
    book = get_book_by_isbn(isbn)
    if not book:
        new_book = Book(title=data['title'], author=data['author'], isbn=isbn)
        db.session.add(new_book)
        db.session.commit()
        book = new_book

    user_id = data['owner_id']
    quantity = data.get('quantity', 1)
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    create_or_update_ownership(book, user_id, quantity)
    return jsonify({'message': 'Book created successfully'}), 201

# Route to update a book
@routes_blueprint.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    data = request.get_json()
    required_fields = ['title', 'author', 'owner_id', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    book.title = data['title']
    book.author = data['author']
    user_id = data['owner_id']
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    create_or_update_ownership(book, user_id, data['quantity'])
    return jsonify({'message': 'Book updated successfully'}), 200

# Route to delete a book
@routes_blueprint.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200

# Route to get all books of a user
@routes_blueprint.route('/users/<int:user_id>/books', methods=['GET'])
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

# Route to request for book exchange
@routes_blueprint.route('/books/<int:book_id>/exchange', methods=['POST'])
def exchange_book(book_id):
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    owners = ownership.select().where(and_(ownership.c.book_isbn == book_id, ownership.c.quantity > 0))
    res = db.session.execute(owners).all()
    if res:
        selected_owner = res[0]
        selected_owner_quantity = selected_owner.quantity
        ownership_entry = ownership.update().where(and_(ownership.c.book_isbn == book_id, ownership.c.user_id == selected_owner.user_id)).values(quantity=selected_owner_quantity - 1)
        db.session.execute(ownership_entry)
        db.session.commit()
        return jsonify({'message': 'Book exchanged successfully'}), 200
    else:
        waiting_list_entry = WaitingList(user_id=user_id, book_isbn=book_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
        return jsonify({'message': 'Book not available. Added to waiting list'}), 200

# Route to add books to reading list
@routes_blueprint.route('/users/<int:user_id>/books/read', methods=['POST'])
def add_to_reading_list(user_id):
    data = request.get_json()
    book_ids = data.get('book_ids', [])
    if not book_ids:
        return jsonify({'error': 'Book IDs are required'}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    for book_id in book_ids:
        reading_list_entry = WishList(user_id=user_id, book_isbn=book_id)
        db.session.add(reading_list_entry)
    db.session.commit()
    return jsonify({'message': 'Books added to reading list'}), 200

# Route to rate a book
@routes_blueprint.route('/books/rate', methods=['POST'])
def rate_book():
    data = request.get_json()
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    rating = data.get('rating')
    if not user_id or not book_id or rating is None:
        return jsonify({'error': 'Missing required fields'}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    rating_entry = BookRating(user_id=user_id, book_isbn=book_id, rating=rating)
    existing_rating = BookRating.query.filter_by(user_id=user_id, book_isbn=book_id).first()
    if existing_rating:
        existing_rating.rating = rating
    else:
        db.session.add(rating_entry)

    db.session.commit()
    return jsonify({'message': 'Book rated successfully'}), 200

# Route to get all ratings for a book
@routes_blueprint.route('/books/ratings/<string:book_id>', methods=['GET'])
def get_book_ratings(book_id):
    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    ratings = BookRating.query.filter_by(book_isbn=book_id).all()
    result = [{'user_id': rating.user_id, 'rating': rating.rating} for rating in ratings]
    return jsonify(result), 200

# Route to get average rating for a book
@routes_blueprint.route('/books/ratings/average/<string:book_id>', methods=['GET'])
def get_book_average_rating(book_id):
    book = get_book_by_isbn(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404

    ratings = BookRating.query.filter_by(book_isbn=book_id).all()
    if not ratings:
        return jsonify({'average_rating': 0}), 200

    avg_rating = sum([rating.rating for rating in ratings]) / len(ratings)
    return jsonify({'average_rating': avg_rating}), 200

# Route to get ratings given by a user
@routes_blueprint.route('/users/ratings/<int:user_id>', methods=['GET'])
def get_user_ratings(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    ratings = BookRating.query.filter_by(user_id=user_id).all()
    result = [{'book_id': rating.book_isbn, 'rating': rating.rating} for rating in ratings]
    return jsonify(result), 200
