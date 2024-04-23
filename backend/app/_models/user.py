from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    waiting_list = db.relationship('WaitingList', backref='user', lazy='dynamic')
    wish_list = db.relationship('WishList', backref='user', lazy='dynamic')
    book_ratings = db.relationship('BookRating', backref='user', lazy='dynamic')
    user_ratings = db.relationship('UserRating', backref='rater', foreign_keys='UserRating.rater_id', lazy='dynamic')
    rated_by = db.relationship('UserRating', backref='ratee', foreign_keys='UserRating.ratee_id', lazy='dynamic')
    book_exchange = db.relationship('BookExchange', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

class UserRating(db.Model):
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    ratee_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<UserRating %r>' % self.id
    
ownership = db.Table('ownership', 
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                     db.Column('book_isbn', db.String(120), db.ForeignKey('book.isbn'), primary_key=True),
                     db.Column('quantity', db.Integer, nullable=False, default=1)
                     )
