from . import db

class WaitingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_isbn = db.Column(db.String(120), db.ForeignKey('book.isbn'))

    def __repr__(self):
        return '<WaitingList %r>' % self.id
