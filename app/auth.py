from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from database import db, User
from utils import hash_password, verify_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(name_util=data['name_util'], deleted_at=None).first()
    if user and verify_password(data['password'], user.password):
        token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
        return jsonify({'token': token}), 200
    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/users', methods=['POST'])
def register():
    data = request.get_json()
    user = User(
        name_util=data['name_util'],
        password=hash_password(data['password']),
        role=data['role']
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'id': user.id, 'name_util': user.name_util, 'role': user.role}), 201
