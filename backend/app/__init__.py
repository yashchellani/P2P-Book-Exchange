from flask import Flask
from models import db, ownership
from routes import (
    users_blueprint,
    books_blueprint,
    ratings_blueprint,
    reading_lists_blueprint,
    exchange_blueprint,
)
from flask_cors import CORS, cross_origin


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["CORS_HEADERS"] = "Content-Type"

    # SQLite DB configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book_exchange.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(users_blueprint)
    app.register_blueprint(books_blueprint)
    app.register_blueprint(ratings_blueprint)
    app.register_blueprint(reading_lists_blueprint)
    app.register_blueprint(exchange_blueprint)

    return app
