# exchange.py
from flask import Blueprint, jsonify, request
from models import db, ownership, WaitingList
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_
from .utils import get_user_by_id
from sqlalchemy import and_

exchange_blueprint = Blueprint('exchange', __name__)

@exchange_blueprint.route('/books/<int:book_id>/exchange', methods=['POST'])
def exchange_book(book_id):
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    owners = ownership.select().where(and_(ownership.c.book_isbn == book_id, ownership.c.quantity > 0))
    owners = db.session.execute(owners).all()
    if owners:
        selected_owner = owners[0]
        new_quantity = selected_owner.quantity - 1
        db.session.execute(ownership.update().where(and_(ownership.c.book_isbn == book_id, ownership.c.user_id == selected_owner.user_id)).values(quantity=new_quantity))
        db.session.commit()
        return jsonify({'message': 'Book exchanged successfully'}), 200
    else:
        waiting_list_entry = WaitingList(user_id=user_id, book_isbn=book_id)
        db.session.add(waiting_list_entry)
        db.session.commit()
        return jsonify({'message': 'Book not available. Added to waiting list'}), 200
