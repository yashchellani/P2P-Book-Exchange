from flask import Blueprint, jsonify, request
from models import db, ownership, WaitingList, BookExchange, BookExchangeStatus
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from .utils import get_user_by_id
from sqlalchemy import and_

exchange_blueprint = Blueprint("exchange", __name__)

valid_exchange_statuses = [
    BookExchangeStatus.PENDING,
    BookExchangeStatus.COMPLETED,
    BookExchangeStatus.CANCELLED,
]


@exchange_blueprint.route("/books/<int:book_id>/exchange", methods=["POST"])
def exchange_book(book_id):
    data = request.json
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    owners = ownership.select().where(
        and_(ownership.c.book_isbn == book_id, ownership.c.quantity > 0)
    )
    owners = db.session.execute(owners).all()
    if owners:
        selected_owner = owners[0]
        new_quantity = selected_owner.quantity - 1
        db.session.execute(
            ownership.update()
            .where(
                and_(
                    ownership.c.book_isbn == book_id,
                    ownership.c.user_id == selected_owner.user_id,
                )
            )
            .values(quantity=new_quantity)
        )
        new_exchange = BookExchange(
            seller=selected_owner.user_id,
            buyer=user_id,
            status=BookExchangeStatus.PENDING,
            book_isbn=book_id,
        )
        db.session.add(new_exchange)
        db.session.commit()
        return jsonify({"message": "Book exchanged successfully"}), 200
    else:
        waiting_list_entry = WaitingList(user_id=user_id, book_isbn=book_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
        return jsonify({"message": "Book not available. Added to waiting list"}), 200


# mark exchange as completed
# in the future, this can also be extended to mark the exchange as cancelled
@exchange_blueprint.route("/books/<int:book_id>/exchange/<int:buyer>", methods=["PUT"])
def update_exchange_status(book_id, buyer):
    data = request.json
    status = data.get("status")
    if not status:
        return jsonify({"error": "Status is required"}), 400
    # get the exchange with buyer and book_id
    exchange = BookExchange.query.filter_by(buyer=buyer, book_isbn=book_id).first()
    if not exchange:
        return jsonify({"error": "Exchange not found"}), 404
    exchange.status = valid_exchange_statuses[int(status)]
    
    # check if the owner has the book
    owner = ownership.select().where(exchange.seller == ownership.c.user_id).where(book_id == ownership.c.book_isbn)
    owner = db.session.execute(owner).first()
    if owner.quantity < 1:
        delete = ownership.delete().where(exchange.seller == ownership.c.user_id).where(book_id == ownership.c.book_isbn)
        db.session.execute(delete)
    db.session.commit()
    return jsonify({"message": "Exchange status updated successfully"}), 200
