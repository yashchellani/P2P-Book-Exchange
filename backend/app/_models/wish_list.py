from . import db

class WishList(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'), primary_key=True)

    def __repr__(self):
        return '<WishList %r>' % self.id
