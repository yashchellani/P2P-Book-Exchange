from models import db, User, Book, BookRating, ownership
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from flask import jsonify

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

# Utility function to search for available books
def search_book_by_keywords(**kwargs):
    result = []
    if "title" in kwargs:
        keyword = f"%{kwargs['title']}%"
        title_books = Book.query.filter(Book.title.ilike(keyword)).all()
        result.extend(title_books)

    if "author" in kwargs:
        keyword = f"%{kwargs['author']}%"
        author_books = Book.query.filter(Book.author.ilike(keyword)).all()
        result.extend(author_books)

    if "isbn" in kwargs:
        isbn_books = Book.query.filter_by(isbn=kwargs['ISBN']).all()
        result.extend(isbn_books)

    if not result:
        return jsonify({'error': 'Title, author, or ISBN is required'}), 400

    unique_books = {book.isbn: {'isbn': book.isbn, 'title': book.title, 'author': book.author} for book in result}.values()
    return jsonify(list(unique_books))