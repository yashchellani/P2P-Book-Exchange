from flask import Blueprint
from .users import users_blueprint
from .books import books_blueprint
from .ratings import ratings_blueprint
from .reading_lists import reading_lists_blueprint
from .exchange import exchange_blueprint
from models import db

routes_blueprint = Blueprint("routes", __name__)


@routes_blueprint.before_app_request
def create_tables():
    db.create_all()


routes_blueprint.register_blueprint(users_blueprint)
routes_blueprint.register_blueprint(books_blueprint)
routes_blueprint.register_blueprint(ratings_blueprint)
routes_blueprint.register_blueprint(reading_lists_blueprint)
routes_blueprint.register_blueprint(exchange_blueprint)
