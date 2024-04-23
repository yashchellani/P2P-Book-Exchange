from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class BookExchangeStatus(Enum):
    PENDING = 1
    CANCELLED = 2
    COMPLETED = 3

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Book(db.Model):
    isbn = db.Column(db.String(120), nullable=False, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.title

class WaitingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'))
    user = db.relationship('User', backref=db.backref('waiting_list', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('waiting_list', lazy='dynamic'))

    def __repr__(self):
        return '<WaitingList %r>' % self.id

class WishList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)
    user = db.relationship('User', backref=db.backref('wish_list', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('wish_list', lazy='dynamic'))
    def __repr__(self):
        return '<ReadingList %r>' % self.id

class BookRating(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('rating', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('rating', lazy='dynamic'))

    def __repr__(self):
        return '<BookRating %r>' % self.id

class UserRating(db.Model):
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    rater = db.relationship('User', foreign_keys=[rater_id], backref=db.backref('rater_ratings', lazy='dynamic'))
    ratee = db.relationship('User', foreign_keys=[ratee_id], backref=db.backref('ratee_ratings', lazy='dynamic'))

    def __repr__(self):
        return '<UserRating %r>' % self.id

class BookExchange(db.Model):
    seller = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    buyer = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.Enum(BookExchangeStatus), nullable=False)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)
    user = db.relationship('User', foreign_keys=[seller], backref=db.backref('book_seller', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('book_exchange', lazy='dynamic'))

    def __repr__(self):
        return '<BookExchange %r>' % self.id
    

#intermediate table for many-to-many relationship between User and Book
ownership = db.Table('ownership', 
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('book_isbn', db.Integer, db.ForeignKey('book.isbn'), primary_key=True),
                     db.Column('quantity', db.Integer, nullable=False, default=1),
                     )
