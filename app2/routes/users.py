from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app2 import db
from app2.models.user import User
from app2.utils.decorators import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def list_users():
    users = User.query.filter_by(deleted_at=None).all()
    return jsonify([{'id': u.id, 'name_util': u.name_util, 'role': u.role} for u in users]), 200


@users_bp.route('/users/<int:user_id>/role', methods=['PATCH'])
@jwt_required()
@admin_required
def update_user_role(user_id):
    user = User.query.filter_by(id=user_id, deleted_at=None).first_or_404()
    data = request.get_json()
    user.role = data.get('role')
    db.session.commit()
    return jsonify({'message': 'Role updated'}), 200
