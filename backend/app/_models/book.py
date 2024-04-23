from . import db
from enum import Enum
class BookExchangeStatus(Enum):
    PENDING = 1
    CANCELLED = 2
    COMPLETED = 3

class Book(db.Model):
    isbn = db.Column(db.String(120), primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    waiting_list = db.relationship('WaitingList', backref='book', lazy='dynamic')
    wish_list = db.relationship('WishList', backref='book', lazy='dynamic')
    book_ratings = db.relationship('BookRating', backref='book', lazy='dynamic')
    book_exchange = db.relationship('BookExchange', backref='book', lazy='dynamic')
    ownership = db.relationship('User', secondary='ownership', backref=db.backref('books', lazy='dynamic'))

    def __repr__(self):
        return '<Book %r>' % self.title


class BookExchange(db.Model):
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.Enum(BookExchangeStatus), nullable=False)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)

    def __repr__(self):
        return '<BookExchange %r>' % self.id

class BookRating(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<BookRating %r>' % self.id