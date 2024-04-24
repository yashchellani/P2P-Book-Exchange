import unittest
from flask import Flask, jsonify
from flask_testing import TestCase
from app.routes import books_blueprint
from models import db, User, Book, BookRating, ownership


class TestBooks(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.register_blueprint(books_blueprint)
        db.init_app(app)
        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_books(self):
        with self.app.app_context():
            book1 = Book(isbn="1234567890", title="Book 1", author="Author 1")
            book2 = Book(isbn="0987654321", title="Book 2", author="Author 2")
            db.session.add(book1)
            db.session.add(book2)
            db.session.commit()

            response = self.client.get("/books")
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["title"], "Book 1")
            self.assertEqual(data[1]["title"], "Book 2")

    def test_create_book(self):
        with self.app.app_context():
            user = User(username="test_user", email="test@example.com", password="test")
            db.session.add(user)
            db.session.commit()

            data = {
                "isbn": "1234567890",
                "title": "Test Book",
                "author": "Test Author",
                "owner_id": user.id,
            }

            response = self.client.post("/books", json=data)
            self.assertEqual(response.status_code, 201)

            book = Book.query.filter_by(isbn="1234567890").first()
            self.assertIsNotNone(book)
            self.assertEqual(book.title, "Test Book")

    def test_search_book(self):
        with self.app.app_context():
            book1 = Book(isbn="1234567890", title="Book 1", author="Author 1")
            book2 = Book(isbn="0987654321", title="Book 2", author="Author 2")
            db.session.add(book1)
            db.session.add(book2)
            db.session.commit()

            data = {"title": "Book 1"}
            response = self.client.post("/books/search", json=data)
            result = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["title"], "Book 1")

    def test_add_books(self):
        with self.app.app_context():
            user = User(username="test_user", email="test@example.com", password="test")
            db.session.add(user)
            db.session.commit()

            data = [
                {
                    "isbn": "1234567890",
                    "title": "Test Book 1",
                    "author": "Test Author 1",
                    "owner_id": user.id,
                },
                {
                    "isbn": "0987654321",
                    "title": "Test Book 2",
                    "author": "Test Author 2",
                    "owner_id": user.id,
                },
            ]

            response = self.client.post("/books/add", json=data)
            self.assertEqual(response.status_code, 200)

            book1 = Book.query.filter_by(isbn="1234567890").first()
            book2 = Book.query.filter_by(isbn="0987654321").first()

            self.assertIsNotNone(book1)
            self.assertIsNotNone(book2)
            self.assertEqual(book1.title, "Test Book 1")
            self.assertEqual(book2.title, "Test Book 2")

    def test_get_recommendations(self):
        with self.app.app_context():
            user = User(username="test_user", email="test@example.com", password="test")
            db.session.add(user)
            db.session.commit()

            book1 = Book(isbn="1234567890", title="Book 1", author="Author 1")
            book2 = Book(isbn="0987654321", title="Book 2", author="Author 2")
            db.session.add(book1)
            db.session.add(book2)
            db.session.commit()

            rating1 = BookRating(user_id=user.id, book_isbn="1234567890", rating=5)
            rating2 = BookRating(user_id=user.id, book_isbn="0987654321", rating=4)
            db.session.add(rating1)
            db.session.add(rating2)
            db.session.commit()

            data = {"user_id": user.id}
            response = self.client.post("/books/recommendations", json=data)
            result = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(result), 2)
            self.assertIn(
                {"isbn": "1234567890", "title": "Book 1", "author": "Author 1"}, result
            )
            self.assertIn(
                {"isbn": "0987654321", "title": "Book 2", "author": "Author 2"}, result
            )


if __name__ == "__main__":
    unittest.main()
