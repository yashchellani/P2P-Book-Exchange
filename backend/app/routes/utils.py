from models import db, User, Book, BookRating, ownership
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from flask import jsonify


def get_book_quantity(book):
    """Utility function to get book quantity"""
    owners = ownership.select().where(ownership.c.book_isbn == book.isbn)
    res = db.session.execute(owners).all()
    return sum([row.quantity for row in res])


def get_user_by_id(user_id):
    """Utility function to get user by id"""
    return User.query.get(user_id)


def get_book_by_isbn(isbn):
    """Utility function to get book by isbn"""
    return Book.query.get(isbn)


def create_or_update_ownership(book, user_id, quantity):
    """Utility function to create or update book ownership"""
    current_quantity = ownership.select().where(
        and_(ownership.c.book_isbn == book.isbn, ownership.c.user_id == user_id)
    )
    res = db.session.execute(current_quantity).all()
    quantity += res[0].quantity if res else 0

    if res:
        ownership_entry = (
            ownership.update()
            .where(
                and_(ownership.c.book_isbn == book.isbn, ownership.c.user_id == user_id)
            )
            .values(quantity=quantity)
        )
    else:
        ownership_entry = ownership.insert().values(
            user_id=user_id, book_isbn=book.isbn, quantity=quantity
        )

    db.session.execute(ownership_entry)
    db.session.commit()


def handle_db_error(error_message):
    """Utility function to handle database errors"""
    db.session.rollback()
    return jsonify({"error": error_message}), 400


def search_book_by_keywords(**kwargs):
    """Utility function to search for available books by title, author, or ISBN"""
    result = []
    if "title" in kwargs and kwargs["title"]:
        keyword = f"%{kwargs['title']}%"
        title_books = Book.query.filter(Book.title.ilike(keyword)).all()
        result.extend(title_books)

    if "author" in kwargs and kwargs["author"]:
        keyword = f"%{kwargs['author']}%"
        author_books = Book.query.filter(Book.author.ilike(keyword)).all()
        result.extend(author_books)

    if "isbn" in kwargs and kwargs["isbn"]:
        isbn_books = Book.query.filter_by(isbn=kwargs["isbn"]).all()
        result.extend(isbn_books)

    if not result:
        return jsonify({"error": "Title, author, or ISBN is required"}), 400

    unique_books = {
        book.isbn: {"isbn": book.isbn, "title": book.title, "author": book.author}
        for book in result
    }.values()
    return jsonify(list(unique_books))
